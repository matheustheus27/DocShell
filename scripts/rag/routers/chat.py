#!/usr/bin/env python3
"""
DocShell Backend - REST Chat Router
"""

try:
    import httpx
except ImportError:
    httpx = None

try:
    import numpy as np
except ImportError:
    np = None

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException

from scripts.core.logger import MeasureTime, get_logger
from scripts.core.translator import normalize_locale
from scripts.rag.models.schemas import ChatRequest, ChatResponse, SourceItem
from scripts.rag.services.ollama_service import fetch_embedding, generate_text, OLLAMA_MODEL
from scripts.rag.services.rag_service import vector_search, lexical_search, EMBEDDINGS

logger = get_logger("docshell-chat-router")
router = APIRouter(tags=["Chat"])


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    RAG Chat endpoint with multi-lingual Ollama synthesis and Datadog tracing.
    """
    user_query = (req.message or req.query or "").strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")

    target_locale = normalize_locale(req.locale or "pt-BR")
    top_k = req.top_k or 5

    with MeasureTime("chat_query", extra={"locale": target_locale, "query": user_query[:50]}):
        relevant_chunks: List[Dict[str, Any]] = []

        # 1. Vector Search
        try:
            if httpx is not None:
                async with httpx.AsyncClient() as client:
                    q_emb = await fetch_embedding(user_query, client)
            else:
                q_emb = await fetch_embedding(user_query)

            if q_emb is not None and EMBEDDINGS is not None and np is not None:
                q_vec = np.array(q_emb, dtype=np.float32)
                q_norm = np.linalg.norm(q_vec)
                if q_norm > 0:
                    q_vec = q_vec / q_norm
                    relevant_chunks = vector_search(q_vec, top_k=top_k)
        except Exception as vec_err:
            logger.warning(f"Vector search lookup error: {vec_err}")

        # 2. Lexical Fallback
        if not relevant_chunks:
            relevant_chunks = lexical_search(user_query, top_k=top_k)

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

        context_blocks = []
        for i, c in enumerate(relevant_chunks, 1):
            context_blocks.append(
                f"[{i}] Documento: {c.get('doc_title')}\n"
                f"Seção: {c.get('chunk_title')} (#{c.get('slug')})\n"
                f"Conteúdo: {c.get('text')}\n"
            )
        context_str = "\n".join(context_blocks)

        system_prompt = (
            f"You are the technical documentation AI assistant for DocShell.\n"
            f"Answer the user query accurately in {target_locale} in a clear, didactic, and well-structured format with Markdown (bold, lists, code blocks).\n"
            f"Guidelines:\n"
            f"1. Base your answer strictly on the DOCUMENTATION CONTEXT below.\n"
            f"2. Use code blocks (```...```) when providing commands or code examples.\n\n"
            f"DOCUMENTATION CONTEXT:\n{context_str}\n\n"
            f"USER QUESTION:\n{user_query}\n\n"
            f"ANSWER:"
        )

        try:
            answer = await generate_text(
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
            model="lexical-index-fallback",
            engine="local-search"
        )
