#!/usr/bin/env python3
"""
DocShell - Vector RAG Backend Microservice (FastAPI + Ollama Embeddings + Redis Cache + Datadog Tracing)
Provides semantic search, dynamic on-demand TranslateGemma translations, and LLM chat.
"""

import os
import sys
import json
import logging
import asyncio
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

import httpx
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path for imports
_parents = Path(__file__).resolve().parents
if len(_parents) > 2 and (_parents[2] / "docs").exists():
    ROOT_DIR = _parents[2]
elif len(_parents) > 0 and (_parents[0] / "scripts").exists():
    ROOT_DIR = _parents[0]
elif Path("/app/scripts").exists():
    ROOT_DIR = Path("/app")
else:
    ROOT_DIR = Path.cwd()

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.core.cache_manager import cache_manager
from scripts.core.logger import get_logger, log_event, MeasureTime

logger = get_logger("docshell-rag")

# Environment & Config
SITE_ROOT = Path(os.getenv("SITE_ROOT", "/site"))
RAG_CACHE_DIR = Path(os.getenv("RAG_CACHE_DIR", "/data/rag"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_TRANSLATE_MODEL = os.getenv("OLLAMA_TRANSLATE_MODEL", "translategemma")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))

# Fallbacks for local / dev execution
if not SITE_ROOT.exists():
    local_dist = ROOT_DIR / "dist" / "webpage"
    if local_dist.exists():
        SITE_ROOT = local_dist
    else:
        SITE_ROOT = ROOT_DIR / "publication"

if not RAG_CACHE_DIR.exists():
    RAG_CACHE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="DocShell RAG & Translation Gateway",
    description="Vector Search, TranslateGemma Translation with Redis Caching, and Datadog Observability",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory State
CHUNKS: List[Dict[str, Any]] = []
EMBEDDINGS: Optional[np.ndarray] = None


class ChatRequest(BaseModel):
    message: Optional[str] = None
    query: Optional[str] = None
    locale: Optional[str] = "pt-BR"
    top_k: Optional[int] = None


class SourceItem(BaseModel):
    title: str
    slug: str
    doc_title: Optional[str] = ""
    section: Optional[str] = ""


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    model: str
    engine: Optional[str] = "ollama-vector-rag"


class TranslateRequest(BaseModel):
    text: str
    target_locale: str
    source_locale: Optional[str] = "pt-BR"


def load_search_index() -> List[Dict[str, Any]]:
    """Loads search chunks from search_index.json."""
    candidates = [
        SITE_ROOT / "data" / "search_index.json",
        SITE_ROOT / "search_index.json",
        ROOT_DIR / "publication" / "search_index.json",
        ROOT_DIR / "dist" / "webpage" / "data" / "search_index.json"
    ]
    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
            except Exception as e:
                logger.error(f"Failed to read search index at {p}: {e}")
    return []


def load_base_docs() -> List[Dict[str, Any]]:
    """Loads base pt-BR documents from docs-i18n.json or scans docs."""
    candidates = [
        SITE_ROOT / "data" / "docs-i18n.json",
        ROOT_DIR / "dist" / "webpage" / "data" / "docs-i18n.json"
    ]
    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "pt-BR" in data:
                    return data["pt-BR"]
                elif isinstance(data, list):
                    return data
            except Exception:
                pass

    from scripts.core.doc_parser import scan_docs_directory, parse_markdown_to_html
    docs_dir = ROOT_DIR / "docs"
    if docs_dir.exists():
        raw_docs = scan_docs_directory(docs_dir, locale="pt-BR")
        return [
            {
                "slug": d["slug"],
                "section": d["section"],
                "title": d["title"],
                "body": d["body"],
                "html_body": parse_markdown_to_html(d["body"])
            }
            for d in raw_docs
        ]
    return []


async def fetch_embedding_from_ollama(text: str, client: httpx.AsyncClient) -> Optional[List[float]]:
    """Calls Ollama embeddings endpoint."""
    try:
        res = await client.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": OLLAMA_EMBED_MODEL, "prompt": text},
            timeout=30.0
        )
        if res.status_code == 200:
            return res.json().get("embedding")
    except Exception as e:
        logger.warning(f"Ollama embedding failed for text snippet: {e}")
    return None


