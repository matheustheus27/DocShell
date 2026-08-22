#!/usr/bin/env python3
"""
DocShell Web Generator - Python Engine
Converts Markdown docs into a responsive, modern HTML5 Web documentation
with live search, functional sidebar, multi-language switcher (9 locales),
theme models, and embedded RAG/AI Assistant widget.
"""

import argparse
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

def _resolve_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent

ROOT_DIR = _resolve_root()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.core.config_loader import load_publication_config, load_theme_model
from scripts.core.doc_parser import scan_docs_directory, build_search_and_rag_index, slugify, parse_markdown_to_html, parse_inline
from scripts.core.translator import SUPPORTED_LOCALES, get_ui_string, normalize_locale, translate_document_content, translate_section
from scripts.core.database import db

MERMAID_THEMES = {
    "glassmorphic": {
        "theme": "base",
        "themeVariables": {
            "darkMode": True,
            "background": "transparent",
            "mainBkg": "#0f172a",
            "nodeBorder": "#6366f1",
            "nodeTextColor": "#f8fafc",
            "clusterBkg": "rgba(30, 41, 59, 0.7)",
            "clusterBorder": "rgba(99, 102, 241, 0.4)",
            "defaultLinkColor": "#38bdf8",
            "lineColor": "#38bdf8",
            "arrowheadColor": "#38bdf8",
            "titleColor": "#e0e7ff",
            "edgeLabelBackground": "#1e293b",
            "actorBkg": "#0f172a",
            "actorBorder": "#6366f1",
            "actorTextColor": "#f8fafc",
            "fontFamily": "Segoe UI, Roboto, -apple-system, BlinkMacSystemFont, sans-serif",
            "fontSize": "13px"
        }
    },
    "modern-dark": {
        "theme": "base",
        "themeVariables": {
            "darkMode": True,
            "background": "transparent",
            "mainBkg": "#090d16",
            "nodeBorder": "#8b5cf6",
            "nodeTextColor": "#f1f5f9",
            "clusterBkg": "#0d1322",
            "clusterBorder": "#1e293b",
            "defaultLinkColor": "#38bdf8",
            "lineColor": "#38bdf8",
            "arrowheadColor": "#38bdf8",
            "titleColor": "#c4b5fd",
            "edgeLabelBackground": "#131b2e",
            "actorBkg": "#090d16",
            "actorBorder": "#8b5cf6",
            "actorTextColor": "#f1f5f9",
            "fontFamily": "Plus Jakarta Sans, JetBrains Mono, sans-serif",
            "fontSize": "13px"
        }
    },
    "corporate": {
        "theme": "base",
        "themeVariables": {
            "darkMode": False,
            "background": "transparent",
            "mainBkg": "#ffffff",
            "nodeBorder": "#2563eb",
            "nodeTextColor": "#0f172a",
            "clusterBkg": "#f8fafc",
            "clusterBorder": "#cbd5e1",
            "defaultLinkColor": "#1e3a8a",
            "lineColor": "#1e3a8a",
            "arrowheadColor": "#1e3a8a",
            "titleColor": "#1e3a8a",
            "edgeLabelBackground": "#ffffff",
            "actorBkg": "#ffffff",
            "actorBorder": "#2563eb",
            "actorTextColor": "#0f172a",
            "fontFamily": "IBM Plex Sans, sans-serif",
            "fontSize": "13px"
        }
    },
    "minimal": {
        "theme": "base",
        "themeVariables": {
            "darkMode": False,
            "background": "transparent",
            "mainBkg": "#ffffff",
            "nodeBorder": "#374151",
            "nodeTextColor": "#111827",
            "clusterBkg": "#fafafa",
            "clusterBorder": "#e5e7eb",
            "defaultLinkColor": "#111827",
            "lineColor": "#111827",
            "arrowheadColor": "#111827",
            "titleColor": "#111827",
            "edgeLabelBackground": "#ffffff",
            "actorBkg": "#ffffff",
            "actorBorder": "#374151",
            "actorTextColor": "#111827",
            "fontFamily": "Segoe UI, Arial, sans-serif",
            "fontSize": "13px"
        }
    }
}


