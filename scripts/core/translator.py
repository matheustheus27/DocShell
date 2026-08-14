#!/usr/bin/env python3
"""
DocShell Core - Translation and Localization Engine (TranslateGemma / Ollama)
Provides multi-language translation and localization across 9 languages:
- pt-BR (Português)
- en-US (English)
- es (Español)
- fr (Français)
- de (Deutsch)
- it (Italiano)
- zh-CN (中文)
- ja (日本語)
- ru (Русский)

Connects to local Ollama instance (e.g., TranslateGemma / Gemma2 / LLaMA3.2)
with local cache in publication/translations_cache.json and built-in UI dictionaries.
"""

import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, Optional

def _resolve_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent

ROOT_DIR = _resolve_root()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Supported Locales Map
SUPPORTED_LOCALES = {
    "pt-BR": {"name": "Português (Brasil)", "native": "Português", "flag": "🇧🇷"},
    "en-US": {"name": "English (US)", "native": "English", "flag": "🇺🇸"},
    "es": {"name": "Spanish", "native": "Español", "flag": "🇪🇸"},
    "fr": {"name": "French", "native": "Français", "flag": "🇫🇷"},
    "de": {"name": "German", "native": "Deutsch", "flag": "🇩🇪"},
    "it": {"name": "Italian", "native": "Italiano", "flag": "🇮🇹"},
    "zh-CN": {"name": "Chinese (Simplified)", "native": "简体中文", "flag": "🇨🇳"},
    "ja": {"name": "Japanese", "native": "日本語", "flag": "🇯🇵"},
    "ru": {"name": "Russian", "native": "Русский", "flag": "🇷🇺"},
}

