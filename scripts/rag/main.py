#!/usr/bin/env python3
"""
DocShell Backend - Main FastAPI Application Entrypoint
Integrates modular routers, SQLite database, async translation queue, and Datadog APM tracing.
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Resolve project paths
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
from scripts.rag.services.rag_service import init_rag_service
from scripts.rag.services.translation_worker import trans_worker
from scripts.rag.routers.docs import load_base_docs
from scripts.rag.routers import (
    chat_router,
    ws_chat_router,
    docs_router,
    translations_router,
    telemetry_router,
)

logger = get_logger("docshell-backend")

SITE_ROOT = Path(os.getenv("SITE_ROOT", "/site"))
RAG_CACHE_DIR = Path(os.getenv("RAG_CACHE_DIR", "/data/rag"))

if not SITE_ROOT.exists():
    local_dist = ROOT_DIR / "dist" / "webpage" / "frontend"
    if local_dist.exists():
        SITE_ROOT = local_dist
    else:
        SITE_ROOT = ROOT_DIR / "dist" / "webpage"

if not RAG_CACHE_DIR.exists():
    try:
        RAG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan management."""
    with MeasureTime("backend_startup"):
        logger.info("Starting DocShell Modular Backend...")
        
        # 1. Load initial base documents into SQLite
        base_docs = load_base_docs()
        logger.info(f"Loaded {len(base_docs)} base documents into SQLite.")

        # 2. Start background translation worker
        trans_worker.start()

        # 3. Initialize RAG search index and vector embeddings
        init_rag_service(SITE_ROOT, RAG_CACHE_DIR, ROOT_DIR)

        log_event("backend_initialized", details={"docs_count": len(base_docs)})

    yield
    logger.info("Shutting down DocShell Backend...")


app = FastAPI(
    title="DocShell Backend Gateway",
    description="Atomic & Modular Backend with Vector Search, TranslateGemma Async Queue, WebSocket Chat & Datadog Observability",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Modular Routers
app.include_router(chat_router)
app.include_router(ws_chat_router)
app.include_router(docs_router)
app.include_router(translations_router)
app.include_router(telemetry_router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
