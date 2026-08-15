#!/usr/bin/env python3
"""
DocShell Backend - Realtime WebSocket Streaming Chat Router
"""

import json
import time
try:
    import httpx
except ImportError:
    httpx = None

try:
    import numpy as np
except ImportError:
    np = None

from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from scripts.core.logger import get_logger, log_event
from scripts.core.translator import normalize_locale
from scripts.rag.services.ollama_service import fetch_embedding, OLLAMA_HOST, OLLAMA_MODEL
from scripts.rag.services.rag_service import vector_search, lexical_search, EMBEDDINGS

logger = get_logger("docshell-wschat-router")
router = APIRouter(tags=["WebSocket Chat"])


@router.websocket("/ws/chat")
@router.websocket("/api/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """
    Realtime Token-by-Token Streaming Chat over WebSocket with LLaMA 3.2.
    """
    await websocket.accept()
    logger.info("[WebSocket] Realtime chat client connected.")

    try:
        while True:
            raw_msg = await websocket.receive_text()
            try:
                payload = json.loads(raw_msg)
            except Exception:
                payload = {"message": raw_msg}

            user_query = payload.get("message", "").strip()
            if not user_query:
                continue

            target_locale = normalize_locale(payload.get("locale", "pt-BR"))
            top_k = payload.get("top_k", 5)

            start_t = time.perf_counter()
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
                logger.warning(f"WebSocket vector search error: {vec_err}")

            # 2. Lexical Fallback
            if not relevant_chunks:
                relevant_chunks = lexical_search(user_query, top_k=top_k)

            # Send sources early to client
            sources_list = []
            seen_slugs = set()
            for c in relevant_chunks:
                slug = c.get("slug", "")
                title = c.get("chunk_title") or c.get("doc_title") or "Documentação"
                if slug and slug not in seen_slugs:
                    seen_slugs.add(slug)
                    sources_list.append({
                        "title": title,
                        "slug": slug,
                        "doc_title": c.get("doc_title", ""),
                        "section": c.get("section", "")
                    })

            await websocket.send_text(json.dumps({
                "type": "sources",
                "sources": sources_list
            }))

            # Build context prompt
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

            # Stream generation from Ollama
            stream_success = False
            if httpx is not None:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    try:
                        async with client.stream(
                            "POST",
                            f"{OLLAMA_HOST}/api/generate",
                            json={"model": OLLAMA_MODEL, "prompt": system_prompt, "stream": True, "options": {"temperature": 0.3}}
                        ) as response:
                            if response.status_code == 200:
                                stream_success = True
                                async for chunk_bytes in response.aiter_lines():
                                    if chunk_bytes:
                                        try:
                                            chunk_obj = json.loads(chunk_bytes)
                                            token = chunk_obj.get("response", "")
                                            if token:
                                                await websocket.send_text(json.dumps({"type": "token", "token": token}))
                                            if chunk_obj.get("done", False):
                                                break
                                        except Exception:
                                            pass
                    except Exception as stream_err:
                        logger.warning(f"WebSocket streaming error with Ollama: {stream_err}")
            else:
                # Fallback to generate_text
                from scripts.rag.services.ollama_service import generate_text
                gen_text = await generate_text(system_prompt, preferred_model=OLLAMA_MODEL, temperature=0.3)
                if gen_text:
                    stream_success = True
                    for word in gen_text.split(" "):
                        await websocket.send_text(json.dumps({"type": "token", "token": word + " "}))
                        await asyncio.sleep(0.015)

            # Fallback if streaming failed
            if not stream_success:
                if relevant_chunks:
                    top_c = relevant_chunks[0]
                    fallback_text = (
                        f"**Resultado da busca na documentação:**\n\n"
                        f"Na seção [**{top_c.get('chunk_title')}**](#{top_c.get('slug')}) do documento *{top_c.get('doc_title')}*:\n\n"
                        f"> {top_c.get('text')}\n\n"
                        f"*(💡 Dica: Para respostas formuladas por IA em tempo real, inicie o Ollama com o modelo `{OLLAMA_MODEL}`).*"
                    )
                else:
                    fallback_text = "Não encontrei informações específicas sobre esta consulta na documentação."

                for word in fallback_text.split(" "):
                    await websocket.send_text(json.dumps({"type": "token", "token": word + " "}))
                    await asyncio.sleep(0.02)

            duration = round((time.perf_counter() - start_t) * 1000, 2)
            log_event("ws_chat_completed", details={"query": user_query[:40], "locale": target_locale}, duration_ms=duration)
            await websocket.send_text(json.dumps({"type": "done", "duration_ms": duration}))

    except WebSocketDisconnect:
        logger.info("[WebSocket] Realtime chat client disconnected.")
    except Exception as e:
        logger.error(f"[WebSocket] Session error: {e}")
