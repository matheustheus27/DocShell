#!/usr/bin/env python3
"""
DocShell Backend - Translation Task Queue & Worker Service
Manages asynchronous background translation using TranslateGemma, RabbitMQ messaging,
SQLite persistence and Redis caching.
"""

import os
import json
import time
import hashlib
import asyncio
from typing import Dict, Any, Optional

from scripts.core.logger import get_logger, log_event
from scripts.core.database import db
from scripts.core.cache_manager import cache_manager
from scripts.core.translator import (
    normalize_locale, translate_section, sanitize_translation_output
)
from scripts.core.doc_parser import parse_markdown_to_html
from scripts.rag.services.ollama_service import (
    generate_text, OLLAMA_TRANSLATE_MODEL, OLLAMA_MODEL
)

logger = get_logger("docshell-translation-worker")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
QUEUE_NAME = "docshell_translation_tasks"


def publish_to_rabbitmq(job_data: Dict[str, Any]) -> bool:
    """Publishes translation task to RabbitMQ queue."""
    try:
        import pika
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            connection_attempts=1,
            retry_delay=1,
            socket_timeout=2
        )
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(job_data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        logger.info(f"[RabbitMQ] Successfully published job '{job_data.get('job_id')}' to queue.")
        return True
    except Exception as e:
        logger.debug(f"[RabbitMQ] Publish skipped (broker offline or not in docker): {e}")
        return False


import re

def split_markdown_into_blocks(text: str, max_chars: int = 1200) -> list:
    """Splits markdown into logical blocks by headers or paragraphs without breaking tables or code."""
    if len(text) <= max_chars:
        return [text]
    
    sections = re.split(r'(?=\n#{1,4}\s)', text)
    blocks = []
    current = ""
    for sec in sections:
        if len(current) + len(sec) < max_chars:
            current += sec
        else:
            if current:
                blocks.append(current.strip())
            if len(sec) > max_chars:
                paras = sec.split('\n\n')
                sub_curr = ""
                for p in paras:
                    if len(sub_curr) + len(p) + 2 < max_chars:
                        sub_curr = (sub_curr + "\n\n" + p).strip()
                    else:
                        if sub_curr:
                            blocks.append(sub_curr.strip())
                        sub_curr = p.strip()
                if sub_curr:
                    blocks.append(sub_curr.strip())
                current = ""
            else:
                current = sec
    if current:
        blocks.append(current.strip())
    return [b for b in blocks if b]


async def _translate_single_block(clean_text: str, target_locale: str, source_locale: str = "pt-BR") -> str:
    """Translates an individual block of text."""
    if not clean_text or target_locale == source_locale:
        return clean_text

    text_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()[:16]
    cached = cache_manager.get_translation(source_locale, target_locale, text_hash)
    if cached and not cache_manager._is_poisoned_text(cached):
        return cached

    prompt = (
        f"Translate the following technical documentation Markdown text from {source_locale} into {target_locale}.\n"
        f"Rules: Preserve all Markdown formatting (#, ##), bullet lists, bold, tables, HTML tags, anchor IDs, image paths, and code blocks untouched.\n"
        f"Output ONLY the translated Markdown text without preamble, instructions, or notes.\n\n"
        f"--- START TEXT ---\n{clean_text}\n--- END TEXT ---"
    )

    try:
        translated = await generate_text(
            prompt=prompt,
            preferred_model=OLLAMA_TRANSLATE_MODEL,
            fallback_models=[OLLAMA_MODEL, "llama3.2", "translategemma", "gemma2", "mistral"],
            temperature=0.2,
            timeout=60.0
        )
        if translated and translated.strip():
            translated_clean = sanitize_translation_output(translated.strip(), clean_text)
            if not cache_manager._is_poisoned_text(translated_clean):
                cache_manager.set_translation(source_locale, target_locale, text_hash, translated_clean)
                return translated_clean
    except Exception as e:
        logger.warning(f"Error calling Ollama Translate for text block: {e}")

    return clean_text


async def translate_text(text: str, target_locale: str, source_locale: str = "pt-BR") -> str:
    """Translates Markdown content completely using TranslateGemma with chunked block processing."""
    clean_text = (text or "").strip()
    if not clean_text or target_locale == source_locale:
        return text

    # Short section translation dictionary lookup
    from scripts.core.translator import SECTION_DICTIONARY
    if len(clean_text) < 30 and clean_text.lower() in SECTION_DICTIONARY.get("pt-BR", {}):
        return translate_section(clean_text, target_locale)

    text_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()[:16]
    cached = cache_manager.get_translation(source_locale, target_locale, text_hash)
    if cached and not cache_manager._is_poisoned_text(cached):
        return cached

    blocks = split_markdown_into_blocks(clean_text, max_chars=1200)
    if len(blocks) == 1:
        translated_result = await _translate_single_block(blocks[0], target_locale, source_locale)
    else:
        translated_blocks = []
        for b in blocks:
            tb = await _translate_single_block(b, target_locale, source_locale)
            translated_blocks.append(tb)
        translated_result = "\n\n".join(translated_blocks)

    if translated_result:
        cache_manager.set_translation(source_locale, target_locale, text_hash, translated_result)
        return translated_result

    return text


class TranslationQueueWorker:
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None

    def start(self):
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._process_queue())

    async def enqueue_job(self, target_locale: str, base_docs: list) -> str:
        norm = normalize_locale(target_locale)
        job_id = f"job_trans_{norm}_{int(time.time())}"
        
        # Check if already processing
        existing_job = db.get_latest_job_for_locale(norm)
        if existing_job and existing_job["status"] == "processing":
            return existing_job["job_id"]

        db.create_or_update_job(job_id, norm, "pending", total_docs=len(base_docs), completed_docs=0)
        
        job_payload = {
            "job_id": job_id,
            "target_locale": norm,
            "attempt": 1
        }

        # Try dispatching to RabbitMQ
        published = publish_to_rabbitmq(job_payload)
        if not published:
            # Fallback to local async queue
            await self.queue.put((job_id, norm, base_docs))

        return job_id

    async def enqueue_locale(self, target_locale: str, base_docs: list) -> str:
        """Alias for enqueue_job."""
        return await self.enqueue_job(target_locale, base_docs)

    async def _process_queue(self):
        logger.info("[TranslationWorker] Background local translation queue active.")
        while True:
            try:
                job_id, norm_locale, base_docs = await self.queue.get()
                db.create_or_update_job(job_id, norm_locale, "processing", total_docs=len(base_docs), completed_docs=0)
                logger.info(f"[TranslationWorker] Starting translation for locale '{norm_locale}' ({len(base_docs)} documents)...")

                completed = 0
                for d in base_docs:
                    slug = d["slug"]
                    cached = cache_manager.get_doc(norm_locale, slug)
                    if not cached:
                        translated_doc = await self._translate_single_doc(d, norm_locale)
                        db.upsert_translation(norm_locale, translated_doc, status="completed")
                        cache_manager.set_doc(norm_locale, slug, translated_doc)
                    else:
                        db.upsert_translation(norm_locale, cached, status="completed")

                    completed += 1
                    db.create_or_update_job(job_id, norm_locale, "processing", total_docs=len(base_docs), completed_docs=completed)

                db.create_or_update_job(job_id, norm_locale, "completed", total_docs=len(base_docs), completed_docs=completed)
                log_event("async_translation_completed", details={"locale": norm_locale, "job_id": job_id, "docs_count": completed})
                logger.info(f"[TranslationWorker] Successfully finished translating '{norm_locale}'.")
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[TranslationWorker] Translation worker error: {e}", exc_info=True)
                if 'job_id' in locals():
                    db.create_or_update_job(job_id, norm_locale, "failed", error_message=str(e))
                self.queue.task_done()

    async def _translate_single_doc(self, doc: Dict[str, Any], target_locale: str) -> Dict[str, Any]:
        slug = doc["slug"]
        raw_body = doc.get("body", "") or doc.get("html_body", "")
        trans_section = translate_section(doc.get("section", "General"), target_locale)

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


trans_worker = TranslationQueueWorker()
