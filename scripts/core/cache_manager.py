#!/usr/bin/env python3
"""
DocShell Core - Cache Manager (Redis with Fallback to Local Disk/Memory Cache)
Provides persistent caching for translations (TranslateGemma) and vector index chunks.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("docshell-cache")

def _resolve_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent

ROOT_DIR = _resolve_root()
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

FALLBACK_CACHE_PATH = ROOT_DIR / "publication" / "translations_cache.json"


class DocShellCache:
    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or ROOT_DIR
        self.fallback_file = self.root_dir / "publication" / "translations_cache.json"
        self._memory_cache: Dict[str, Any] = {}
        self._redis_client = None
        self._redis_available = False
        self.stats = {"hits": 0, "misses": 0, "engine": "disk"}
        
        self._init_redis()
        self._load_fallback_cache()

    def _init_redis(self):
        """Attempts to initialize connection to Redis server."""
        try:
            import redis
            client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                socket_timeout=1.5,
                socket_connect_timeout=1.5,
                decode_responses=True
            )
            client.ping()
            self._redis_client = client
            self._redis_available = True
            self.stats["engine"] = "redis"
            logger.info(f"Connected to Redis cache at {REDIS_HOST}:{REDIS_PORT}")
        except Exception:
            self._redis_available = False
            self.stats["engine"] = "disk"

    def _load_fallback_cache(self):
        """Loads cached entries from disk fallback file."""
        if self.fallback_file.exists():
            try:
                self._memory_cache = json.loads(self.fallback_file.read_text(encoding="utf-8"))
            except Exception:
                self._memory_cache = {}

    def _save_fallback_cache(self):
        """Persists memory cache to disk fallback file."""
        try:
            self.fallback_file.parent.mkdir(parents=True, exist_ok=True)
            self.fallback_file.write_text(
                json.dumps(self._memory_cache, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.warning(f"Failed to save disk cache: {e}")

    # =========================================================================
    # Translation Cache Operations
    # =========================================================================
    def _is_poisoned_text(self, text: Any) -> bool:
        """Checks if text contains LLM prompt artifacts / prompt echo."""
        if not text or not isinstance(text, str):
            return False
        markers = [
            "CRITICAL RULES:",
            "Preserve ALL Markdown syntax",
            "Content to translate:",
            "You are a professional technical documentation translator"
        ]
        return any(m in text for m in markers)

    def get_translation(self, source_locale: str, target_locale: str, text_hash: str) -> Optional[str]:
        """Retrieves cached translation text for given text hash."""
        key = f"docshell:trans:{source_locale}->{target_locale}:{text_hash}"
        
        if self._redis_available and self._redis_client:
            try:
                val = self._redis_client.get(key)
                if val:
                    if self._is_poisoned_text(val):
                        self._redis_client.delete(key)
                    else:
                        self.stats["hits"] += 1
                        return val
            except Exception:
                pass

        # Fallback to local memory / disk cache
        if key in self._memory_cache:
            val = self._memory_cache[key]
            if self._is_poisoned_text(val):
                del self._memory_cache[key]
                self._save_fallback_cache()
            else:
                self.stats["hits"] += 1
                return val

        self.stats["misses"] += 1
        return None

    def set_translation(self, source_locale: str, target_locale: str, text_hash: str, translated_text: str, ttl_seconds: int = 2592000):
        """Stores translated text in Redis and local disk cache."""
        if not translated_text or self._is_poisoned_text(translated_text):
            return

        key = f"docshell:trans:{source_locale}->{target_locale}:{text_hash}"
        
        if self._redis_available and self._redis_client:
            try:
                self._redis_client.setex(key, ttl_seconds, translated_text)
            except Exception:
                pass

        self._memory_cache[key] = translated_text
        self._save_fallback_cache()

    # =========================================================================
    # Document Cache Operations
    # =========================================================================
    def get_doc(self, locale: str, slug: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached translated document structure."""
        key = f"docshell:doc:{locale}:{slug}"
        if self._redis_available and self._redis_client:
            try:
                raw = self._redis_client.get(key)
                if raw:
                    data = json.loads(raw)
                    if self._is_poisoned_text(data.get("section", "")) or self._is_poisoned_text(data.get("title", "")) or self._is_poisoned_text(data.get("html_body", "")):
                        self._redis_client.delete(key)
                    else:
                        self.stats["hits"] += 1
                        return data
            except Exception:
                pass

        if key in self._memory_cache:
            val = self._memory_cache[key]
            data = json.loads(val) if isinstance(val, str) else val
            if self._is_poisoned_text(data.get("section", "")) or self._is_poisoned_text(data.get("title", "")) or self._is_poisoned_text(data.get("html_body", "")):
                del self._memory_cache[key]
                self._save_fallback_cache()
            else:
                self.stats["hits"] += 1
                return data

        self.stats["misses"] += 1
        return None

    def set_doc(self, locale: str, slug: str, doc_data: Dict[str, Any], ttl_seconds: int = 2592000):
        """Stores translated document in cache."""
        if self._is_poisoned_text(doc_data.get("section", "")) or self._is_poisoned_text(doc_data.get("title", "")) or self._is_poisoned_text(doc_data.get("html_body", "")):
            return

        key = f"docshell:doc:{locale}:{slug}"
        val_str = json.dumps(doc_data, ensure_ascii=False)
        
        if self._redis_available and self._redis_client:
            try:
                self._redis_client.setex(key, ttl_seconds, val_str)
            except Exception:
                pass

        self._memory_cache[key] = doc_data
        self._save_fallback_cache()

    def get_stats(self) -> Dict[str, Any]:
        """Returns cache telemetry stats."""
        total = self.stats["hits"] + self.stats["misses"]
        hit_ratio = round((self.stats["hits"] / total) * 100, 2) if total > 0 else 0.0
        return {
            "engine": self.stats["engine"],
            "redis_connected": self._redis_available,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_ratio_percent": hit_ratio,
            "cached_keys_count": len(self._memory_cache)
        }


# Singleton Instance
cache_manager = DocShellCache()
