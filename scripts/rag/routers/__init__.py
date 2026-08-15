"""DocShell Routers Package"""
from .chat import router as chat_router
from .ws_chat import router as ws_chat_router
from .docs import router as docs_router
from .translations import router as translations_router
from .telemetry import router as telemetry_router

__all__ = [
    "chat_router",
    "ws_chat_router",
    "docs_router",
    "translations_router",
    "telemetry_router",
]