def build_python_site(model_name: str | None = None, locale: str = "pt-BR") -> int:
    config = load_publication_config()
    target_model = (model_name or config.get("theme", {}).get("default_model", "glassmorphic")).lower().strip()
    norm_locale = normalize_locale(locale or "pt-BR")
    
    docs_dir = ROOT_DIR / "docs"
    dist_web = ROOT_DIR / "dist" / "webpage"
    images_dir = ROOT_DIR / "images"
    model_dir = ROOT_DIR / "models" / target_model
    
    if not model_dir.exists():
        model_dir = ROOT_DIR / "models" / "glassmorphic"

    # Clean existing webpage directory
    if dist_web.exists():
        for item in dist_web.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)
            except Exception:
                pass

    dist_web.mkdir(parents=True, exist_ok=True)
    
    # 1. Setup strictly Frontend, Backend, and Worker directories
    dist_frontend = dist_web / "frontend"
    dist_backend = dist_web / "backend"
    dist_worker = dist_web / "worker"
    
    dist_frontend.mkdir(parents=True, exist_ok=True)
    dist_backend.mkdir(parents=True, exist_ok=True)
    dist_worker.mkdir(parents=True, exist_ok=True)

    dist_data = dist_frontend / "data"
    dist_data.mkdir(parents=True, exist_ok=True)

    print("=================================================================")
    print(f"[DocShell] Python Web, Backend & Worker Generator")
    print(f"   Model       : {target_model}")
    print(f"   Locale      : {norm_locale}")
    print(f"   Frontend Dir: {dist_frontend}")
    print(f"   Backend Dir : {dist_backend}")
    print(f"   Worker Dir  : {dist_worker}")
    print("=================================================================")

    # 1. Copy images exclusively to frontend
    if images_dir.exists():
        dist_images = dist_frontend / "images"
        dist_images.mkdir(parents=True, exist_ok=True)
        for img_file in images_dir.glob("*"):
            if img_file.is_file():
                shutil.copy2(img_file, dist_images / img_file.name)
        print("  [OK] Images copied to dist/webpage/frontend/images/")

    # 2. Copy CSS and JS exclusively to frontend
    dist_assets = dist_frontend / "assets"
    dist_assets.mkdir(parents=True, exist_ok=True)
    
    css_file = model_dir / "web" / "style.css"
    js_file = model_dir / "web" / "script.js"
    if not js_file.exists():
        js_file = ROOT_DIR / "models" / "glassmorphic" / "web" / "script.js"
    
    if css_file.exists():
        shutil.copy2(css_file, dist_assets / "style.css")
    if js_file.exists():
        shutil.copy2(js_file, dist_assets / "script.js")

    # 3. Scan docs in base locale
    docs = scan_docs_directory(docs_dir, locale=norm_locale)

    # 4. Build Dataset (docs-i18n.json)
    # Only includes pt-BR base and verified completed translations from SQLite
    i18n_bundle = {
        "pt-BR": [
            {
                "slug": d["slug"],
                "section": d["section"],
                "title": d["title"],
                "body": d["body"],
                "html_body": parse_markdown_to_html(d["body"]),
                "is_translated": True
            }
            for d in docs
        ]
    }

    # Load any pre-cached completed translations from SQLite
    for loc in SUPPORTED_LOCALES:
        norm_loc = normalize_locale(loc)
        if norm_loc == "pt-BR":
            continue
        try:
            cached_trans = db.get_translations_for_locale(norm_loc)
            if len(cached_trans) >= len(docs):
                i18n_bundle[norm_loc] = [
                    {
                        "slug": t["slug"],
                        "section": t["section"],
                        "title": t["title"],
                        "body": t.get("body", ""),
                        "html_body": t.get("html_body") or parse_markdown_to_html(t.get("body", "")),
                        "is_translated": True
                    }
                    for t in cached_trans
                ]
        except Exception:
            pass
    
    i18n_json_path = dist_data / "docs-i18n.json"
    i18n_json_path.write_text(json.dumps(i18n_bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [OK] Language dataset generated: {i18n_json_path}")

    # 5. Populate Modular Backend Directory (dist/webpage/backend/)
    rag_dir = ROOT_DIR / "scripts" / "rag"
    if rag_dir.exists():
        for item in ["main.py", "app.py"]:
            src = rag_dir / item
            if src.exists():
                shutil.copy2(src, dist_backend / item)

        for folder in ["models", "routers", "services"]:
            src_f = rag_dir / folder
            dst_f = dist_backend / folder
            if src_f.exists():
                shutil.copytree(src_f, dst_f, dirs_exist_ok=True)

        # Copy core dependencies into backend
        core_src = ROOT_DIR / "scripts" / "core"
        core_dst = dist_backend / "scripts" / "core"
        if core_src.exists():
            shutil.copytree(core_src, core_dst, dirs_exist_ok=True)

        # Copy requirements.txt
        req_src = ROOT_DIR / "scripts" / "requirements.txt"
        if req_src.exists():
            shutil.copy2(req_src, dist_backend / "requirements.txt")

        # Copy publication config into backend for self-contained operation
        pub_src = ROOT_DIR / "publication"
        if pub_src.exists():
            shutil.copytree(pub_src, dist_backend / "publication", dirs_exist_ok=True)

        # Copy data folder into backend
        (dist_backend / "data").mkdir(parents=True, exist_ok=True)
        if (dist_frontend / "data").exists():
            shutil.copytree(dist_frontend / "data", dist_backend / "data", dirs_exist_ok=True)

        # Standalone Backend Dockerfile
        (dist_backend / "Dockerfile").write_text(
            """FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl sqlite3 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
ENV PYTHONPATH=/app \\
    PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
""",
            encoding="utf-8"
        )
        print(f"  [OK] Atomic Backend generated: {dist_backend}")

    # 6. Populate Dedicated Worker Directory (dist/webpage/worker/)
    worker_src_dir = ROOT_DIR / "scripts" / "worker"
    if (worker_src_dir / "worker.py").exists():
        shutil.copy2(worker_src_dir / "worker.py", dist_worker / "worker.py")
    elif (ROOT_DIR / "scripts" / "worker.py").exists():
        shutil.copy2(ROOT_DIR / "scripts" / "worker.py", dist_worker / "worker.py")

    req_src = ROOT_DIR / "scripts" / "requirements.txt"
    if req_src.exists():
        shutil.copy2(req_src, dist_worker / "requirements.txt")

    # Copy core & rag into worker for self-contained operation
    if (ROOT_DIR / "scripts" / "core").exists():
        shutil.copytree(ROOT_DIR / "scripts" / "core", dist_worker / "scripts" / "core", dirs_exist_ok=True)
    if (ROOT_DIR / "scripts" / "rag").exists():
        shutil.copytree(ROOT_DIR / "scripts" / "rag", dist_worker / "scripts" / "rag", dirs_exist_ok=True)
    if worker_src_dir.exists():
        shutil.copytree(worker_src_dir, dist_worker / "scripts" / "worker", dirs_exist_ok=True)

    pub_src = ROOT_DIR / "publication"
    if pub_src.exists():
        shutil.copytree(pub_src, dist_worker / "publication", dirs_exist_ok=True)
    (dist_worker / "data").mkdir(parents=True, exist_ok=True)
    if (dist_frontend / "data").exists():
        shutil.copytree(dist_frontend / "data", dist_worker / "data", dirs_exist_ok=True)

    # Copy publication config into dist_web root
    if pub_src.exists():
        shutil.copytree(pub_src, dist_web / "publication", dirs_exist_ok=True)

    # Standalone Worker Dockerfile
    (dist_worker / "Dockerfile").write_text(
        """FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl sqlite3 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir pika redis
COPY . /app
ENV PYTHONPATH=/app \\
    PYTHONUNBUFFERED=1 \\
    RABBITMQ_HOST=rabbitmq \\
    RABBITMQ_PORT=5672
CMD ["python", "worker.py"]
""",
        encoding="utf-8"
    )
    print(f"  [OK] Dedicated Worker generated: {dist_worker}")

    # 7. Frontend Dockerfile & Nginx Conf
    nginx_conf_src = ROOT_DIR / "scripts" / "docker" / "nginx.conf"
    if nginx_conf_src.exists():
        shutil.copy2(nginx_conf_src, dist_frontend / "nginx.conf")
    else:
        (dist_frontend / "nginx.conf").write_text(
            """server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /ws/ {
        proxy_pass http://backend:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
""",
            encoding="utf-8"
        )

    (dist_frontend / "Dockerfile").write_text(
        """FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
""",
        encoding="utf-8"
    )

    # 8. Standalone Docker Compose for Portable Distribution
    standalone_compose = dist_web / "docker-compose.yml"
    standalone_compose.write_text(
        """# ==============================================================================
# DocShell Standalone Distribution Stack
# Run 'docker compose up -d' from within this folder to start the complete stack.
# ==============================================================================
name: docshell-standalone

services:
  ollama:
    image: ollama/ollama:latest
    container_name: docshell-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

  ollama-pull:
    image: ollama/ollama:latest
    container_name: docshell-ollama-pull
    depends_on:
      ollama:
        condition: service_started
    entrypoint: [ "/bin/sh", "-c" ]
    command:
      - |
        set -e
        until ollama list >/dev/null 2>&1; do sleep 2; done
        ollama pull llama3.2
        ollama pull translategemma || true
        ollama pull nomic-embed-text
    restart: "no"

  redis:
    image: redis:7-alpine
    container_name: docshell-redis
    ports:
      - "6379:6379"
    restart: unless-stopped

  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    container_name: docshell-rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    restart: unless-stopped

  mongo:
    image: mongo:7.0
    container_name: docshell-mongo
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: docshell
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: docshell-rag
    environment:
      SITE_ROOT: /site
      RAG_CACHE_DIR: /data/rag
      MONGO_HOST: mongo
      MONGO_PORT: 27017
      MONGO_DB_NAME: docshell
      MONGO_URI: mongodb://mongo:27017/docshell
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_PORT: 5672
      REDIS_HOST: redis
      REDIS_PORT: 6379
      OLLAMA_HOST: http://ollama:11434
      OLLAMA_MODEL: llama3.2
      OLLAMA_EMBED_MODEL: nomic-embed-text
      OLLAMA_TRANSLATE_MODEL: translategemma
    volumes:
      - ./frontend:/site:ro
      - rag_data:/data/rag
    depends_on:
      mongo:
        condition: service_started
      redis:
        condition: service_started
      rabbitmq:
        condition: service_started
      ollama:
        condition: service_started
    restart: unless-stopped

  worker:
    build:
      context: ./worker
      dockerfile: Dockerfile
    container_name: docshell-worker
    environment:
      MONGO_HOST: mongo
      MONGO_PORT: 27017
      MONGO_DB_NAME: docshell
      MONGO_URI: mongodb://mongo:27017/docshell
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_PORT: 5672
      REDIS_HOST: redis
      REDIS_PORT: 6379
      OLLAMA_HOST: http://ollama:11434
      OLLAMA_MODEL: llama3.2
      OLLAMA_TRANSLATE_MODEL: translategemma
    depends_on:
      mongo:
        condition: service_started
      rabbitmq:
        condition: service_started
      redis:
        condition: service_started
      ollama:
        condition: service_started
    restart: unless-stopped

  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: docshell-web
    ports:
      - "8000:80"
    depends_on:
      backend:
        condition: service_started
    restart: unless-stopped

volumes:
  ollama_data:
  rag_data:
  mongo_data:
""",
        encoding="utf-8"
    )

    # 9. Standalone README.md in dist/webpage/ (English technical standard)
    (dist_web / "README.md").write_text(
        """# 🐚 DocShell - Standalone Web Documentation Package

This directory contains a complete, self-contained standalone package generated by DocShell.

## 🚀 How to Run with Docker (Recommended)

Simply open a terminal in this directory and run:

```bash
docker compose up -d
```

The documentation website will be available at: **http://localhost:8000**

## 📂 Package Directory Structure
- `frontend/`: Static HTML, CSS styles, JavaScript assets, images, and full-text search index.
- `backend/`: FastAPI API Gateway with RAG engine, WebSocket streaming, and documentation endpoints.
- `worker/`: Background translation task worker with RabbitMQ orchestrator and TranslateGemma.
- `docker-compose.yml`: Multi-container orchestrator configured for standalone execution.
""",
        encoding="utf-8"
    )
    print(f"  [OK] Standalone Docker stack generated in: {dist_web}")

    # 5. Build Sidebar navigation
    sidebar_items = []
    sections = {}
    for doc in docs:
        sec = doc["section"]
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(doc)

    is_first_nav = True
    for sec_name, sec_docs in sections.items():
        sidebar_items.append(f'<div class="sidebar-section-title">{html.escape(sec_name)}</div>')
        sidebar_items.append('<ul class="sidebar-nav">')
        for d in sec_docs:
            active_cls = " active" if is_first_nav else ""
            sidebar_items.append(f'<li class="sidebar-nav-item"><a href="#{d["slug"]}" class="sidebar-nav-link{active_cls}">{html.escape(d["title"])}</a></li>')
            is_first_nav = False
        sidebar_items.append('</ul>')
    sidebar_str = "\n".join(sidebar_items)

    # 6. Build Content cards with .doc-card-body wrapper for dynamic translation
    content_cards_html = []
    for doc in docs:
        card_html = parse_markdown_to_html(doc["body"])
        content_cards_html.append(f'''
        <section id="{doc['slug']}" class="content-card">
            <div class="content-card-header">
                <span class="badge-tag">{html.escape(doc['section'])}</span>
                <span class="content-path">{html.escape(doc['relative_path'])}</span>
            </div>
            <div class="doc-card-body">
                {card_html}
            </div>
        </section>
        ''')
    content_str = "\n".join(content_cards_html)

    # Build Locale selector options with HTML entities
    locale_options = [
        '<option value="pt-BR" selected>&#127463;&#127479; Portugu&ecirc;s</option>',
        '<option value="en-US">&#127482;&#127480; English</option>',
        '<option value="es">&#127466;&#127480; Espa&ntilde;ol</option>',
        '<option value="fr">&#127467;&#127479; Fran&ccedil;ais</option>',
        '<option value="de">&#127465;&#127466; Deutsch</option>',
        '<option value="it">&#127470;&#127481; Italiano</option>',
        '<option value="zh-CN">&#127464;&#127475; &#31616;&#20307;&#20013;&#25991;</option>',
        '<option value="ja">&#127471;&#127477; &#26085;&#26412;&#35486;</option>',
        '<option value="ru">&#127479;&#127482; &#1056;&#1091;&#1089;&#1089;&#1082;&#1080;&#1081;</option>',
    ]
    locale_options_str = "\n                ".join(locale_options)

    title = get_ui_string("doc_title", norm_locale)
    subtitle = get_ui_string("doc_subtitle", norm_locale)
    release = config.get("document", {}).get("release", "v1.0")
    nav_title = get_ui_string("navigation", norm_locale)
    docs_loaded_lbl = get_ui_string("documents_loaded", norm_locale)
    search_lbl = get_ui_string("search_placeholder", norm_locale)
    ai_btn_lbl = get_ui_string("ai_assistant", norm_locale)
    ai_greeting_lbl = get_ui_string("ai_greeting", norm_locale)

    mermaid_cfg = MERMAID_THEMES.get(target_model, MERMAID_THEMES["glassmorphic"])
    mermaid_init_dict = {
        "startOnLoad": True,
        "securityLevel": "loose",
        **mermaid_cfg
    }
    mermaid_init_js = json.dumps(mermaid_init_dict, indent=2)

    # 7. HTML Template
    html_template = f'''<!DOCTYPE html>
<html lang="{norm_locale}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - {html.escape(release)}</title>
    <meta name="description" content="{html.escape(subtitle)}">
    <link rel="stylesheet" href="assets/style.css">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        if (typeof mermaid !== 'undefined') {{
            mermaid.initialize({mermaid_init_js});
        }}
    </script>
</head>
<body>
    <!-- Top Navigation Header (Organism: Header) -->
    <header class="doc-header organism-header">
        <a href="#" class="brand-container molecule-brand">
            <img src="https://glass-hub-engine.vercel.app/api/logo?project=docshell&animated=true&width=40&height=40" alt="GlassHub DocShell Logo" class="brand-logo atom-logo" onerror="this.src='images/logo.svg'">
            <span class="brand-title">GlassHub <span>DocShell</span></span>
            <span class="badge-tag atom-badge">{html.escape(release)}</span>
        </a>
        
        <div class="search-container molecule-search">
            <span class="search-icon">&#128269;</span>
            <input type="text" id="docSearchInput" class="search-input atom-input" placeholder="{html.escape(search_lbl)}">
        </div>

        <div class="header-actions molecule-actions">
            <!-- 9-Language Selector -->
            <select id="docLocaleSelector" class="locale-select atom-select" title="Select Language">
                {locale_options_str}
            </select>
            <span style="font-size:0.85rem; color:var(--text-secondary);">Runtime: <strong>Python</strong></span>
        </div>
    </header>

    <!-- Main Docs Layout -->
    <div class="doc-wrapper">
        <aside class="doc-sidebar">
            <div style="margin-bottom:1.5rem;">
                <h3 id="navTitle" style="font-size:1.1rem; color:#fff; font-weight:700;">{html.escape(nav_title)}</h3>
                <p style="font-size:0.8rem; color:var(--text-muted);">{len(docs)} {html.escape(docs_loaded_lbl)}</p>
            </div>
            {sidebar_str}
        </aside>

        <main class="doc-main">
            {content_str}
        </main>
    </div>

    <!-- Floating AI Assistant Widget -->
    <div class="ai-assistant-widget">
        <button id="aiToggleBtn" class="ai-toggle-btn">
            <span>{html.escape(ai_btn_lbl)}</span>
        </button>

        <div id="aiChatBox" class="ai-chat-box hidden">
            <div class="ai-chat-header">
                <div class="ai-chat-title">
                    <span class="ai-status-indicator"></span>
                    <span>DocShell AI Assistant</span>
                </div>
                <div class="ai-chat-header-actions" style="display:flex; align-items:center; gap:6px;">
                    <button id="aiClearBtn" class="ai-chat-clear" title="Limpar conversa" style="background:none; border:none; color:#94a3b8; cursor:pointer; font-size:14px; padding:3px 6px; border-radius:4px; transition:color 0.2s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='#94a3b8'">🗑️</button>
                    <button id="aiCloseBtn" class="ai-chat-close">&times;</button>
                </div>
            </div>
            <div id="aiMessages" class="ai-chat-messages">
                <div class="chat-msg assistant">
                    {html.escape(ai_greeting_lbl)}
                </div>
            </div>
            <div class="ai-chat-input-area">
                <input type="text" id="aiChatInput" class="ai-chat-input" placeholder="Faça uma pergunta sobre a documentação...">
                <button id="aiSendBtn" class="ai-chat-send">&#10148;</button>
            </div>
        </div>
    </div>

    <script src="assets/script.js"></script>
</body>
</html>'''

    index_html = dist_frontend / "index.html"
    index_html.write_text(html_template, encoding="utf-8")
    print(f"  [OK] Website generated successfully: {index_html}")

    # 8. Search Index
    search_index = build_search_and_rag_index(docs, ROOT_DIR)
    (dist_frontend / "data" / "search_index.json").write_text(json.dumps(search_index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [OK] Search index updated in dist/webpage/frontend/data/search_index.json")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DocShell Python Web Builder")
    parser.add_argument("-m", "--model", help="Theme model (glassmorphic, corporate, modern-dark, minimal)", default=None)
    parser.add_argument("-l", "--locale", help="Target locale (pt-BR, en-US, es, fr, de, it, zh-CN, ja, ru)", default="pt-BR")
    args = parser.parse_args()
    sys.exit(build_python_site(args.model, locale=args.locale))
