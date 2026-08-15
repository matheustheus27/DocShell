#!/usr/bin/env python3
"""
DocShell Backend - Translations Status & Management Router
"""

from fastapi import APIRouter, Query
from scripts.core.logger import MeasureTime
from scripts.core.database import db
from scripts.core.translator import normalize_locale
from scripts.rag.models.schemas import TranslateRequest, TranslateResponse, TranslationStatusResponse
from scripts.rag.services.translation_worker import translate_text, OLLAMA_TRANSLATE_MODEL
from scripts.rag.routers.docs import load_base_docs

router = APIRouter(tags=["Translations"])


@router.get("/api/translations/status", response_model=TranslationStatusResponse)
async def translation_status(locale: str = Query(...)):
    """Queries async translation job status and percentage."""
    norm_locale = normalize_locale(locale)
    base_docs = load_base_docs()
    total = len(base_docs)

    db_translations = db.get_translations_for_locale(norm_locale)
    base_slugs = {d["slug"] for d in base_docs}
    valid_translations = [d for d in db_translations if d["slug"] in base_slugs and d.get("status") == "completed"]
    completed_count = len(valid_translations)

    job = db.get_latest_job_for_locale(norm_locale)
    is_completed = (completed_count >= total and total > 0)
    status = "completed" if is_completed else (job["status"] if job else "pending")
    progress = 100 if is_completed else int((completed_count / total) * 100 if total else 0)

    doc_map = {d["slug"]: d for d in valid_translations}
    ordered = [doc_map[d["slug"]] for d in base_docs if d["slug"] in doc_map]

    return TranslationStatusResponse(
        locale=norm_locale,
        status=status,
        progress=progress,
        completed_count=completed_count,
        total_count=total,
        docs=ordered if is_completed else []
    )


@router.post("/api/translate", response_model=TranslateResponse)
async def translate_endpoint(req: TranslateRequest):
    """Translates Markdown documentation content with TranslateGemma."""
    with MeasureTime("translate_text", extra={"target_locale": req.target_locale}):
        src = req.source_locale or "pt-BR"
        translated = await translate_text(req.text, target_locale=req.target_locale, source_locale=src)
        return TranslateResponse(
            translated_text=translated,
            target_locale=req.target_locale,
            model=OLLAMA_TRANSLATE_MODEL
        )
