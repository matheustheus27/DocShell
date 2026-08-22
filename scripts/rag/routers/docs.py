#!/usr/bin/env python3
"""
DocShell Backend - Documentation & Localization Router
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, Query

from scripts.core.logger import MeasureTime
from scripts.core.database import db
from scripts.core.translator import normalize_locale, translate_section
from scripts.core.doc_parser import parse_markdown_to_html, scan_docs_directory
from scripts.rag.services.translation_worker import trans_worker

router = APIRouter(tags=["Documents"])

def _resolve_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent

ROOT_DIR = _resolve_root()
SITE_ROOT = Path("/site") if Path("/site").exists() else (ROOT_DIR / "dist" / "webpage" / "frontend")


def load_base_docs() -> List[Dict[str, Any]]:
    """Loads base pt-BR documents from SQLite, docs-i18n.json, or docs/."""
    # 1. SQLite
    db_docs = db.get_all_documents()
    if db_docs and len(db_docs) > 0:
        return db_docs

    # 2. JSON
    candidates = [
        SITE_ROOT / "data" / "docs-i18n.json",
        ROOT_DIR / "dist" / "webpage" / "frontend" / "data" / "docs-i18n.json",
        ROOT_DIR / "dist" / "webpage" / "data" / "docs-i18n.json"
    ]
    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "pt-BR" in data:
                    for d in data["pt-BR"]:
                        db.upsert_document(d)
                    return data["pt-BR"]
            except Exception:
                pass

    # 3. docs/
    docs_dir = ROOT_DIR / "docs"
    if docs_dir.exists():
        raw_docs = scan_docs_directory(docs_dir, locale="pt-BR")
        parsed = [
            {
                "slug": d["slug"],
                "section": d["section"],
                "title": d["title"],
                "body": d["body"],
                "html_body": parse_markdown_to_html(d["body"]),
                "relative_path": d.get("relative_path", "")
            }
            for d in raw_docs
        ]
        for d in parsed:
            db.upsert_document(d)
        return parsed

    return []


@router.get("/api/docs")
async def get_docs(locale: str = Query("pt-BR")):
    """
    Returns localized documentation documents.
    If cached in SQLite, returns with status 'completed'.
    If not yet translated, enqueues background worker and returns base docs with status 'translating'.
    """
    norm_locale = normalize_locale(locale)
    with MeasureTime("get_docs", extra={"locale": norm_locale}):
        base_docs = load_base_docs()
        if norm_locale == "pt-BR" or not base_docs:
            return {"status": "completed", "locale": "pt-BR", "docs": base_docs, "cached": True, "progress": 100}

        # 1. Check if complete translation exists in SQLite
        db_translations = db.get_translations_for_locale(norm_locale)
        base_slugs = {d["slug"] for d in base_docs}
        valid_translations = [d for d in db_translations if d["slug"] in base_slugs and d.get("status") == "completed"]
        if len(valid_translations) >= len(base_docs) and len(base_docs) > 0:
            doc_map = {d["slug"]: d for d in valid_translations}
            ordered = [doc_map[d["slug"]] for d in base_docs if d["slug"] in doc_map]
            return {"status": "completed", "locale": norm_locale, "docs": ordered, "cached": True, "progress": 100}

        # 2. Enqueue background translation
        job_id = await trans_worker.enqueue_locale(norm_locale, base_docs)

        # Return instant dictionary fallback
        instant_docs = [
            {
                "slug": d["slug"],
                "section": translate_section(d.get("section", "General"), norm_locale),
                "title": translate_section(d.get("title", ""), norm_locale) if d.get("title") else d.get("title", ""),
                "body": d.get("body", ""),
                "html_body": d.get("html_body", ""),
                "locale": norm_locale
            }
            for d in base_docs
        ]

        return {
            "status": "translating",
            "job_id": job_id,
            "locale": norm_locale,
            "docs": instant_docs,
            "cached": False,
            "progress": int((len(db_translations) / len(base_docs)) * 100) if base_docs else 0
        }
