#!/usr/bin/env python3
"""
DocShell Core - RAG Engine (Retrieval-Augmented Generation)
Motor de busca semântica, indexação de documentos e conexão com LLMs locais (Ollama) ou APIs.
Suporta modelos TranslateGemma, Llama 3.2, Gemma 2, Qwen e gera referências clicáveis.
"""

import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

def _resolve_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent

ROOT_DIR = _resolve_root()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.core.config_loader import load_publication_config


class DocShellRAG:
    def __init__(self, root_dir: Path, config: Optional[Dict[str, Any]] = None):
        self.root_dir = root_dir
        self.config = config if config is not None else load_publication_config()
        self.ai_cfg = self.config.get("ai_assistant", {})
        
        ollama_cfg = self.ai_cfg.get("ollama", {})
        self.ollama_host = os.environ.get("OLLAMA_HOST", ollama_cfg.get("host", "http://127.0.0.1:11434")).rstrip("/")
        self.preferred_model = os.environ.get("OLLAMA_MODEL", ollama_cfg.get("chat_model", "llama3.2"))
        
        self.index_path = self.root_dir / "publication" / "search_index.json"
        self._chunks: List[Dict[str, Any]] = []
        self._load_index()
        self.active_model = self._detect_ollama_model()

    def _load_index(self):
        candidates = [
            self.root_dir / "data" / "search_index.json",
            self.root_dir / "publication" / "search_index.json",
            self.root_dir / "dist" / "webpage" / "frontend" / "data" / "search_index.json",
            self.root_dir / "frontend" / "data" / "search_index.json",
            Path("/site/data/search_index.json"),
        ]
        for p in candidates:
            if p.exists():
                try:
                    self._chunks = json.loads(p.read_text(encoding="utf-8"))
                    if isinstance(self._chunks, list) and self._chunks:
                        break
                except Exception:
                    self._chunks = []

    def _detect_ollama_model(self) -> str:
        """Verifica quais modelos estão instalados no Ollama local e seleciona o mais adequado."""
        try:
            req = urllib.request.Request(f"{self.ollama_host}/api/tags", headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                
                # 1. Se o modelo preferido estiver presente (ex: llama3.2, translategemma)
                for m in models:
                    if self.preferred_model in m or m.startswith(self.preferred_model):
                        return m
                
                # 2. Modelos recomendados em ordem
                priority_list = ["translategemma", "gemma2", "llama3.2", "llama3", "mistral", "qwen2.5", "qwen", "phi3", "deepseek-r1"]
                for p in priority_list:
                    for m in models:
                        if p in m:
                            return m
                
                # 3. Qualquer modelo disponível
                if models:
                    return models[0]
        except Exception:
            pass
        
        return self.preferred_model

    def _tokenize(self, text: str) -> List[str]:
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower(), flags=re.UNICODE)
        return [t for t in text_clean.split() if len(t) > 2]

    def search_bm25(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Busca BM25 / TF-IDF rápida sobre os chunks de texto."""
        if not self._chunks:
            self._load_index()
        if not self._chunks:
            return []

        query_terms = self._tokenize(query)
        if not query_terms:
            return self._chunks[:top_k]

        scores = []
        for chunk in self._chunks:
            text = f"{chunk.get('text', '')} {chunk.get('chunk_title', '')} {chunk.get('doc_title', '')} {chunk.get('section', '')}"
            chunk_terms = Counter(self._tokenize(text))
            
            score = 0.0
            for qt in query_terms:
                if qt in chunk_terms:
                    score += 1.0 + math.log(1.0 + chunk_terms[qt])
            
            if score > 0:
                scores.append((score, chunk))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scores[:top_k]]

    def ask(self, query: str, top_k: int = 5, locale: str = "pt-BR") -> Dict[str, Any]:
        """
        Executes hybrid search (lexical/semantic) and calls Ollama in the requested locale.
        """
        relevant_chunks = self.search_bm25(query, top_k=top_k)
        
        # Extrai fontes únicas com título e slug para links clicáveis
        sources_map = {}
        for c in relevant_chunks:
            title = c.get("chunk_title") or c.get("doc_title") or "Documentação"
            slug = c.get("slug", "")
            if title and slug and slug not in sources_map:
                sources_map[slug] = {
                    "title": title,
                    "slug": slug,
                    "doc_title": c.get("doc_title", ""),
                    "section": c.get("section", "")
                }
        sources_list = list(sources_map.values())

        if not relevant_chunks:
            return {
                "answer": "Não encontrei informações correspondentes na documentação do projeto.",
                "sources": [],
                "model": self.active_model
            }

        context_texts = []
        for i, c in enumerate(relevant_chunks, 1):
            context_texts.append(f"[{i}] Documento: {c.get('doc_title')}\nSeção: {c.get('chunk_title')} (#{c.get('slug')})\nConteúdo: {c.get('text')}\n")

        context_str = "\n".join(context_texts)

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
        target_lang = locale_names.get(locale, "Português")

        prompt = f"""You are the technical documentation AI assistant for GlassHub DocShell.
Answer the user query accurately in {target_lang} ({locale}) in a clear, professional, didactic, and well-structured Markdown format.
Base your answer strictly on the DOCUMENTATION CONTEXT below.

DOCUMENTATION CONTEXT:
{context_str}

USER QUESTION:
{query}

ANSWER IN {target_lang.upper()}:"""

        # 1. Tenta comunicação com Ollama local (re-detecta modelo disponível dinamicamente)
        current_model = self._detect_ollama_model()
        try:
            req_data = json.dumps({
                "model": current_model,
                "prompt": prompt,
                "stream": False
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.ollama_host}/api/generate",
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                llm_answer = result.get("response", "").strip()

            if llm_answer:
                return {
                    "answer": llm_answer,
                    "sources": sources_list,
                    "model": current_model,
                    "engine": "ollama-rag"
                }

        except Exception as err:
            pass

        # 2. Fallback inteligente com links clicáveis se Ollama não estiver rodando
        top_chunk = relevant_chunks[0]
        chunk_title = top_chunk.get('chunk_title', 'Seção')
        doc_title = top_chunk.get('doc_title', 'Documento')
        chunk_slug = top_chunk.get('slug', '')
        raw_text = top_chunk.get('text', '').strip()
        
        fallback_answer = (
            f"**Resultado da busca na documentação:**\n\n"
            f"Na seção [**{chunk_title}**](#{chunk_slug}) do documento *{doc_title}*:\n\n"
            f"> {raw_text}\n\n"
            f"*(💡 Dica: Para respostas sintetizadas por IA, inicie o Ollama com o modelo `{current_model}`).*"
        )
        return {
            "answer": fallback_answer,
            "sources": sources_list,
            "model": "bm25-retriever-fallback",
            "engine": "offline-search"
        }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    rag = DocShellRAG(root)
    print(f"🔍 DocShell RAG (Host: {rag.ollama_host}, Modelo: {rag.active_model}):")
    res = rag.ask("Como funciona a ordenação numérica dos arquivos no DocShell?")
    print("Resposta:\n", res["answer"])
    print("Fontes:", res["sources"])
