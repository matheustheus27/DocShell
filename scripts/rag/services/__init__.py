"""DocShell Services Package"""
from .ollama_service import get_available_ollama_models, fetch_embedding, generate_text, OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_EMBED_MODEL, OLLAMA_TRANSLATE_MODEL
from .rag_service import init_rag_service, vector_search, lexical_search, CHUNKS, EMBEDDINGS
from .translation_worker import trans_worker, translate_text
from .database_service import db
from .cache_service import cache_manager

__all__ = [
    "get_available_ollama_models",
    "fetch_embedding",
    "generate_text",
    "OLLAMA_HOST",
    "OLLAMA_MODEL",
    "OLLAMA_EMBED_MODEL",
    "OLLAMA_TRANSLATE_MODEL",
    "init_rag_service",
    "vector_search",
    "lexical_search",
    "CHUNKS",
    "EMBEDDINGS",
    "trans_worker",
    "translate_text",
    "db",
    "cache_manager",
]
