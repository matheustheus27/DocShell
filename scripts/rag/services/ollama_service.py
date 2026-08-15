#!/usr/bin/env python3
"""
DocShell Backend - Ollama AI Inference Service
Manages communication with Ollama for text generation, embeddings, and model discovery.
"""

import os
import json
import urllib.request
from typing import List, Optional, Any
from scripts.core.logger import get_logger

try:
    import httpx
except ImportError:
    httpx = None

logger = get_logger("docshell-ollama-service")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_TRANSLATE_MODEL = os.getenv("OLLAMA_TRANSLATE_MODEL", "translategemma")


def _sync_http_post(url: str, payload: dict, timeout: float = 15.0) -> Optional[dict]:
    """Fallback synchronous HTTP POST using standard urllib."""
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception:
        pass
    return None


def _sync_http_get(url: str, timeout: float = 3.0) -> Optional[dict]:
    """Fallback synchronous HTTP GET using standard urllib."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DocShell-Backend"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception:
        pass
    return None


async def get_available_ollama_models(client: Optional[Any] = None) -> List[str]:
    """Queries Ollama /api/tags to discover available installed models."""
    url = f"{OLLAMA_HOST}/api/tags"
    if httpx and client and isinstance(client, httpx.AsyncClient):
        try:
            res = await client.get(url, timeout=3.0)
            if res.status_code == 200:
                data = res.json()
                return [m.get("name") for m in data.get("models", []) if m.get("name")]
        except Exception:
            pass
    else:
        data = _sync_http_get(url, timeout=3.0)
        if data:
            return [m.get("name") for m in data.get("models", []) if m.get("name")]
    return []


async def fetch_embedding(text: str, client: Optional[Any] = None) -> Optional[List[float]]:
    """Calls Ollama embeddings endpoint."""
    url = f"{OLLAMA_HOST}/api/embeddings"
    payload = {"model": OLLAMA_EMBED_MODEL, "prompt": text}

    if httpx and client and isinstance(client, httpx.AsyncClient):
        try:
            res = await client.post(url, json=payload, timeout=15.0)
            if res.status_code == 200:
                return res.json().get("embedding")
        except Exception as e:
            logger.warning(f"Ollama embedding request error: {e}")
    else:
        res_json = _sync_http_post(url, payload, timeout=15.0)
        if res_json:
            return res_json.get("embedding")
    return None


async def generate_text(
    prompt: str,
    preferred_model: Optional[str] = None,
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.2,
    timeout: float = 60.0
) -> Optional[str]:
    """Attempts text generation with preferred model, then fallbacks, then any discovered model."""
    target_model = preferred_model or OLLAMA_MODEL
    models_to_try = [target_model]
    if fallback_models:
        for m in fallback_models:
            if m not in models_to_try:
                models_to_try.append(m)

    url = f"{OLLAMA_HOST}/api/generate"
    gen_options = {
        "temperature": temperature,
        "num_predict": 4096,
        "num_ctx": 8192
    }

    if httpx:
        async with httpx.AsyncClient(timeout=timeout) as client:
            for m in models_to_try:
                try:
                    res = await client.post(
                        url,
                        json={"model": m, "prompt": prompt, "stream": False, "options": gen_options}
                    )
                    if res.status_code == 200:
                        text = res.json().get("response", "").strip()
                        if text:
                            return text
                except Exception:
                    continue

            # Dynamic fallback to any available model
            available = await get_available_ollama_models(client)
            for m in available:
                if m not in models_to_try:
                    try:
                        res = await client.post(
                            url,
                            json={"model": m, "prompt": prompt, "stream": False, "options": gen_options}
                        )
                        if res.status_code == 200:
                            text = res.json().get("response", "").strip()
                            if text:
                                return text
                    except Exception:
                        continue
    else:
        for m in models_to_try:
            payload = {"model": m, "prompt": prompt, "stream": False, "options": gen_options}
            res_json = _sync_http_post(url, payload, timeout=timeout)
            if res_json:
                text = res_json.get("response", "").strip()
                if text:
                    return text
    return None