# Pre-defined UI Translation Dictionary
UI_DICTIONARY: Dict[str, Dict[str, str]] = {
    "pt-BR": {
        "doc_title": "DocShell - Documentação Técnica",
        "doc_subtitle": "Guia de Arquitetura e Engenharia do Sistema",
        "toc": "Sumário Executivo",
        "navigation": "Navegação",
        "documents_loaded": "documentos carregados",
        "search_placeholder": "Pesquisar documentação (Ctrl+K)...",
        "runtime": "Ambiente de Execução",
        "ai_assistant": "Assistente IA",
        "ai_greeting": "Olá! Sou o assistente de IA do DocShell. Faça qualquer pergunta sobre arquitetura, comandos, temas ou instalação!",
        "ai_input_placeholder": "Faça uma pergunta sobre a documentação...",
        "send": "Enviar",
        "version": "Versão",
        "author": "Autor",
        "organization": "Organização",
        "classification": "Classificação",
        "property": "Propriedade",
        "specification": "Especificação",
        "compiled_docs": "Documentos Compilados",
        "close": "Fechar",
        "language": "Idioma",
    },
    "en-US": {
        "doc_title": "DocShell - Technical Documentation",
        "doc_subtitle": "Architecture and System Engineering Guide",
        "toc": "Table of Contents",
        "navigation": "Navigation",
        "documents_loaded": "documents loaded",
        "search_placeholder": "Search documentation (Ctrl+K)...",
        "runtime": "Runtime",
        "ai_assistant": "AI Assistant",
        "ai_greeting": "Hello! I am your AI assistant for DocShell documentation. Ask any question about architecture, commands, themes, or deployment!",
        "ai_input_placeholder": "Ask a question about the docs...",
        "send": "Send",
        "version": "Version",
        "author": "Author",
        "organization": "Organization",
        "classification": "Classification",
        "property": "Property",
        "specification": "Specification",
        "compiled_docs": "Compiled Documents",
        "close": "Close",
        "language": "Language",
    },
    "es": {
        "doc_title": "DocShell - Documentación Técnica",
        "doc_subtitle": "Guía de Arquitectura e Ingeniería del Sistema",
        "toc": "Índice de Contenidos",
        "navigation": "Navegación",
        "documents_loaded": "documentos cargados",
        "search_placeholder": "Buscar en la documentación (Ctrl+K)...",
        "runtime": "Entorno",
        "ai_assistant": "Asistente IA",
        "ai_greeting": "¡Hola! Soy tu asistente de IA para la documentación de DocShell. ¡Pregunta lo que quieras sobre arquitectura, comandos o temas!",
        "ai_input_placeholder": "Haz una pregunta sobre los documentos...",
        "send": "Enviar",
        "version": "Versión",
        "author": "Autor",
        "organization": "Organización",
        "classification": "Clasificación",
        "property": "Propiedad",
        "specification": "Especificación",
        "compiled_docs": "Documentos Compilados",
        "close": "Cerrar",
        "language": "Idioma",
    },
    "fr": {
        "doc_title": "DocShell - Documentation Technique",
        "doc_subtitle": "Guide d'Architecture et d'Ingénierie Système",
        "toc": "Table des Matières",
        "navigation": "Navigation",
        "documents_loaded": "documents chargés",
        "search_placeholder": "Rechercher dans la documentation (Ctrl+K)...",
        "runtime": "Environnement",
        "ai_assistant": "Assistant IA",
        "ai_greeting": "Bonjour ! Je suis votre assistant IA pour la documentation DocShell. Posez vos questions sur l'architecture, les commandes ou les thèmes !",
        "ai_input_placeholder": "Posez une question sur la documentation...",
        "send": "Envoyer",
        "version": "Version",
        "author": "Auteur",
        "organization": "Organisation",
        "classification": "Classification",
        "property": "Propriété",
        "specification": "Spécification",
        "compiled_docs": "Documents Compilés",
        "close": "Fermer",
        "language": "Langue",
    },
    "de": {
        "doc_title": "DocShell - Technische Dokumentation",
        "doc_subtitle": "Architektur- und Systemtechnik-Leitfaden",
        "toc": "Inhaltsverzeichnis",
        "navigation": "Navigation",
        "documents_loaded": "Dokumente geladen",
        "search_placeholder": "Dokumentation durchsuchen (Strg+K)...",
        "runtime": "Laufzeitumgebung",
        "ai_assistant": "KI-Assistent",
        "ai_greeting": "Hallo! Ich bin Ihr KI-Assistent für DocShell. Stellen Sie beliebige Fragen zu Architektur, Befehlen oder Themes!",
        "ai_input_placeholder": "Frage zur Dokumentation stellen...",
        "send": "Senden",
        "version": "Version",
        "author": "Autor",
        "organization": "Organisation",
        "classification": "Klassifizierung",
        "property": "Eigenschaft",
        "specification": "Spezifikation",
        "compiled_docs": "Kompilierte Dokumente",
        "close": "Schließen",
        "language": "Sprache",
    },
    "it": {
        "doc_title": "DocShell - Documentazione Tecnica",
        "doc_subtitle": "Guida all'Architettura e all'Ingegneria di Sistema",
        "toc": "Indice dei Contenuti",
        "navigation": "Navigazione",
        "documents_loaded": "documenti caricati",
        "search_placeholder": "Cerca nella documentazione (Ctrl+K)...",
        "runtime": "Runtime",
        "ai_assistant": "Assistente IA",
        "ai_greeting": "Ciao! Sono l'assistente IA di DocShell. Fai qualsiasi domanda su architettura, comandi o temi!",
        "ai_input_placeholder": "Fai una domanda sulla documentazione...",
        "send": "Invia",
        "version": "Versione",
        "author": "Autore",
        "organization": "Organizzazione",
        "classification": "Classificazione",
        "property": "Proprietà",
        "specification": "Specifica",
        "compiled_docs": "Documenti Compilati",
        "close": "Chiudi",
        "language": "Lingua",
    },
    "zh-CN": {
        "doc_title": "DocShell - 技术文档",
        "doc_subtitle": "系统架构与工程指南",
        "toc": "目录",
        "navigation": "导航",
        "documents_loaded": "个文档已加载",
        "search_placeholder": "搜索文档 (Ctrl+K)...",
        "runtime": "运行环境",
        "ai_assistant": "AI 助手",
        "ai_greeting": "您好！我是 DocShell 文档 AI 助手。欢迎随时询问关于系统架构、命令、主题或部署的问题！",
        "ai_input_placeholder": "输入关于文档的问题...",
        "send": "发送",
        "version": "版本",
        "author": "作者",
        "organization": "组织机构",
        "classification": "密级",
        "property": "属性",
        "specification": "规格说明",
        "compiled_docs": "已编译文档数",
        "close": "关闭",
        "language": "语言",
    },
    "ja": {
        "doc_title": "DocShell - 技術ドキュメント",
        "doc_subtitle": "システムアーキテクチャおよびエンジニアリングガイド",
        "toc": "目次",
        "navigation": "ナビゲーション",
        "documents_loaded": "件のドキュメントを読み込みました",
        "search_placeholder": "ドキュメントを検索 (Ctrl+K)...",
        "runtime": "ランタイム",
        "ai_assistant": "AI アシスタント",
        "ai_greeting": "こんにちは！DocShell ドキュメント AI アシスタントです。アーキテクチャやコマンド、テーマについて何でもお聞きください！",
        "ai_input_placeholder": "ドキュメントについて質問する...",
        "send": "送信",
        "version": "バージョン",
        "author": "作成者",
        "organization": "組織",
        "classification": "区分",
        "property": "項目",
        "specification": "仕様",
        "compiled_docs": "コンパイル済み文書数",
        "close": "閉じる",
        "language": "言語",
    },
    "ru": {
        "doc_title": "DocShell - Техническая Документация",
        "doc_subtitle": "Руководство по архитектуре и системной инженерии",
        "toc": "Содержание",
        "navigation": "Навигация",
        "documents_loaded": "документов загружено",
        "search_placeholder": "Поиск по документации (Ctrl+K)...",
        "runtime": "Среда выполнения",
        "ai_assistant": "ИИ-Ассистент",
        "ai_greeting": "Здравствуйте! Я ИИ-ассистент документации DocShell. Задавайте любые вопросы по архитектуре, командам и темам оформления!",
        "ai_input_placeholder": "Задайте вопрос по документации...",
        "send": "Отправить",
        "version": "Версия",
        "author": "Автор",
        "organization": "Организация",
        "classification": "Классификация",
        "property": "Свойство",
        "specification": "Спецификация",
        "compiled_docs": "Скомпилированных документов",
        "close": "Закрыть",
        "language": "Язык",
    }
}


