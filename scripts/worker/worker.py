#!/usr/bin/env python3
"""
DocShell - Dedicated Translation Task Worker & RabbitMQ Orchestrator
Features:
- RabbitMQ AMQP message broker integration with Dead Letter Queue (DLQ)
- Resilient polling fallback to SQLite job queue if RabbitMQ is offline
- Strict Task Deadline enforcement (180s timeout)
- Maximum 3 Retries with exponential backoff
- Datadog tracing & SQLite audit logging
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Resolve root
_parents = Path(__file__).resolve().parents
if len(_parents) > 2 and (_parents[2] / "docs").exists():
    ROOT_DIR = _parents[2]
elif len(_parents) > 0 and (_parents[0] / "scripts").exists():
    ROOT_DIR = _parents[0]
elif Path("/app").exists():
    ROOT_DIR = Path("/app")
else:
    ROOT_DIR = Path.cwd()

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.core.logger import get_logger, log_event, MeasureTime
from scripts.core.database import db
from scripts.core.cache_manager import cache_manager
from scripts.core.translator import normalize_locale, translate_section, sanitize_translation_output
from scripts.core.doc_parser import parse_markdown_to_html
from scripts.rag.services.ollama_service import generate_text, OLLAMA_TRANSLATE_MODEL, OLLAMA_MODEL

logger = get_logger("docshell-worker")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
QUEUE_NAME = "docshell_translation_tasks"
DLQ_NAME = "docshell_translation_dlq"

MAX_RETRIES = 3
TASK_DEADLINE_SECONDS = 180.0


async def translate_single_document(doc: Dict[str, Any], target_locale: str) -> Dict[str, Any]:
    """Translates a single document using TranslateGemma with Redis cache."""
    slug = doc["slug"]
    raw_body = doc.get("body", "") or doc.get("html_body", "")
    trans_section = translate_section(doc.get("section", "General"), target_locale)

    from scripts.rag.services.translation_worker import translate_text
    trans_title = await translate_text(doc.get("title", ""), target_locale, source_locale="pt-BR")
    trans_body = await translate_text(raw_body, target_locale, source_locale="pt-BR")

    trans_title = sanitize_translation_output(trans_title, doc.get("title", ""))
    trans_body = sanitize_translation_output(trans_body, raw_body)

    return {
        "slug": slug,
        "section": trans_section,
        "title": trans_title,
        "body": trans_body,
        "html_body": parse_markdown_to_html(trans_body),
        "locale": target_locale
    }


async def process_translation_job(job_data: Dict[str, Any]) -> bool:
    """
    Executes a translation job with deadline and retry tracking.
    """
    job_id = job_data.get("job_id")
    target_locale = normalize_locale(job_data.get("target_locale", "en-US"))
    attempt = job_data.get("attempt", 1)

    logger.info(f"[Worker] Processing job '{job_id}' for locale '{target_locale}' (Attempt {attempt}/{MAX_RETRIES})...")
    start_time = time.perf_counter()

    from scripts.rag.routers.docs import load_base_docs
    base_docs = load_base_docs()
    total_docs = len(base_docs)

    db.create_or_update_job(job_id, target_locale, "processing", total_docs=total_docs, completed_docs=0)

    try:
        completed = 0
        for doc in base_docs:
            # Check Deadline
            elapsed = time.perf_counter() - start_time
            if elapsed > TASK_DEADLINE_SECONDS:
                raise TimeoutError(f"Task exceeded deadline of {TASK_DEADLINE_SECONDS}s (elapsed: {round(elapsed, 1)}s)")

            slug = doc["slug"]
            cached = cache_manager.get_doc(target_locale, slug)
            if not cached:
                translated_doc = await translate_single_document(doc, target_locale)
                db.upsert_translation(target_locale, translated_doc, status="completed")
                cache_manager.set_doc(target_locale, slug, translated_doc)
            else:
                db.upsert_translation(target_locale, cached, status="completed")

            completed += 1
            db.create_or_update_job(job_id, target_locale, "processing", total_docs=total_docs, completed_docs=completed)

        duration = round((time.perf_counter() - start_time) * 1000, 2)
        db.create_or_update_job(job_id, target_locale, "completed", total_docs=total_docs, completed_docs=completed)
        log_event("worker_translation_completed", details={"job_id": job_id, "locale": target_locale, "attempt": attempt}, duration_ms=duration)
        logger.info(f"[Worker] Successfully completed job '{job_id}' in {duration}ms.")
        return True

    except Exception as err:
        logger.error(f"[Worker] Job '{job_id}' failed on attempt {attempt}: {err}")
        if attempt < MAX_RETRIES:
            backoff_delay = 2 ** attempt
            logger.info(f"[Worker] Scheduling retry {attempt + 1}/{MAX_RETRIES} in {backoff_delay}s...")
            await asyncio.sleep(backoff_delay)
            job_data["attempt"] = attempt + 1
            return await process_translation_job(job_data)
        else:
            db.create_or_update_job(job_id, target_locale, "failed", error_message=f"Max retries reached: {err}")
            log_event("worker_translation_dead_letter", level="ERROR", details={"job_id": job_id, "locale": target_locale, "error": str(err)})
            return False


class RabbitMQWorker:
    """Consumes tasks from RabbitMQ queue with DLQ and deadline management."""
    def __init__(self):
        self.pika = None
        try:
            import pika
            self.pika = pika
        except ImportError:
            pass

    def run_blocking(self):
        if not self.pika:
            logger.info("[RabbitMQWorker] Pika not installed. Running in SQLite queue polling mode.")
            asyncio.run(self._run_sqlite_polling())
            return

        while True:
            try:
                logger.info(f"[RabbitMQWorker] Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}...")
                credentials = self.pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
                params = self.pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                connection = self.pika.BlockingConnection(params)
                channel = connection.channel()

                # Declare Queues & DLQ
                channel.queue_declare(queue=DLQ_NAME, durable=True)
                channel.queue_declare(
                    queue=QUEUE_NAME,
                    durable=True,
                    arguments={
                        "x-dead-letter-exchange": "",
                        "x-dead-letter-routing-key": DLQ_NAME
                    }
                )
                channel.basic_qos(prefetch_count=1)

                logger.info(f"[RabbitMQWorker] Subscribed to queue '{QUEUE_NAME}'. Waiting for translation messages...")

                for method_frame, properties, body in channel.consume(QUEUE_NAME):
                    try:
                        job_data = json.loads(body.decode("utf-8"))
                        success = asyncio.run(process_translation_job(job_data))
                        if success:
                            channel.basic_ack(method_frame.delivery_tag)
                        else:
                            channel.basic_nack(method_frame.delivery_tag, requeue=False)
                    except Exception as msg_err:
                        logger.error(f"[RabbitMQWorker] Message processing error: {msg_err}")
                        channel.basic_nack(method_frame.delivery_tag, requeue=False)

            except Exception as conn_err:
                logger.warning(f"[RabbitMQWorker] RabbitMQ connection failed ({conn_err}). Falling back to SQLite polling...")
                asyncio.run(self._run_sqlite_polling(single_pass=True))
                time.sleep(5)

    async def _run_sqlite_polling(self, single_pass: bool = False):
        """Fallback polling worker consuming pending jobs from SQLite."""
        while True:
            try:
                with db._get_connection() as conn:
                    cursor = conn.execute(
                        "SELECT * FROM translation_jobs WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1;"
                    )
                    row = cursor.fetchone()
                    if row:
                        job_data = dict(row)
                        await process_translation_job(job_data)
            except Exception as poll_err:
                logger.error(f"[SQLitePolling] Error: {poll_err}")

            if single_pass:
                break
            await asyncio.sleep(3)


def main():
    logger.info("=================================================================")
    logger.info("       DOCSHELL - DEDICATED TRANSLATION WORKER (RABBITMQ)        ")
    logger.info(f"   Broker: {RABBITMQ_HOST}:{RABBITMQ_PORT} | Queue: {QUEUE_NAME}")
    logger.info(f"   Max Retries: {MAX_RETRIES} | Deadline: {TASK_DEADLINE_SECONDS}s")
    logger.info("=================================================================")
    worker = RabbitMQWorker()
    worker.run_blocking()


if __name__ == "__main__":
    main()