@app.on_event("startup")
async def startup_event():
    """Initializes search chunks and vector embeddings."""
    global CHUNKS, EMBEDDINGS
    with MeasureTime("rag_service_startup"):
        logger.info("Initializing DocShell RAG Service...")
        CHUNKS = load_search_index()
        logger.info(f"Loaded {len(CHUNKS)} chunks from documentation index.")

        if not CHUNKS:
            logger.warning("No search chunks found. Search will operate in minimal mode.")
            return

        cache_file = RAG_CACHE_DIR / f"embeddings_{OLLAMA_EMBED_MODEL.replace(':', '_')}.npy"
        if cache_file.exists():
            try:
                EMBEDDINGS = np.load(cache_file)
                if len(EMBEDDINGS) == len(CHUNKS):
                    logger.info(f"Loaded pre-computed vector embeddings from {cache_file}")
                    return
            except Exception as e:
                logger.warning(f"Failed to load cached embeddings: {e}")

        # Compute embeddings asynchronously in background if Ollama is accessible
        asyncio.create_task(build_embeddings_index(cache_file))


async def build_embeddings_index(cache_file: Path):
    """Builds vector embeddings for all chunks in the documentation."""
    global EMBEDDINGS
    logger.info(f"Building vector embeddings using {OLLAMA_EMBED_MODEL} via {OLLAMA_HOST}...")
    vecs = []
    async with httpx.AsyncClient() as client:
        for i, chunk in enumerate(CHUNKS):
            snippet = f"{chunk.get('chunk_title', '')}\n{chunk.get('text', '')}"
            emb = await fetch_embedding_from_ollama(snippet, client)
            if emb:
                vecs.append(emb)
            else:
                vecs.append([0.0] * 768)

    if vecs:
        EMBEDDINGS = np.array(vecs, dtype=np.float32)
        # Normalize vectors for cosine similarity
        norms = np.linalg.norm(EMBEDDINGS, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        EMBEDDINGS = EMBEDDINGS / norms
        try:
            np.save(cache_file, EMBEDDINGS)
            logger.info(f"Successfully cached {len(EMBEDDINGS)} vector embeddings to {cache_file}")
        except Exception as e:
            logger.warning(f"Could not persist embeddings cache: {e}")


def vector_search(query_vec: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
    """Performs cosine similarity search using dot product on normalized vectors."""
    if EMBEDDINGS is None or len(EMBEDDINGS) == 0:
        return []
    scores = np.dot(EMBEDDINGS, query_vec)
    top_indices = np.argsort(scores)[::-1][:top_k]
    results = []
    for idx in top_indices:
        c = dict(CHUNKS[idx])
        c["score"] = float(scores[idx])
        results.append(c)
    return results


def lexical_search_fallback(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Keyword-based ranking fallback."""
    terms = query.lower().split()
    scored = []
    for chunk in CHUNKS:
        text = (chunk.get("text", "") + " " + chunk.get("chunk_title", "") + " " + chunk.get("doc_title", "")).lower()
        score = sum(text.count(t) for t in terms)
        if score > 0:
            c = dict(chunk)
            c["score"] = float(score)
            scored.append(c)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


async def get_available_ollama_models(client: httpx.AsyncClient) -> List[str]:
    """Queries Ollama /api/tags to list installed models."""
    try:
        res = await client.get(f"{OLLAMA_HOST}/api/tags", timeout=3.0)
        if res.status_code == 200:
            data = res.json()
            return [m.get("name") for m in data.get("models", []) if m.get("name")]
    except Exception:
        pass
    return []


async def generate_with_ollama(
    prompt: str,
    preferred_model: str,
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.2,
    timeout: float = 60.0
) -> Optional[str]:
    """Attempts text generation with preferred model, then fallbacks, then any discovered model."""
    models_to_try = [preferred_model]
    if fallback_models:
        for m in fallback_models:
            if m not in models_to_try:
                models_to_try.append(m)

    async with httpx.AsyncClient(timeout=timeout) as client:
        # First attempt configured models
        for m in models_to_try:
            try:
                res = await client.post(
                    f"{OLLAMA_HOST}/api/generate",
                    json={"model": m, "prompt": prompt, "stream": False, "options": {"temperature": temperature}}
                )
                if res.status_code == 200:
                    text = res.json().get("response", "").strip()
                    if text:
                        return text
            except Exception:
                continue

        # If still not generated, discover active models in Ollama
        available = await get_available_ollama_models(client)
        for m in available:
            if m not in models_to_try:
                try:
                    res = await client.post(
                        f"{OLLAMA_HOST}/api/generate",
                        json={"model": m, "prompt": prompt, "stream": False, "options": {"temperature": temperature}}
                    )
                    if res.status_code == 200:
                        text = res.json().get("response", "").strip()
                        if text:
                            return text
                except Exception:
                    continue
    return None


async def translate_text_via_ollama(text: str, target_locale: str, source_locale: str = "pt-BR") -> str:
    """Translates text using TranslateGemma / Ollama with Redis cache integration and prompt sanitization."""
    clean_text = (text or "").strip()
    if not clean_text or target_locale == source_locale:
        return text

    from scripts.core.translator import sanitize_translation_output, SECTION_DICTIONARY, translate_section

    # Check if this is a short section name
    if len(clean_text) < 30 and clean_text.lower() in SECTION_DICTIONARY.get("pt-BR", {}):
        return translate_section(clean_text, target_locale)

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
        translated = await generate_with_ollama(
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
        logger.warning(f"Ollama TranslateGemma translation failed: {e}")

    return text


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/healthz")
async def healthz():
    return {
        "status": "healthy",
        "service": "docshell-rag",
        "chunks_indexed": len(CHUNKS),
        "embeddings_ready": EMBEDDINGS is not None,
        "cache": cache_manager.get_stats()
    }


@app.get("/api/docs")
async def get_docs_endpoint(locale: str = Query("pt-BR")):
    """
    Returns documentation cards for the given locale.
    Retrieves from Redis cache or dynamically translates concurrently via TranslateGemma / Ollama.
    """
    with MeasureTime("get_docs", extra={"locale": locale}):
        base_docs = load_base_docs()
        if locale == "pt-BR" or not base_docs:
            return {"locale": "pt-BR", "docs": base_docs, "cached": True}

        from scripts.core.doc_parser import parse_markdown_to_html
        from scripts.core.translator import translate_section, sanitize_translation_output

        translated_docs: List[Dict[str, Any]] = []
        missing_docs: List[Dict[str, Any]] = []

        for d in base_docs:
            slug = d["slug"]
            cached_doc = cache_manager.get_doc(locale, slug)
            # Verify cached document is actually translated, valid, and not containing prompt echoes
            if (
                cached_doc
                and cached_doc.get("html_body")
                and not cache_manager._is_poisoned_text(cached_doc.get("section", ""))
                and not cache_manager._is_poisoned_text(cached_doc.get("title", ""))
                and not cache_manager._is_poisoned_text(cached_doc.get("html_body", ""))
                and (cached_doc.get("locale") == locale or cached_doc.get("title") != d["title"])
            ):
                translated_docs.append(cached_doc)
            else:
                missing_docs.append(d)

        if not missing_docs:
            return {"locale": locale, "docs": translated_docs, "cached": True}

        # Concurrently translate missing documents with bounded semaphore
        sem = asyncio.Semaphore(4)

        async def translate_single_doc(d: Dict[str, Any]) -> Dict[str, Any]:
            slug = d["slug"]
            raw_body = d.get("body", "") or d.get("html_body", "")
            # Direct dictionary translation for section tag (0-LLM latency, 100% reliable)
            trans_section = translate_section(d["section"], target_locale=locale)

            async with sem:
                trans_title, trans_body = await asyncio.gather(
                    translate_text_via_ollama(d["title"], target_locale=locale, source_locale="pt-BR"),
                    translate_text_via_ollama(raw_body, target_locale=locale, source_locale="pt-BR")
                )

                trans_title = sanitize_translation_output(trans_title, d["title"])
                trans_body = sanitize_translation_output(trans_body, raw_body)

                entry = {
                    "slug": slug,
                    "section": trans_section,
                    "title": trans_title,
                    "body": trans_body,
                    "html_body": parse_markdown_to_html(trans_body),
                    "locale": locale
                }

                # Only persist in Redis when translation succeeded (different from Portuguese original and unpoisoned)
                if (trans_body != raw_body or trans_title != d["title"]) and not cache_manager._is_poisoned_text(trans_body):
                    cache_manager.set_doc(locale, slug, entry)

                return entry

        newly_translated = await asyncio.gather(*[translate_single_doc(d) for d in missing_docs])
        doc_map = {d["slug"]: d for d in translated_docs + list(newly_translated)}
        ordered_docs = [doc_map.get(d["slug"], d) for d in base_docs]

        return {"locale": locale, "docs": ordered_docs, "cached": False}


@app.post("/api/translate")
async def translate_endpoint(req: TranslateRequest):
    """Translates Markdown documentation content via Ollama TranslateGemma with Redis caching."""
    with MeasureTime("translate_text", extra={"target_locale": req.target_locale}):
        src = req.source_locale or "pt-BR"
        translated = await translate_text_via_ollama(req.text, target_locale=req.target_locale, source_locale=src)
        return {
            "translated_text": translated,
            "target_locale": req.target_locale,
            "model": OLLAMA_TRANSLATE_MODEL
        }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    RAG Chat endpoint with multi-lingual Ollama synthesis and Datadog tracing.
    """
    user_query = (req.message or req.query or "").strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")

    target_locale = req.locale or "pt-BR"
    top_k = req.top_k or RAG_TOP_K

    with MeasureTime("chat_query", extra={"locale": target_locale, "query": user_query[:50]}):
        relevant_chunks: List[Dict[str, Any]] = []

        # 1. Try vector embedding search
        async with httpx.AsyncClient() as client:
            q_emb = await fetch_embedding_from_ollama(user_query, client)
            if q_emb is not None and EMBEDDINGS is not None:
                q_vec = np.array(q_emb, dtype=np.float32)
                q_norm = np.linalg.norm(q_vec)
                if q_norm > 0:
                    q_vec = q_vec / q_norm
                    relevant_chunks = vector_search(q_vec, top_k=top_k)

        # 2. Fallback to lexical BM25 search
        if not relevant_chunks:
            relevant_chunks = lexical_search_fallback(user_query, top_k=top_k)

        # Format sources
        sources_map: Dict[str, SourceItem] = {}
        for c in relevant_chunks:
            slug = c.get("slug", "")
            title = c.get("chunk_title") or c.get("doc_title") or "Documentação"
            if slug and slug not in sources_map:
                sources_map[slug] = SourceItem(
                    title=title,
                    slug=slug,
                    doc_title=c.get("doc_title", ""),
                    section=c.get("section", "")
                )
        sources_list = list(sources_map.values())

        # Build Context
        context_blocks = []
        for i, c in enumerate(relevant_chunks, 1):
            context_blocks.append(
                f"[{i}] Documento: {c.get('doc_title')}\n"
                f"Seção: {c.get('chunk_title')} (#{c.get('slug')})\n"
                f"Conteúdo: {c.get('text')}\n"
            )
        context_str = "\n".join(context_blocks)

        locale_names = {
            "pt-BR": "Português",
            "en-US": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "it": "Italiano",
            "zh-CN": "简体中文 (Chinese)",
            "ja": "日本語 (Japanese)",
            "ru": "Русский (Russian)"
        }
        target_lang = locale_names.get(target_locale, "Português")

        system_prompt = (
            f"You are the technical documentation AI assistant for DocShell.\n"
            f"Answer the user query accurately in {target_lang} ({target_locale}) in a clear, didactic, and well-structured format with Markdown (bold, lists, code blocks).\n"
            f"Guidelines:\n"
            f"1. Base your answer strictly on the DOCUMENTATION CONTEXT below.\n"
            f"2. Use code blocks (```...```) when providing commands or code examples.\n"
            f"3. Always respond in {target_lang}.\n\n"
            f"DOCUMENTATION CONTEXT:\n{context_str}\n\n"
            f"USER QUESTION:\n{user_query}\n\n"
            f"ANSWER IN {target_lang.upper()}:"
        )

        try:
            answer = await generate_with_ollama(
                prompt=system_prompt,
                preferred_model=OLLAMA_MODEL,
                fallback_models=["llama3.2", "translategemma", "gemma2", "mistral"],
                temperature=0.3,
                timeout=60.0
            )
            if answer and answer.strip():
                return ChatResponse(
                    answer=answer.strip(),
                    sources=sources_list,
                    model=OLLAMA_MODEL,
                    engine="ollama-vector-rag"
                )
        except Exception as err:
            logger.warning(f"Ollama generation call failed: {err}")

        # Fallback to search excerpt
        if relevant_chunks:
            top_c = relevant_chunks[0]
            fallback_answer = (
                f"**Resultado da busca na documentação:**\n\n"
                f"Na seção [**{top_c.get('chunk_title')}**](#{top_c.get('slug')}) do documento *{top_c.get('doc_title')}*:\n\n"
                f"> {top_c.get('text')}\n\n"
                f"*(💡 Dica: Para respostas formuladas por IA em tempo real, inicie o Ollama com o modelo `{OLLAMA_MODEL}`).*"
            )
        else:
            fallback_answer = "Não encontrei informações específicas sobre esta consulta na documentação."

        return ChatResponse(
            answer=fallback_answer,
            sources=sources_list,
            model="bm25-vector-fallback",
            engine="offline-search"
        )


@app.get("/api/cache/stats")
async def cache_stats():
    """Returns Redis and local cache telemetry."""
    return cache_manager.get_stats()


@app.get("/api/telemetry/report")
async def telemetry_report():
    """Generates and returns the latest Datadog telemetry performance report."""
    from scripts.core.datadog_reporter import load_telemetry_entries, generate_report
    entries = load_telemetry_entries()
    return generate_report(entries)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