def normalize_locale(locale: Optional[str]) -> str:
    """Normalizes locale identifier to standard keys (e.g., pt -> pt-BR, zh -> zh-CN)."""
    if not locale:
        return "en-US"
    clean = locale.strip().replace("_", "-")
    clean_lower = clean.lower()
    
    mapping = {
        "pt": "pt-BR", "pt-br": "pt-BR", "portugues": "pt-BR", "portuguese": "pt-BR",
        "en": "en-US", "en-us": "en-US", "english": "en-US",
        "es": "es", "es-es": "es", "spanish": "es", "espanol": "es",
        "fr": "fr", "fr-fr": "fr", "french": "fr", "francais": "fr",
        "de": "de", "de-de": "de", "german": "de", "deutsch": "de",
        "it": "it", "it-it": "it", "italian": "it", "italiano": "it",
        "zh": "zh-CN", "zh-cn": "zh-CN", "zh-ch": "zh-CN", "chinese": "zh-CN",
        "ja": "ja", "ja-jp": "ja", "japanese": "ja",
        "ru": "ru", "ru-ru": "ru", "russian": "ru"
    }
    return mapping.get(clean_lower, "en-US")


def get_ui_string(key: str, locale: str = "en-US") -> str:
    """Retrieves localized UI text string for a given key."""
    norm = normalize_locale(locale)
    loc_dict = UI_DICTIONARY.get(norm, UI_DICTIONARY["en-US"])
    return loc_dict.get(key, UI_DICTIONARY["en-US"].get(key, key))


# Pre-defined Section Translation Dictionary (0-LLM overhead, 100% reliable)
SECTION_DICTIONARY: Dict[str, Dict[str, str]] = {
    "pt-BR": {
        "general": "Geral",
        "arquitetura": "Arquitetura",
        "guia de uso": "Guia de Uso",
        "ia e rag": "IA e RAG",
        "docker": "Docker",
        "conclusao": "Conclusão",
        "conclusão": "Conclusão",
    },
    "en-US": {
        "general": "General",
        "arquitetura": "Architecture",
        "guia de uso": "User Guide",
        "ia e rag": "AI & RAG",
        "docker": "Docker",
        "conclusao": "Conclusion",
        "conclusão": "Conclusion",
    },
    "es": {
        "general": "General",
        "arquitetura": "Arquitectura",
        "guia de uso": "Guía de Uso",
        "ia e rag": "IA y RAG",
        "docker": "Docker",
        "conclusao": "Conclusión",
        "conclusão": "Conclusión",
    },
    "fr": {
        "general": "Général",
        "arquitetura": "Architecture",
        "guia de uso": "Guide d'Utilisation",
        "ia e rag": "IA et RAG",
        "docker": "Docker",
        "conclusao": "Conclusion",
        "conclusão": "Conclusion",
    },
    "de": {
        "general": "Allgemein",
        "arquitetura": "Architektur",
        "guia de uso": "Benutzerhandbuch",
        "ia e rag": "KI & RAG",
        "docker": "Docker",
        "conclusao": "Fazit",
        "conclusão": "Fazit",
    },
    "it": {
        "general": "Generale",
        "arquitetura": "Architettura",
        "guia de uso": "Guida all'Uso",
        "ia e rag": "IA e RAG",
        "docker": "Docker",
        "conclusao": "Conclusione",
        "conclusão": "Conclusione",
    },
    "zh-CN": {
        "general": "概述",
        "arquitetura": "系统架构",
        "guia de uso": "使用指南",
        "ia e rag": "人工智能与 RAG",
        "docker": "Docker 容器",
        "conclusao": "结论与展望",
        "conclusão": "结论与展望",
    },
    "ja": {
        "general": "概要",
        "arquitetura": "アーキテクチャ",
        "guia de uso": "利用ガイド",
        "ia e rag": "AI と RAG",
        "docker": "Docker",
        "conclusao": "まとめ",
        "conclusão": "まとめ",
    },
    "ru": {
        "general": "Общее",
        "arquitetura": "Архитектура",
        "guia de uso": "Руководство пользователя",
        "ia e rag": "ИИ и RAG",
        "docker": "Docker",
        "conclusao": "Заключение",
        "conclusão": "Заключение",
    }
}


