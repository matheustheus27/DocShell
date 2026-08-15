#!/usr/bin/env python3
"""
DocShell Backend - Pydantic Data Models & Schemas
"""

from typing import List, Optional
from pydantic import BaseModel


class SourceItem(BaseModel):
    title: str
    slug: str
    doc_title: Optional[str] = ""
    section: Optional[str] = ""


class ChatRequest(BaseModel):
    message: Optional[str] = None
    query: Optional[str] = None
    locale: Optional[str] = "pt-BR"
    top_k: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    model: str
    engine: Optional[str] = "ollama-vector-rag"


class TranslateRequest(BaseModel):
    text: str
    target_locale: str
    source_locale: Optional[str] = "pt-BR"


class TranslateResponse(BaseModel):
    translated_text: str
    target_locale: str
    model: str


class TranslationStatusResponse(BaseModel):
    locale: str
    status: str
    progress: int
    completed_count: int
    total_count: int
    docs: List[dict] = []
