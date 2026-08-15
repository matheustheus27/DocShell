#!/usr/bin/env python3
"""
DocShell Core - Hybrid Database Engine (MongoDB with Persistent SQLite Fallback)
Provides schema-flexible, containerized document & telemetry storage:
- Base documents registry and metadata
- Translated document cache and status tracking
- Translation worker job queue state
- Detailed structured audit logs and telemetry for Datadog cross-referencing
"""

import os
import sys
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("docshell-db")

def _resolve_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent

ROOT_DIR = _resolve_root()

# Persistent Fallback DB Directory (outside dist/ so it is never deleted by task site or task clean)
FALLBACK_DB_DIR = ROOT_DIR / "publication" / "data"
FALLBACK_DB_PATH = FALLBACK_DB_DIR / "docshell.db"

MONGO_HOST = os.getenv("MONGO_HOST", os.getenv("DB_HOST", "mongo" if Path("/app").exists() else "localhost"))
MONGO_PORT = int(os.getenv("MONGO_PORT", os.getenv("DB_PORT", "27017")))
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "docshell")
MONGO_URI = os.getenv("MONGO_URI", f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}")


class DatabaseManager:
    """
    Unified Database Manager supporting MongoDB in Docker with seamless
    fallback to persistent SQLite outside Docker.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or FALLBACK_DB_PATH
        self._mongo_client = None
        self._mongo_db = None
        self.engine = "sqlite"

        self._init_mongo()
        if self._mongo_db is None:
            self._ensure_sqlite_dir()
            self._init_sqlite_schema()

    def _init_mongo(self):
        """Attempts connection to MongoDB container."""
        try:
            from pymongo import MongoClient
            client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
                socketTimeoutMS=2000
            )
            # Ping database to verify connection
            client.admin.command('ping')
            self._mongo_client = client
            self._mongo_db = client[MONGO_DB_NAME]
            self.engine = "mongodb"
            self._init_mongo_indexes()
            logger.info(f"Connected to MongoDB at {MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}")
        except Exception as e:
            self._mongo_client = None
            self._mongo_db = None
            self.engine = "sqlite"
            logger.debug(f"MongoDB not available ({e}), using persistent SQLite fallback: {self.db_path}")

    def _init_mongo_indexes(self):
        """Ensures high-performance unique indexes on MongoDB collections."""
        try:
            self._mongo_db.documents.create_index("slug", unique=True)
            self._mongo_db.translations.create_index([("locale", 1), ("slug", 1)], unique=True)
            self._mongo_db.translation_jobs.create_index("job_id", unique=True)
            self._mongo_db.translation_jobs.create_index([("target_locale", 1), ("created_at", -1)])
            self._mongo_db.audit_logs.create_index([("timestamp", -1)])
            self._mongo_db.audit_logs.create_index("service")
            self._mongo_db.audit_logs.create_index("event")
        except Exception as e:
            logger.warning(f"Failed to create Mongo indexes: {e}")

    # =========================================================================
    # SQLite Fallback Layer
    # =========================================================================
    def _ensure_sqlite_dir(self):
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def _get_sqlite_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_sqlite_schema(self):
        with self._get_sqlite_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    slug TEXT PRIMARY KEY,
                    section TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    html_body TEXT NOT NULL,
                    relative_path TEXT,
                    updated_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS translations (
                    locale TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    section TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    html_body TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'completed',
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (locale, slug)
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS translation_jobs (
                    job_id TEXT PRIMARY KEY,
                    target_locale TEXT NOT NULL,
                    status TEXT NOT NULL,
                    total_docs INTEGER DEFAULT 0,
                    completed_docs INTEGER DEFAULT 0,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    service TEXT NOT NULL,
                    event TEXT NOT NULL,
                    level TEXT NOT NULL,
                    duration_ms REAL,
                    status_code INTEGER,
                    details TEXT,
                    dd_trace_id TEXT,
                    dd_span_id TEXT
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trans_locale ON translations(locale);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_service ON audit_logs(service);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_event ON audit_logs(event);")

    # =========================================================================
    # Document Operations
    # =========================================================================
    def upsert_document(self, doc: Dict[str, Any]):
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "slug": doc["slug"],
            "section": doc.get("section", "General"),
            "title": doc.get("title", ""),
            "body": doc.get("body", ""),
            "html_body": doc.get("html_body", ""),
            "relative_path": doc.get("relative_path", ""),
            "updated_at": now
        }
        if self._mongo_db is not None:
            try:
                self._mongo_db.documents.update_one(
                    {"slug": doc["slug"]},
                    {"$set": payload},
                    upsert=True
                )
                return
            except Exception as e:
                logger.warning(f"Mongo upsert_document failed: {e}")

        # SQLite Fallback
        with self._get_sqlite_connection() as conn:
            conn.execute("""
                INSERT INTO documents (slug, section, title, body, html_body, relative_path, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    section = excluded.section,
                    title = excluded.title,
                    body = excluded.body,
                    html_body = excluded.html_body,
                    relative_path = excluded.relative_path,
                    updated_at = excluded.updated_at;
            """, (
                payload["slug"], payload["section"], payload["title"],
                payload["body"], payload["html_body"],
                payload["relative_path"], now
            ))

    def get_all_documents(self) -> List[Dict[str, Any]]:
        if self._mongo_db is not None:
            try:
                docs = list(self._mongo_db.documents.find({}, {"_id": 0}))
                if docs:
                    return docs
            except Exception as e:
                logger.warning(f"Mongo get_all_documents failed: {e}")

        # SQLite Fallback
        with self._get_sqlite_connection() as conn:
            cursor = conn.execute("SELECT slug, section, title, body, html_body, relative_path, updated_at FROM documents;")
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # Translation Operations
    # =========================================================================
    def upsert_translation(self, locale: str, doc: Dict[str, Any], status: str = "completed"):
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "locale": locale,
            "slug": doc["slug"],
            "section": doc.get("section", "General"),
            "title": doc.get("title", ""),
            "body": doc.get("body", ""),
            "html_body": doc.get("html_body", ""),
            "status": status,
            "updated_at": now
        }
        if self._mongo_db is not None:
            try:
                self._mongo_db.translations.update_one(
                    {"locale": locale, "slug": doc["slug"]},
                    {"$set": payload},
                    upsert=True
                )
                return
            except Exception as e:
                logger.warning(f"Mongo upsert_translation failed: {e}")

        # SQLite Fallback
        with self._get_sqlite_connection() as conn:
            conn.execute("""
                INSERT INTO translations (locale, slug, section, title, body, html_body, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(locale, slug) DO UPDATE SET
                    section = excluded.section,
                    title = excluded.title,
                    body = excluded.body,
                    html_body = excluded.html_body,
                    status = excluded.status,
                    updated_at = excluded.updated_at;
            """, (
                locale, payload["slug"], payload["section"], payload["title"],
                payload["body"], payload["html_body"], status, now
            ))

    def get_translations_for_locale(self, locale: str) -> List[Dict[str, Any]]:
        if self._mongo_db is not None:
            try:
                docs = list(self._mongo_db.translations.find({"locale": locale, "status": "completed"}, {"_id": 0}))
                return docs
            except Exception as e:
                logger.warning(f"Mongo get_translations_for_locale failed: {e}")

        # SQLite Fallback
        with self._get_sqlite_connection() as conn:
            cursor = conn.execute("""
                SELECT locale, slug, section, title, body, html_body, status, updated_at
                FROM translations WHERE locale = ? AND status = 'completed';
            """, (locale,))
            return [dict(row) for row in cursor.fetchall()]

    def has_full_translation(self, locale: str, expected_count: int) -> bool:
        if self._mongo_db is not None:
            try:
                count = self._mongo_db.translations.count_documents({"locale": locale, "status": "completed"})
                return count >= expected_count
            except Exception:
                pass

        # SQLite Fallback
        with self._get_sqlite_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as cnt FROM translations WHERE locale = ? AND status = 'completed';
            """, (locale,))
            row = cursor.fetchone()
            return row["cnt"] >= expected_count if row else False

    # =========================================================================
    # Job Queue Operations
    # =========================================================================
    def create_or_update_job(
        self,
        job_id: str,
        target_locale: str,
        status: str,
        total_docs: int = 0,
        completed_docs: int = 0,
        error_message: Optional[str] = None
    ):
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "job_id": job_id,
            "target_locale": target_locale,
            "status": status,
            "total_docs": total_docs,
            "completed_docs": completed_docs,
            "error_message": error_message,
            "updated_at": now
        }
        if self._mongo_db is not None:
            try:
                self._mongo_db.translation_jobs.update_one(
                    {"job_id": job_id},
                    {"$set": payload, "$setOnInsert": {"created_at": now}},
                    upsert=True
                )
                return
            except Exception as e:
                logger.warning(f"Mongo create_or_update_job failed: {e}")

        # SQLite Fallback
        with self._get_sqlite_connection() as conn:
            conn.execute("""
                INSERT INTO translation_jobs (job_id, target_locale, status, total_docs, completed_docs, error_message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    status = excluded.status,
                    completed_docs = excluded.completed_docs,
                    total_docs = excluded.total_docs,
                    error_message = excluded.error_message,
                    updated_at = excluded.updated_at;
            """, (job_id, target_locale, status, total_docs, completed_docs, error_message, now, now))

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        if self._mongo_db is not None:
            try:
                job = self._mongo_db.translation_jobs.find_one({"job_id": job_id}, {"_id": 0})
                if job:
                    return job
            except Exception:
                pass

        with self._get_sqlite_connection() as conn:
            cursor = conn.execute("SELECT * FROM translation_jobs WHERE job_id = ?;", (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_latest_job_for_locale(self, locale: str) -> Optional[Dict[str, Any]]:
        if self._mongo_db is not None:
            try:
                job = self._mongo_db.translation_jobs.find_one(
                    {"target_locale": locale},
                    sort=[("created_at", -1)],
                    projection={"_id": 0}
                )
                if job:
                    return job
            except Exception:
                pass

        with self._get_sqlite_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM translation_jobs WHERE target_locale = ? ORDER BY created_at DESC LIMIT 1;
            """, (locale,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # =========================================================================
    # Audit Logging Operations
    # =========================================================================
    def log_audit_event(
        self,
        service: str,
        event: str,
        level: str = "INFO",
        duration_ms: Optional[float] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        dd_trace_id: Optional[str] = None,
        dd_span_id: Optional[str] = None
    ):
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "timestamp": now,
            "service": service,
            "event": event,
            "level": level,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "details": details or {},
            "dd_trace_id": dd_trace_id,
            "dd_span_id": dd_span_id
        }
        if self._mongo_db is not None:
            try:
                self._mongo_db.audit_logs.insert_one(payload)
                return
            except Exception:
                pass

        # SQLite Fallback
        details_json = json.dumps(details or {}, ensure_ascii=False)
        try:
            with self._get_sqlite_connection() as conn:
                conn.execute("""
                    INSERT INTO audit_logs (timestamp, service, event, level, duration_ms, status_code, details, dd_trace_id, dd_span_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (now, service, event, level, duration_ms, status_code, details_json, dd_trace_id, dd_span_id))
        except Exception:
            pass

    def get_audit_summary(self, limit: int = 100) -> Dict[str, Any]:
        if self._mongo_db is not None:
            try:
                total = self._mongo_db.audit_logs.count_documents({})
                errors = self._mongo_db.audit_logs.count_documents({"level": "ERROR"})
                recent = list(self._mongo_db.audit_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
                pipeline = [
                    {"$group": {"_id": "$event", "count": {"$sum": 1}, "avg_duration": {"$avg": "$duration_ms"}}}
                ]
                events_agg = [
                    {"event": r["_id"], "count": r["count"], "avg_duration": r.get("avg_duration") or 0.0}
                    for r in self._mongo_db.audit_logs.aggregate(pipeline)
                ]
                return {
                    "engine": "mongodb",
                    "total_events": total,
                    "error_events": errors,
                    "event_aggregations": events_agg,
                    "recent_logs": recent
                }
            except Exception as e:
                logger.warning(f"Mongo get_audit_summary failed: {e}")

        # SQLite Fallback
        with self._get_sqlite_connection() as conn:
            total_logs = conn.execute("SELECT COUNT(*) as cnt FROM audit_logs;").fetchone()["cnt"]
            error_logs = conn.execute("SELECT COUNT(*) as cnt FROM audit_logs WHERE level = 'ERROR';").fetchone()["cnt"]
            recent_logs = [
                dict(row) for row in conn.execute(
                    "SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?;", (limit,)
                ).fetchall()
            ]
            events_agg = [
                dict(row) for row in conn.execute(
                    "SELECT event, COUNT(*) as count, AVG(duration_ms) as avg_duration FROM audit_logs GROUP BY event;"
                ).fetchall()
            ]
            return {
                "engine": "sqlite",
                "total_events": total_logs,
                "error_events": error_logs,
                "event_aggregations": events_agg,
                "recent_logs": recent_logs
            }


# Singleton database instance
db = DatabaseManager()
