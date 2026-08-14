#!/usr/bin/env python3
"""
DocShell Core - Config Loader
Carrega configurações centrais de publication/publication.yml e tokens de tema.
"""

from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    yaml = None


def get_project_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent


def load_publication_config(custom_path: Path | None = None) -> Dict[str, Any]:
    root = get_project_root()
    yml_path = custom_path or (root / "publication" / "publication.yml")
    
    if not yml_path.exists():
        return get_default_config()

    raw_text = yml_path.read_text(encoding="utf-8")

    if yaml is not None:
        try:
            data = yaml.safe_load(raw_text)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # Fallback parser simples embutido (caso PyYAML não esteja instalado)
    return parse_yaml_fallback(raw_text)


def parse_yaml_fallback(raw: str) -> Dict[str, Any]:
    cfg: Dict[str, Any] = {
        "document": {
            "title": "DocShell - Documentação Técnica",
            "subtitle": "Guia de Arquitetura e Engenharia",
            "author": "Matheus Ferreira",
            "version": "1.0.0",
            "release": "v1.0",
            "language": "pt-BR",
            "output": {
                "pdf": {"enabled": True, "basename": "DocShell-Documentacao", "directory": "dist/pdf"},
                "website": {"enabled": True, "directory": "dist/webpage", "default_runtime": "python", "port": 8000}
            }
        },
        "metadata": {
            "organization": "DocShell Platform",
            "document_type": "Technical Specification",
            "classification": "Public"
        },
        "theme": {"default_model": "glassmorphic"},
        "ai_assistant": {"enabled": True, "provider": "ollama"}
    }

    m_title = re.search(r'title:\s*["\']?([^"\']+)["\']?', raw)
    if m_title:
        cfg["document"]["title"] = m_title.group(1).strip()

    m_sub = re.search(r'subtitle:\s*["\']?([^"\']+)["\']?', raw)
    if m_sub:
        cfg["document"]["subtitle"] = m_sub.group(1).strip()

    m_author = re.search(r'author:\s*["\']?([^"\']+)["\']?', raw)
    if m_author:
        cfg["document"]["author"] = m_author.group(1).strip()

    m_version = re.search(r'version:\s*["\']?([^"\']+)["\']?', raw)
    if m_version:
        cfg["document"]["version"] = m_version.group(1).strip()

    m_release = re.search(r'release:\s*["\']?([^"\']+)["\']?', raw)
    if m_release:
        cfg["document"]["release"] = m_release.group(1).strip()

    m_model = re.search(r'default_model:\s*["\']?([^"\']+)["\']?', raw)
    if m_model:
        cfg["theme"]["default_model"] = m_model.group(1).strip()

    return cfg


def get_default_config() -> Dict[str, Any]:
    return {
        "document": {
            "title": "DocShell",
            "subtitle": "Documentação Técnica",
            "author": "Autor",
            "version": "1.0.0",
            "release": "v1.0",
            "output": {"pdf": {"basename": "DocShell-Doc"}, "website": {"directory": "dist/webpage"}}
        },
        "theme": {"default_model": "glassmorphic"}
    }


def load_theme_model(model_name: str | None = None) -> Dict[str, Any]:
    root = get_project_root()
    cfg = load_publication_config()
    target_model = (model_name or cfg.get("theme", {}).get("default_model", "glassmorphic")).lower().strip()
    
    model_dir = root / "models" / target_model
    if not model_dir.exists():
        # Fallback para glassmorphic ou primeiro existente
        target_model = "glassmorphic"
        model_dir = root / "models" / "glassmorphic"

    json_path = model_dir / "model.json"
    if json_path.exists():
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {"id": target_model, "name": target_model.capitalize(), "tokens": {}}


if __name__ == "__main__":
    print("Project Root:", get_project_root())
    print("Loaded Config:", json.dumps(load_publication_config(), indent=2, ensure_ascii=False))