def translate_section(section_name: str, target_locale: str = "en-US") -> str:
    """Translates standard documentation section names without LLM overhead."""
    norm = normalize_locale(target_locale)
    sec_key = (section_name or "").strip().lower()
    
    loc_dict = SECTION_DICTIONARY.get(norm, SECTION_DICTIONARY.get("en-US", {}))
    if sec_key in loc_dict:
        return loc_dict[sec_key]
    
    return section_name


def sanitize_translation_output(raw_text: str, original_input: str) -> str:
    """
    Cleans up LLM translation responses by stripping prompt echoes, preamble, and markdown fences.
    """
    if not raw_text:
        return original_input

    text = raw_text.strip()

    # 1. If LLM echoed prompt headers or markers, extract only the content after
    markers = [
        "Content to translate:",
        "Markdown content to translate:",
        "Content:",
        "TRANSLATED TEXT:",
        "Translated text:",
        "Translation:",
        "Here is the translation:",
        "Here is the translated text:",
        "Here is the translated Markdown:",
        "Here's the translation:",
        "--- START DOCUMENT ---",
        "--- END DOCUMENT ---",
    ]
    for marker in markers:
        if marker in text:
            parts = text.split(marker)
            candidate = parts[-1].strip()
            if candidate and "CRITICAL RULES" not in candidate:
                text = candidate

    # 2. If it still contains "CRITICAL RULES:" or prompt artifacts
    if "CRITICAL RULES" in text or "You are a professional technical documentation translator" in text or "Preserve ALL Markdown" in text:
        if len(original_input.strip()) < 100:
            return original_input
        clean_lines = []
        for line in text.splitlines():
            line_str = line.strip()
            if any(k in line_str for k in ["CRITICAL RULES:", "You are a professional", "Preserve ALL Markdown", "Keep all HTML tags", "Return ONLY the", "Content to translate:"]):
                continue
            if line_str.startswith("1. Preserve") or line_str.startswith("2. Keep") or line_str.startswith("3. Return"):
                continue
            clean_lines.append(line)
        text = "\n".join(clean_lines).strip()

    # 3. Strip wrapping markdown code blocks if the entire response was fenced
    fence_match = re.match(r"^```(?:markdown|md)?\s*\n(.*?)\n```$", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    # 4. Length anomaly check for short inputs (titles/sections)
    if len(original_input.strip()) < 60 and len(text) > (len(original_input) * 4) and ("\n" in text):
        first_line = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#") and "CRITICAL" not in l]
        if first_line:
            text = first_line[0]
        else:
            text = original_input

    return text.strip() if text.strip() else original_input


def is_ollama_available(host: Optional[str] = None) -> bool:
    """Checks if Ollama daemon is reachable."""
    target_host = (host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")).rstrip("/")
    try:
        req = urllib.request.Request(f"{target_host}/api/tags", headers={"User-Agent": "DocShell"})
        with urllib.request.urlopen(req, timeout=2.5) as response:
            return response.status == 200
    except Exception:
        return False


def get_available_ollama_models(host: Optional[str] = None) -> list:
    """Discovers installed models in Ollama."""
    target_host = (host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")).rstrip("/")
    try:
        req = urllib.request.Request(f"{target_host}/api/tags", headers={"User-Agent": "DocShell"})
        with urllib.request.urlopen(req, timeout=2.5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return [m.get("name") for m in data.get("models", []) if m.get("name")]
    except Exception:
        pass
    return []


def query_ollama_translate(
    text: str,
    target_locale: str,
    source_locale: str = "pt-BR",
    host: Optional[str] = None,
    model: Optional[str] = None
) -> Optional[str]:
    """
    Calls Ollama TranslateGemma / LLM to translate markdown text while preserving code blocks, tags, and formatting.
    Supports automatic multi-model fallback and prompt sanitization.
    """
    target_host = (host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")).rstrip("/")
    target_lang_name = SUPPORTED_LOCALES.get(target_locale, {}).get("name", target_locale)
    
    prompt = (
        f"Translate the following technical documentation Markdown text from {source_locale} into {target_lang_name} ({target_locale}).\n"
        f"Rules: Preserve all Markdown formatting, headings, bullet lists, bold, tables, HTML tags, anchor IDs, image paths, and code blocks untouched.\n"
        f"Output ONLY the translated Markdown text without any preamble, instructions, or notes.\n\n"
        f"--- START TEXT ---\n{text}\n--- END TEXT ---"
    )

    models_to_try = []
    preferred = model or os.getenv("OLLAMA_TRANSLATE_MODEL", "translategemma")
    fallback = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    for m in [preferred, fallback, "translategemma", "llama3.2", "gemma2", "mistral"]:
        if m and m not in models_to_try:
            models_to_try.append(m)

    # Add any other locally available models
    installed = get_available_ollama_models(target_host)
    for inst in installed:
        if inst not in models_to_try:
            models_to_try.append(inst)

    for m in models_to_try:
        payload = {
            "model": m,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2}
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{target_host}/api/generate",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60.0) as response:
                if response.status == 200:
                    res_body = json.loads(response.read().decode("utf-8"))
                    result_text = res_body.get("response", "").strip()
                    if result_text:
                        cleaned = sanitize_translation_output(result_text, text)
                        if cleaned:
                            return cleaned
        except Exception:
            continue

    return None


def load_translations_cache(root_dir: Optional[Path] = None) -> Dict[str, str]:
    if root_dir is None:
        root_dir = ROOT_DIR
    cache_file = Path(root_dir) / "publication" / "translations_cache.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_translations_cache(arg1: Any, arg2: Any = None) -> None:
    if isinstance(arg1, dict):
        cache, root_dir = arg1, arg2 or ROOT_DIR
    else:
        root_dir, cache = arg1 or ROOT_DIR, arg2 or {}
    pub_dir = Path(root_dir) / "publication"
    pub_dir.mkdir(parents=True, exist_ok=True)
    cache_file = pub_dir / "translations_cache.json"
    try:
        cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def translate_text(
    text: str,
    target_locale: str,
    source_locale: str = "pt-BR",
    root_dir: Optional[Path] = None,
    ollama_host: Optional[str] = None,
    ollama_model: Optional[str] = None
) -> str:
    """
    Main translation entry point with Redis/disk cache lookup and Ollama TranslateGemma integration.
    """
    target = normalize_locale(target_locale)
    source = normalize_locale(source_locale)

    if target == source or not text or not text.strip():
        return text

    if root_dir is None:
        root_dir = ROOT_DIR

    clean_text = text.strip()

    # Check if this is a single word or standard section name
    if len(clean_text) < 30 and clean_text.lower() in SECTION_DICTIONARY.get("pt-BR", {}):
        return translate_section(clean_text, target)

    text_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()[:16]

    # 1. Try Redis cache via cache_manager if available
    try:
        from scripts.core.cache_manager import cache_manager
        cached_val = cache_manager.get_translation(source, target, text_hash)
        if cached_val and not cache_manager._is_poisoned_text(cached_val):
            return cached_val
    except Exception:
        pass

    # 2. Try disk cache
    cache = load_translations_cache(root_dir)
    cache_key = f"{source}->{target}:{text_hash}"
    if cache_key in cache:
        val = cache[cache_key]
        if "CRITICAL RULES" not in val:
            return val

    # 3. If Ollama is running, request dynamic translation
    target_host = ollama_host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    if is_ollama_available(target_host):
        translated = query_ollama_translate(
            clean_text, target, source, host=target_host, model=ollama_model
        )
        if translated and translated.strip():
            translated_clean = sanitize_translation_output(translated.strip(), clean_text)
            if "CRITICAL RULES" not in translated_clean:
                cache[cache_key] = translated_clean
                save_translations_cache(root_dir, cache)
                try:
                    from scripts.core.cache_manager import cache_manager
                    cache_manager.set_translation(source, target, text_hash, translated_clean)
                except Exception:
                    pass
                return translated_clean

    return text


translate_document_content = translate_text
