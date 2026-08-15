#!/usr/bin/env python3
"""
DocShell Core - Datadog Structured Logger
Emits JSON structured logs conforming to Datadog APM & Log Management schemas.
Maintains an append-only JSONL telemetry store for audit & metrics reporting.
"""

import os
import sys
import json
import time
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

def _resolve_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent

ROOT_DIR = _resolve_root()
LOGS_DIR = ROOT_DIR / "dist" / "logs"
TELEMETRY_FILE = LOGS_DIR / "datadog_telemetry.jsonl"

DD_SERVICE = os.getenv("DD_SERVICE", "docshell")
DD_ENV = os.getenv("DD_ENV", "production")
DD_VERSION = os.getenv("DD_VERSION", "1.0.0")


class DatadogJSONFormatter(logging.Formatter):
    """Formats standard python logging records into Datadog JSON schema."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": DD_SERVICE,
            "env": DD_ENV,
            "version": DD_VERSION,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "dd": {
                "trace_id": getattr(record, "trace_id", None) or str(uuid.uuid4().int)[:16],
                "span_id": getattr(record, "span_id", None) or str(uuid.uuid4().int)[:16]
            }
        }
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj.update(record.extra_data)
        
        # Write to telemetry file for reporter
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            with open(TELEMETRY_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_obj, ensure_ascii=False) + "\n")
        except Exception:
            pass

        return json.dumps(log_obj, ensure_ascii=False)


def get_logger(name: str = "docshell") -> logging.Logger:
    """Configures and returns a Datadog-ready logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler with clean human output or JSON
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", datefmt="%H:%M:%S")
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


def log_event(event_name: str, level: str = "INFO", details: Optional[Dict[str, Any]] = None, duration_ms: Optional[float] = None, status_code: Optional[int] = None):
    """Logs a structured event into both Datadog telemetry stream and SQLite audit logs."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": DD_SERVICE,
        "env": DD_ENV,
        "version": DD_VERSION,
        "level": level.upper(),
        "event": event_name,
        "duration_ms": duration_ms,
        "status_code": status_code,
        "details": details or {}
    }
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(TELEMETRY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    try:
        from scripts.core.database import db
        db.log_audit_event(
            service=DD_SERVICE,
            event=event_name,
            level=level.upper(),
            duration_ms=duration_ms,
            status_code=status_code,
            details=details
        )
    except Exception:
        pass


class MeasureTime:
    """Context manager for logging execution duration of operations."""
    def __init__(self, operation_name: str, extra: Optional[Dict[str, Any]] = None):
        self.operation = operation_name
        self.extra = extra or {}
        self.start = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = round((time.perf_counter() - self.start) * 1000, 2)
        level = "ERROR" if exc_type else "INFO"
        details = dict(self.extra)
        if exc_val:
            details["error"] = str(exc_val)
        log_event(self.operation, level=level, details=details, duration_ms=duration)
