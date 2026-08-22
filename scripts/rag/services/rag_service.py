#!/usr/bin/env python3
"""
DocShell Backend - Vector RAG & Search Service
Handles vector chunk search, indexing, cosine similarity, and lexical search fallback.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import httpx
except ImportError:
    httpx = None

try:
    import numpy as np
except ImportError:
    np = None

from scripts.core.logger import get_logger
from scripts.rag.services.ollama_service import fetch_embedding, OLLAMA_EMBED_MODEL

logger = get_logger("docshell-rag-service")

CHUNKS: List[Dict[str, Any]] = []
EMBEDDINGS: Optional[Any] = None


def init_rag_service(site_root: Path, cache_dir: Path, root_dir: Path):
    """Loads search index and pre-computed vector embeddings."""
    global CHUNKS, EMBEDDINGS
    candidates = [
        site_root / "data" / "search_index.json",
        site_root / "search_index.json",
        root_dir / "data" / "search_index.json",
        root_dir / "dist" / "webpage" / "frontend" / "data" / "search_index.json",
        root_dir / "dist" / "webpage" / "data" / "search_index.json",
        root_dir / "publication" / "search_index.json"
    ]
    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    CHUNKS = data
                    logger.info(f"Loaded {len(CHUNKS)} search chunks from {p}")
                    break
            except Exception as e:
                logger.error(f"Error reading search index: {e}")

    if np is not None:
        cache_file = cache_dir / f"embeddings_{OLLAMA_EMBED_MODEL.replace(':', '_')}.npy"
        if cache_file.exists():
            try:
                EMBEDDINGS = np.load(cache_file)
                logger.info(f"Loaded {len(EMBEDDINGS)} pre-computed vector embeddings from cache.")
            except Exception:
                pass

        if EMBEDDINGS is None and CHUNKS:
            asyncio.create_task(build_embeddings_cache(cache_file))


async def build_embeddings_cache(cache_file: Path):
    """Builds vector embeddings for all documentation chunks in the background."""
    global EMBEDDINGS
    if np is None:
        return
    logger.info(f"Generating vector embeddings via Ollama ({OLLAMA_EMBED_MODEL})...")
    vecs = []
    
    if httpx:
        async with httpx.AsyncClient() as client:
            for chunk in CHUNKS:
                snippet = f"{chunk.get('chunk_title', '')}\n{chunk.get('text', '')}"
                emb = await fetch_embedding(snippet, client)
                vecs.append(emb if emb else [0.0] * 768)
    else:
        for chunk in CHUNKS:
            snippet = f"{chunk.get('chunk_title', '')}\n{chunk.get('text', '')}"
            emb = await fetch_embedding(snippet)
            vecs.append(emb if emb else [0.0] * 768)

    if vecs:
        EMBEDDINGS = np.array(vecs, dtype=np.float32)
        norms = np.linalg.norm(EMBEDDINGS, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        EMBEDDINGS = EMBEDDINGS / norms
        try:
            np.save(cache_file, EMBEDDINGS)
            logger.info(f"Saved {len(EMBEDDINGS)} vector embeddings to {cache_file}")
        except Exception as e:
            logger.warning(f"Could not persist embeddings cache: {e}")


def vector_search(query_vec: Any, top_k: int = 5) -> List[Dict[str, Any]]:
    """Performs cosine similarity search using dot product on normalized vectors."""
    if np is None or EMBEDDINGS is None or len(EMBEDDINGS) == 0:
        return []
    scores = np.dot(EMBEDDINGS, query_vec)
    top_indices = np.argsort(scores)[::-1][:top_k]
    results = []
    for idx in top_indices:
        c = dict(CHUNKS[idx])
        c["score"] = float(scores[idx])
        results.append(c)
    return results


def lexical_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
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
