#!/usr/bin/env python3
"""
DocShell Backend - Telemetry, Healthcheck & Datadog Audit Router
"""

from fastapi import APIRouter
from scripts.core.database import db
from scripts.rag.services.rag_service import CHUNKS, EMBEDDINGS

router = APIRouter(tags=["Telemetry"])


@router.get("/healthz")
async def healthz():
    """Service healthcheck endpoint."""
    return {
        "status": "healthy",
        "service": "docshell-backend",
        "database": db.engine,
        "cache": "redis",
        "chunks_indexed": len(CHUNKS),
        "embeddings_ready": EMBEDDINGS is not None
    }


@router.get("/api/telemetry/report")
async def telemetry_report():
    """Generates and returns Datadog, Container, and Database cross-referenced audit report."""
    from scripts.core.datadog_reporter import generate_report, load_telemetry_entries
    entries = load_telemetry_entries()
    rep = generate_report(entries)
    rep["db_audit"] = db.get_audit_summary()
    return rep
