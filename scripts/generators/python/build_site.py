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
from scripts.core.translator import SUPPORTED_LOCALES, get_ui_string, normalize_locale, translate_document_content


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
    dist_data = dist_web / "data"
    dist_data.mkdir(parents=True, exist_ok=True)

    print("=================================================================")
    print(f"[DocShell] Python Web Generator")
    print(f"   Model       : {target_model}")
    print(f"   Locale      : {norm_locale}")
    print(f"   Destination : {dist_web}")
    print("=================================================================")

    # 1. Copy images
    if images_dir.exists():
        dist_images = dist_web / "images"
        dist_images.mkdir(parents=True, exist_ok=True)
        for img_file in images_dir.glob("*"):
            if img_file.is_file():
                shutil.copy2(img_file, dist_images / img_file.name)
        print("  [OK] Images copied to dist/webpage/images/")

    # 2. Copy CSS and JS
    dist_assets = dist_web / "assets"
    dist_assets.mkdir(parents=True, exist_ok=True)
    
    css_file = model_dir / "web" / "style.css"
    js_file = model_dir / "web" / "script.js"
    
    if css_file.exists():
        shutil.copy2(css_file, dist_assets / "style.css")
    if js_file.exists():
        shutil.copy2(js_file, dist_assets / "script.js")

    # 3. Scan docs in base locale
    docs = scan_docs_directory(docs_dir, locale=norm_locale)

    # 4. Build Base Dataset (docs-i18n.json) containing original pt-BR docs
    i18n_bundle = {
        "pt-BR": [
            {
                "slug": d["slug"],
                "section": d["section"],
                "title": d["title"],
                "body": d["body"],
                "html_body": parse_markdown_to_html(d["body"])
            }
            for d in docs
        ]
    }
    
    i18n_json_path = dist_data / "docs-i18n.json"
    i18n_json_path.write_text(json.dumps(i18n_bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [OK] Base language dataset (pt-BR) generated: {i18n_json_path}")

    # 5. Build Sidebar navigation
    sidebar_items = []
    sections = {}
    for doc in docs:
        sec = doc["section"]
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(doc)

    for sec_name, sec_docs in sections.items():
        sidebar_items.append(f'<div class="sidebar-section-title">{html.escape(sec_name)}</div>')
        sidebar_items.append('<ul class="sidebar-nav">')
        for d in sec_docs:
            sidebar_items.append(f'<li class="sidebar-nav-item"><a href="#{d["slug"]}" class="sidebar-nav-link">{html.escape(d["title"])}</a></li>')
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

    # 7. HTML Template
    html_template = f'''<!DOCTYPE html>
<html lang="{norm_locale}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - {html.escape(release)}</title>
    <meta name="description" content="{html.escape(subtitle)}">
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <!-- Top Navigation Header -->
    <header class="doc-header">
        <a href="#" class="brand-container">
            <img src="images/logo.svg" alt="Logo" class="brand-logo" onerror="this.style.display='none'">
            <span class="brand-title">Doc<span>Shell</span></span>
            <span class="badge-tag">{html.escape(release)}</span>
        </a>
        
        <div class="search-container">
            <span class="search-icon">&#128269;</span>
            <input type="text" id="docSearchInput" class="search-input" placeholder="{html.escape(search_lbl)}">
        </div>

        <div class="header-actions">
            <!-- 9-Language Selector -->
            <select id="docLocaleSelector" class="locale-select" title="Select Language">
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
                <button id="aiCloseBtn" class="ai-chat-close">&times;</button>
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

    index_html = dist_web / "index.html"
    index_html.write_text(html_template, encoding="utf-8")
    print(f"  [OK] Website generated successfully: {index_html}")

    # 8. Search Index
    search_index = build_search_and_rag_index(docs, ROOT_DIR)
    (dist_web / "search_index.json").write_text(json.dumps(search_index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [OK] Search index updated in dist/webpage/search_index.json")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DocShell Python Web Builder")
    parser.add_argument("-m", "--model", help="Theme model (glassmorphic, corporate, modern-dark, minimal)", default=None)
    parser.add_argument("-l", "--locale", help="Target locale (pt-BR, en-US, es, fr, de, it, zh-CN, ja, ru)", default="pt-BR")
    args = parser.parse_args()
    sys.exit(build_python_site(args.model, locale=args.locale))
