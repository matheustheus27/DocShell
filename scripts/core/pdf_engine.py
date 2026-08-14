#!/usr/bin/env python3
"""
DocShell Core - PDF Compilation Engine
Uses Pandoc and XeLaTeX with customizable visual design models (Glassmorphic,
Corporate, Modern Dark, Minimal), Roboto font family, and multi-language support (9 locales).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

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
from scripts.core.doc_parser import scan_docs_directory, generate_consolidated_markdown
from scripts.core.translator import get_ui_string, normalize_locale


def write_pdf_meta(config: dict, output_path: Path, locale: str = "en-US"):
    """Writes LaTeX metadata definitions for document title, author, and versioning in target locale."""
    norm_locale = normalize_locale(locale)
    meta_cfg = config.get("metadata", {})

    title = get_ui_string("doc_title", norm_locale)
    subtitle = get_ui_string("doc_subtitle", norm_locale)
    author = config.get("document", {}).get("author", "Matheus Ferreira")
    version = config.get("document", {}).get("version", "1.0.0")
    release = config.get("document", {}).get("release", "v1.0")
    org = meta_cfg.get("organization", "DocShell")

    content = f"""% Auto-generated DocShell Metadata ({norm_locale})
\\newcommand{{\\DocTitle}}{{{title}}}
\\newcommand{{\\DocSubtitle}}{{{subtitle}}}
\\newcommand{{\\DocAuthor}}{{{author}}}
\\newcommand{{\\DocVersion}}{{{version}}}
\\newcommand{{\\DocRelease}}{{{release}}}
\\newcommand{{\\DocOrganization}}{{{org}}}
\\newcommand{{\\DocLocale}}{{{norm_locale}}}
"""
    output_path.write_text(content, encoding="utf-8")


def write_mermaid_pdf_config(model_name: str, root_dir: Path):
    """
    Writes .mermaid-config.json matching the visual model theme for mermaid-filter.
    """
    import json
    model = (model_name or "glassmorphic").lower().strip()
    configs = {
        "glassmorphic": {
            "theme": "neutral",
            "themeVariables": {
                "primaryColor": "#EEF2FF",
                "primaryTextColor": "#1E1B4B",
                "primaryBorderColor": "#6366F1",
                "lineColor": "#4338CA",
                "secondaryColor": "#F8FAFC",
                "tertiaryColor": "#F1F5F9",
                "fontFamily": "Segoe UI, Arial, sans-serif",
                "fontSize": "13px"
            }
        },
        "corporate": {
            "theme": "neutral",
            "themeVariables": {
                "primaryColor": "#EFF6FF",
                "primaryTextColor": "#1E3A8A",
                "primaryBorderColor": "#2563EB",
                "lineColor": "#1E3A8A",
                "secondaryColor": "#F8FAFC",
                "tertiaryColor": "#F1F5F9",
                "fontFamily": "Segoe UI, Arial, sans-serif",
                "fontSize": "13px"
            }
        },
        "modern-dark": {
            "theme": "neutral",
            "themeVariables": {
                "primaryColor": "#F5F3FF",
                "primaryTextColor": "#0F172A",
                "primaryBorderColor": "#8B5CF6",
                "lineColor": "#7C3AED",
                "secondaryColor": "#FAF5FF",
                "tertiaryColor": "#F3E8FF",
                "fontFamily": "Segoe UI, Arial, sans-serif",
                "fontSize": "13px"
            }
        },
        "minimal": {
            "theme": "neutral",
            "themeVariables": {
                "primaryColor": "#FFFFFF",
                "primaryTextColor": "#111827",
                "primaryBorderColor": "#374151",
                "lineColor": "#111827",
                "secondaryColor": "#F9FAFB",
                "tertiaryColor": "#F3F4F6",
                "fontFamily": "Segoe UI, Arial, sans-serif",
                "fontSize": "13px"
            }
        }
    }

    cfg = configs.get(model, configs["glassmorphic"])
    config_file = root_dir / ".mermaid-config.json"
    config_file.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def compile_pdf(model_name: Optional[str] = None, locale: str = "en-US") -> int:
    """
    Compiles Markdown documentation into a styled, versioned PDF in requested locale.
    """
    norm_locale = normalize_locale(locale)
    root_dir = ROOT_DIR
    pub_dir = root_dir / "publication"
    dist_dir = root_dir / "dist" / "pdf"
    dist_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate consolidated document and TOC with target locale
    source_md = pub_dir / "documento-completo.md"
    config = load_publication_config()
    docs = scan_docs_directory(root_dir / "docs")
    generate_consolidated_markdown(docs, config, source_md, root_dir, locale=norm_locale)

    # 2. Resolve visual model, headers, and mermaid theme configuration
    target_model = (model_name or config.get("theme", {}).get("default_model", "glassmorphic")).lower().strip()
    model_dir = root_dir / "models" / target_model
    pdf_header = model_dir / "pdf" / "header.tex"
    if not pdf_header.exists():
        pdf_header = root_dir / "models" / "glassmorphic" / "pdf" / "header.tex"

    write_mermaid_pdf_config(target_model, root_dir)

    meta_tex = pub_dir / ".pdf-meta.tex"
    write_pdf_meta(config, meta_tex, locale=norm_locale)

    doc_cfg = config.get("document", {})
    basename = doc_cfg.get("output", {}).get("pdf", {}).get("basename", "DocShell-Technical-Documentation")
    release = doc_cfg.get("release", "v1.0")
    
    if norm_locale in ["en-US", "pt-BR"] and norm_locale == doc_cfg.get("language", "en-US"):
        pdf_filename = f"{basename}-{release}.pdf"
    else:
        pdf_filename = f"{basename}-{release}-{norm_locale}.pdf"
        
    pdf_output_path = dist_dir / pdf_filename

    print("=================================================================")
    print(f"[DocShell] PDF Compilation Engine")
    print(f"   Model       : {target_model}")
    print(f"   Locale      : {norm_locale}")
    print(f"   Source      : {source_md}")
    print(f"   TeX Header  : {pdf_header}")
    print(f"   Destination : {pdf_output_path}")
    print("=================================================================")

    # 3. Check for Pandoc and LaTeX availability
    pandoc_cmd = shutil.which("pandoc")
    xelatex_cmd = shutil.which("xelatex") or shutil.which("pdflatex")

    if not pandoc_cmd:
        print("[ERROR] Pandoc was not found in PATH.")
        print("[HINT] Run 'task install' or 'winget install JohnMacFarlane.Pandoc'.")
        return 1

    if not xelatex_cmd:
        print("[ERROR] XeLaTeX / LaTeX compiler was not found in PATH.")
        print("[HINT] Run 'task install' or 'winget install MiKTeX.MiKTeX'.")
        return 1

    # 4. Build Pandoc command
    cmd = [
        pandoc_cmd,
        str(source_md),
        "--from", "markdown+raw_tex+header_attributes",
        f"--pdf-engine={xelatex_cmd}",
        "--resource-path=.:publication:images",
        f"--include-in-header={str(meta_tex)}",
        f"--include-in-header={str(pdf_header)}",
        "-V", "documentclass=report",
        "-V", "papersize=a4",
        "-V", "fontsize=11pt",
        "-V", "colorlinks=true",
        "-o", str(pdf_output_path)
    ]

    # Detect mermaid-filter for rendering Mermaid diagrams in PDF
    mermaid_filter = shutil.which("mermaid-filter") or shutil.which("mermaid-filter.cmd")
    if mermaid_filter:
        print(f"  [DocShell] Mermaid diagram filter detected: {mermaid_filter}")
        cmd.extend(["--filter", mermaid_filter])
    else:
        print("  [DocShell] Tip: Install 'mermaid-filter' ('npm install -g mermaid-filter') to auto-render Mermaid diagrams in PDF.")

    print("[DocShell] Running Pandoc and XeLaTeX...")
    res = subprocess.run(cmd, cwd=str(root_dir))
    if res.returncode == 0 and pdf_output_path.exists():
        print(f"  [OK] PDF successfully generated: {pdf_output_path}")
        return 0
    else:
        print(f"[ERROR] PDF compilation failed with exit code {res.returncode}.")
        return res.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DocShell PDF Compiler")
    parser.add_argument("-m", "--model", help="PDF visual model (glassmorphic, corporate, modern-dark, minimal)", default=None)
    parser.add_argument("-l", "--locale", help="Document locale (pt-BR, en-US, es, fr, de, it, zh-CN, ja, ru)", default="en-US")
    args = parser.parse_args()
    sys.exit(compile_pdf(args.model, locale=args.locale))
