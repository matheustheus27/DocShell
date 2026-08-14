#!/usr/bin/env python3
"""
DocShell Python Web Server & RAG API
Executa o servidor local HTTP para a documentação e fornece a API REST do Chatbot IA.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

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
from scripts.core.rag_engine import DocShellRAG


class DocShellHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        self.rag_engine = DocShellRAG(ROOT_DIR)
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            status_data = {
                "status": "online",
                "runtime": "python",
                "rag_enabled": True,
                "ollama_host": self.rag_engine.ollama_host,
                "chat_model": getattr(self.rag_engine, "active_model", "llama3.2")
            }
            self.wfile.write(json.dumps(status_data).encode("utf-8"))
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            
            try:
                body_json = json.loads(body_bytes.decode("utf-8"))
                user_msg = body_json.get("message", "").strip() or body_json.get("query", "").strip()
                user_locale = body_json.get("locale", "pt-BR")
                
                result = self.rag_engine.ask(user_msg, locale=user_locale)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
                return

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

        if parsed.path == "/api/translate":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                body_json = json.loads(body_bytes.decode("utf-8"))
                text = body_json.get("text", "")
                target_loc = body_json.get("target_locale", "en-US")
                src_loc = body_json.get("source_locale", "pt-BR")

                from scripts.core.translator import translate_text
                translated = translate_text(text, target_locale=target_loc, source_locale=src_loc, root_dir=ROOT_DIR)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"translated_text": translated}, ensure_ascii=False).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

        self.send_error(404, "Endpoint não encontrado")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run_server(port: int = 8000):
    dist_web = ROOT_DIR / "dist" / "webpage"
    if not (dist_web / "index.html").exists():
        print("⚠️ dist/webpage/index.html não encontrado. Compilando site...")
        from scripts.generators.python.build_site import build_python_site
        build_python_site()

    print("=================================================================")
    print(f"🚀 DocShell Python Server & RAG Engine")
    print(f"   URL: http://127.0.0.1:{port}")
    print(f"   Doc Root: {dist_web}")
    print("   Pressione Ctrl+C para encerrar.")
    print("=================================================================")

    handler = lambda *args, **kwargs: DocShellHTTPHandler(*args, directory=str(dist_web), **kwargs)
    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor encerrado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DocShell Python Web Server")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Porta HTTP")
    args = parser.parse_args()
    run_server(args.port)
