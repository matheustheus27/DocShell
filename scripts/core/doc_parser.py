#!/usr/bin/env python3
"""
DocShell Core - Smart Document Parser & TOC Builder
Recursively scans docs/ directory, naturally sorts files and folders,
extracts titles, builds document hierarchies, normalizes image assets,
and generates consolidated markdown with a functional Table of Contents (TOC)
supporting multi-language localization (TranslateGemma / 9 locales).
"""

import html
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def _resolve_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent

ROOT_DIR = _resolve_root()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.core.translator import get_ui_string, normalize_locale, translate_text


def natural_sort_key(s: str) -> List[Any]:
    """Key for natural alphanumeric sorting (e.g., 01, 02, 10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]


def slugify(text: str) -> str:
    """Generates clean, valid URL and HTML anchor slugs from titles."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')


def parse_inline(text: str) -> str:
    """Converts inline markdown links, bold, italics, images, and code."""
    # Images ![alt](src)
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" class="doc-img" />', text)
    # Links [text](url)
    text = re.sub(r'(?<!!)\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    # Bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic *text*
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Inline code `code`
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text


def parse_markdown_to_html(md_text: str) -> str:
    """Converts standard Markdown text into structured HTML."""
    lines = md_text.splitlines()
    html_lines = []
    in_code_block = False
    code_lang = ""
    in_list = False
    list_type = "ul"
    in_table = False

    for line in lines:
        stripped = line.strip()

        # Code block fences ```lang
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_lang = stripped.lstrip("`").strip()
                if code_lang.lower() == "mermaid":
                    html_lines.append('<pre class="mermaid">')
                else:
                    html_lines.append(f'<pre><code class="language-{code_lang}">')
            else:
                in_code_block = False
                if code_lang.lower() == "mermaid":
                    html_lines.append('</pre>')
                else:
                    html_lines.append('</code></pre>')
            continue

        if in_code_block:
            if code_lang.lower() == "mermaid":
                html_lines.append(line)
            else:
                html_lines.append(html.escape(line))
            continue

        # Close open lists/tables when encountering a blank line
        if not stripped:
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
            if in_table:
                html_lines.append('</tbody></table></div>')
                in_table = False
            continue

        # Headings
        h_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if h_match:
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
            if in_table:
                html_lines.append('</tbody></table></div>')
                in_table = False
            level = len(h_match.group(1))
            heading_text = h_match.group(2).strip()
            
            h_id = ""
            id_match = re.search(r'\{#(.*?)\}', heading_text)
            if id_match:
                h_id = f' id="{id_match.group(1)}"'
                heading_text = re.sub(r'\{#.*?\}', '', heading_text).strip()
            else:
                h_id = f' id="{slugify(heading_text)}"'

            html_lines.append(f'<h{level}{h_id}>{parse_inline(heading_text)}</h{level}>')
            continue

        # Blockquotes > quote
        if stripped.startswith(">"):
            quote_text = stripped.lstrip("> ").strip()
            html_lines.append(f'<blockquote class="doc-quote">{parse_inline(quote_text)}</blockquote>')
            continue

        # Horizontal rules --- or ***
        if re.match(r'^(-{3,}|\*{3,}|_{3,})$', stripped):
            html_lines.append('<hr class="doc-divider" />')
            continue

        # Unordered Lists - item or * item
        ul_match = re.match(r'^[-*+]\s+(.+)$', stripped)
        if ul_match:
            if in_table:
                html_lines.append('</tbody></table></div>')
                in_table = False
            if not in_list or list_type != "ul":
                if in_list:
                    html_lines.append(f'</{list_type}>')
                html_lines.append('<ul class="doc-list">')
                in_list = True
                list_type = "ul"
            html_lines.append(f'<li>{parse_inline(ul_match.group(1))}</li>')
            continue

        # Ordered Lists 1. item
        ol_match = re.match(r'^\d+\.\s+(.+)$', stripped)
        if ol_match:
            if in_table:
                html_lines.append('</tbody></table></div>')
                in_table = False
            if not in_list or list_type != "ol":
                if in_list:
                    html_lines.append(f'</{list_type}>')
                html_lines.append('<ol class="doc-list">')
                in_list = True
                list_type = "ol"
            html_lines.append(f'<li>{parse_inline(ol_match.group(1))}</li>')
            continue

        # Tables | col | col |
        if stripped.startswith("|") and stripped.endswith("|"):
            parts = [p.strip() for p in stripped.split("|")[1:-1]]
            if all(re.match(r'^:?-+:?$', p) for p in parts):
                continue
            
            if not in_table:
                in_table = True
                html_lines.append('<div class="table-container"><table class="doc-table"><thead><tr>')
                for p in parts:
                    html_lines.append(f'<th>{parse_inline(p)}</th>')
                html_lines.append('</tr></thead><tbody>')
            else:
                html_lines.append('<tr>')
                for p in parts:
                    html_lines.append(f'<td>{parse_inline(p)}</td>')
                html_lines.append('</tr>')
            continue

        # Paragraph
        html_lines.append(f'<p>{parse_inline(line)}</p>')

    if in_list:
        html_lines.append(f'</{list_type}>')
    if in_table:
        html_lines.append('</tbody></table></div>')

    return "\n".join(html_lines)


def extract_frontmatter_and_content(file_path: Path) -> Tuple[Dict[str, str], str, str]:
    """
    Extracts YAML frontmatter (if present) and clean markdown content.
    Returns (metadata, markdown_content, title).
    """
    content = file_path.read_text(encoding="utf-8")
    metadata: Dict[str, str] = {}
    title = ""

    # Check for YAML frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if fm_match:
        fm_raw = fm_match.group(1)
        content_body = content[fm_match.end():]
        for line in fm_raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                metadata[k.strip()] = v.strip().strip('"').strip("'")
        if "title" in metadata:
            title = metadata["title"]
    else:
        content_body = content

    # If no title in frontmatter, extract first # Heading
    if not title:
        h1_match = re.search(r"^#\s+(.+)$", content_body, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
        else:
            raw_name = file_path.stem
            clean_name = re.sub(r"^\d+[-_.]*", "", raw_name).replace("-", " ").replace("_", " ").strip()
            title = clean_name.capitalize() if clean_name else raw_name

    return metadata, content_body, title


def scan_docs_directory(docs_dir: Path, locale: str = "pt-BR") -> List[Dict[str, Any]]:
    """
    Recursively scans docs_dir and builds a structured list of documents in requested locale.
    """
    items = []
    if not docs_dir.exists():
        return items

    # Collect all .md files
    md_files = list(docs_dir.rglob("*.md"))
    # Natural sort by relative path parts
    md_files.sort(key=lambda p: [natural_sort_key(part) for part in p.relative_to(docs_dir).parts])

    for md_path in md_files:
        rel_path = md_path.relative_to(docs_dir)
        parts = rel_path.parts
        
        # Determine section (parent directory or General)
        if len(parts) > 1:
            section_raw = parts[0]
            section_clean = re.sub(r"^\d+[-_.]*", "", section_raw).replace("-", " ").replace("_", " ").title()
        else:
            section_clean = "General"

        metadata, body, title = extract_frontmatter_and_content(md_path)
        doc_slug = slugify(f"{section_clean}-{title}")

        items.append({
            "file_path": str(md_path),
            "relative_path": str(rel_path).replace("\\", "/"),
            "section": section_clean,
            "title": title,
            "slug": doc_slug,
            "metadata": metadata,
            "body": body,
            "locale": locale
        })

    return items


def normalize_image_paths(body: str, source_file: Path, root_dir: Path, target_mode: str = "pdf") -> str:
    """
    Normalizes markdown image paths ![alt](path) and HTML <img> tags:
    - For PDF: Points to images/ or ../images/ with automatic SVG->PNG fallback for XeLaTeX,
      and converts remote GlassHub Engine API image URLs to local assets/placeholders so XeLaTeX doesn't require Inkscape.
    - For Web: Keeps full HTML and markdown URLs intact.
    """
    images_dir = root_dir / "images"

    if target_mode == "pdf":
        # Convert HTML <img src="...logo..."> to local logo image for PDF
        body = re.sub(
            r'<img\s+[^>]*src=["\']https://glass-hub-engine\.vercel\.app/api/logo[^"\']*["\'][^>]*>',
            r'![GlassHub DocShell Logo](images/logo.svg)',
            body,
            flags=re.IGNORECASE
        )
        # Remove HTML badges from PDF output to prevent LaTeX svg package errors
        body = re.sub(
            r'<img\s+[^>]*src=["\']https://glass-hub-engine\.vercel\.app/api/badge[^"\']*["\'][^>]*>',
            r'',
            body,
            flags=re.IGNORECASE
        )
        # Remove HTML container tags in PDF output
        body = re.sub(r'<div\s+align=["\']center["\']>', '', body, flags=re.IGNORECASE)
        body = re.sub(r'</div>', '', body, flags=re.IGNORECASE)

        def replace_md_img(match):
            alt = match.group(1)
            src = match.group(2).strip()
            
            if "glass-hub-engine.vercel.app/api/logo" in src:
                return f"![{alt}](images/logo.svg)"
            elif "glass-hub-engine.vercel.app/api/" in src:
                return f"**[{alt}]**" if alt else ""

            if src.startswith("http://") or src.startswith("https://") or src.startswith("data:"):
                return match.group(0)

            clean_src = src.replace("\\", "/")
            img_name = clean_src.split("images/")[-1] if "images/" in clean_src else Path(clean_src).name

            target_img_name = img_name
            if img_name.lower().endswith(".svg"):
                png_counterpart = Path(img_name).stem + ".png"
                if (images_dir / png_counterpart).exists():
                    target_img_name = png_counterpart
            
            return f"![{alt}](images/{target_img_name})"

        return re.sub(r"!\[(.*?)\]\((.*?)\)", replace_md_img, body)
    else:
        def replace_web_img(match):
            alt = match.group(1)
            src = match.group(2).strip()
            if src.startswith("http://") or src.startswith("https://") or src.startswith("data:"):
                return match.group(0)
            clean_src = src.replace("\\", "/")
            img_name = clean_src.split("images/")[-1] if "images/" in clean_src else Path(clean_src).name
            return f"![{alt}](images/{img_name})"

        return re.sub(r"!\[(.*?)\]\((.*?)\)", replace_web_img, body)


def generate_consolidated_markdown(
    docs: List[Dict[str, Any]],
    config: Dict[str, Any],
    output_path: Path,
    root_dir: Path,
    locale: str = "en-US"
) -> str:
    """
    Generates publication/documento-completo.md with cover, metadata table,
    properly spaced functional clickable TOC, and fully cross-referenced sections with unique anchors.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    norm_locale = normalize_locale(locale)
    doc_cfg = config.get("document", {})
    meta_cfg = config.get("metadata", {})

    doc_title = get_ui_string("doc_title", norm_locale)
    doc_subtitle = get_ui_string("doc_subtitle", norm_locale)
    doc_author = doc_cfg.get("author", "Matheus Ferreira")
    doc_version = doc_cfg.get("version", "1.0.0")
    doc_release = doc_cfg.get("release", "v1.0")

    lbl_toc = get_ui_string("toc", norm_locale)
    lbl_property = get_ui_string("property", norm_locale)
    lbl_specification = get_ui_string("specification", norm_locale)
    lbl_version = get_ui_string("version", norm_locale)
    lbl_author = get_ui_string("author", norm_locale)
    lbl_classification = get_ui_string("classification", norm_locale)
    lbl_compiled_docs = get_ui_string("compiled_docs", norm_locale)

    lines = []
    
    # Consolidated Document Frontmatter
    lines.append("---")
    lines.append(f'title: "{doc_title}"')
    lines.append(f'subtitle: "{doc_subtitle}"')
    lines.append(f'author: "{doc_author}"')
    lines.append(f'version: "{doc_version}"')
    lines.append(f'release: "{doc_release}"')
    lines.append(f'language: "{norm_locale}"')
    lines.append(f'organization: "{meta_cfg.get("organization", "DocShell Platform")}"')
    lines.append(f'classification: "{meta_cfg.get("classification", "Public")}"')
    lines.append("---")
    lines.append("")

    # Cover Header
    lines.append(f"# {doc_title}")
    lines.append("")
    if doc_subtitle:
        lines.append(f"> *{doc_subtitle}*")
        lines.append("")

def format_doc_for_pdf(
    body: str,
    slug: str,
    doc_title: str,
    sec_num: int,
    doc_idx: int,
    is_cover_doc: bool = False
) -> str:
    """
    Normalizes document headings for PDF book compilation.
    - Level 1 (#) becomes Level 2 (## sec_num.doc_idx Title {#slug})
    - Subheadings are shifted down (## -> ###, ### -> ####)
    - Preserves raw tex / figures without orphan page breaks.
    """
    lines = body.splitlines()
    new_lines = []
    first_h1_handled = False

    for line in lines:
        stripped = line.strip()
        h_match = re.match(r'^(#{1,5})\s+(.+)$', stripped)
        if h_match:
            level = len(h_match.group(1))
            htext = h_match.group(2).strip()
            htext_clean = re.sub(r'\s*\{#.*?\}', '', htext).strip()

            if level == 1 and not first_h1_handled:
                first_h1_handled = True
                new_lines.append(f"## {sec_num}.{doc_idx} {htext_clean} {{#{slug}}}")
            else:
                new_hashes = "#" * (level + 1)
                new_lines.append(f"{new_hashes} {htext_clean}")
        else:
            new_lines.append(line)

    if not first_h1_handled:
        new_lines.insert(0, f"## {sec_num}.{doc_idx} {doc_title} {{#{slug}}}\n")

    return "\n".join(new_lines)


def generate_consolidated_markdown(
    docs: List[Dict[str, Any]],
    config: Dict[str, Any],
    output_path: Path,
    root_dir: Path,
    locale: str = "en-US"
) -> str:
    """
    Combines scanned markdown docs into a single, beautifully structured Markdown file
    with normalized heading hierarchy and clean LaTeX page breaks.
    """
    norm_locale = normalize_locale(locale)
    doc_cfg = config.get("document", {})
    meta_cfg = config.get("metadata", {})

    doc_title = get_ui_string("doc_title", norm_locale)
    doc_subtitle = get_ui_string("doc_subtitle", norm_locale)
    doc_author = doc_cfg.get("author", "Matheus Ferreira")
    doc_version = doc_cfg.get("version", "1.0.0")
    doc_release = doc_cfg.get("release", "v1.0")

    lbl_property = get_ui_string("property", norm_locale)
    lbl_specification = get_ui_string("specification", norm_locale)
    lbl_version = get_ui_string("version", norm_locale)
    lbl_author = get_ui_string("author", norm_locale)
    lbl_classification = get_ui_string("classification", norm_locale)
    lbl_compiled_docs = get_ui_string("compiled_docs", norm_locale)
    lbl_toc = get_ui_string("toc", norm_locale)

    lines = []
    
    # Consolidated Document Frontmatter
    lines.append("---")
    lines.append(f'title: "{doc_title}"')
    lines.append(f'subtitle: "{doc_subtitle}"')
    lines.append(f'author: "{doc_author}"')
    lines.append(f'version: "{doc_version}"')
    lines.append(f'release: "{doc_release}"')
    lines.append(f'language: "{norm_locale}"')
    lines.append(f'organization: "{meta_cfg.get("organization", "DocShell Platform")}"')
    lines.append(f'classification: "{meta_cfg.get("classification", "Public")}"')
    lines.append("---")
    lines.append("")

    # Cover Page
    lines.append(f"# {doc_title}")
    lines.append("")
    if doc_subtitle:
        lines.append(f"> *{doc_subtitle}*")
        lines.append("")

    # Document Metadata Table
    lines.append(f"| {lbl_property} | {lbl_specification} |")
    lines.append("| :--- | :--- |")
    lines.append(f"| **{lbl_version} / Release** | `{doc_version}` ({doc_release}) |")
    lines.append(f"| **{lbl_author}** | {doc_author} |")
    lines.append(f"| **{lbl_classification}** | {meta_cfg.get('classification', 'Public')} |")
    lines.append(f"| **{lbl_compiled_docs}** | {len(docs)} files processed |")
    lines.append("")
    lines.append("\\newpage")
    lines.append("")

    # FUNCTIONAL TABLE OF CONTENTS (TOC)
    lines.append(f"# {lbl_toc} {{#sumario-toc}}")
    lines.append("")

    # Group documents by section
    section_map: Dict[str, List[Dict[str, Any]]] = {}
    for doc in docs:
        if Path(doc["relative_path"]).name == "00-capa.md":
            continue
        section_name = doc["section"]
        if section_name not in section_map:
            section_map[section_name] = []
        section_map[section_name].append(doc)

    sec_num = 0
    for section_name, doc_list in section_map.items():
        sec_num += 1
        disp_sec = section_name
        if norm_locale != "pt-BR":
            disp_sec = translate_text(section_name, target_locale=norm_locale, source_locale="pt-BR", root_dir=root_dir)
        sec_slug = slugify(f"section-{sec_num}-{section_name}")
        lines.append(f"### {sec_num}. [{disp_sec}](#{sec_slug})")
        lines.append("")
        for item_idx, d in enumerate(doc_list, 1):
            disp_title = d["title"]
            if norm_locale != "pt-BR":
                disp_title = translate_text(d["title"], target_locale=norm_locale, source_locale="pt-BR", root_dir=root_dir)
            lines.append(f"- [{sec_num}.{item_idx} {disp_title}](#{d['slug']})")
        lines.append("")

    lines.append("\\newpage")
    lines.append("")

    # SECTION AND DOCUMENT BODIES (Chapters & Sections)
    sec_num = 0
    for section_name, doc_list in section_map.items():
        sec_num += 1
        disp_sec = section_name
        if norm_locale != "pt-BR":
            disp_sec = translate_text(section_name, target_locale=norm_locale, source_locale="pt-BR", root_dir=root_dir)
        sec_slug = slugify(f"section-{sec_num}-{section_name}")
        lines.append(f"# {sec_num}. {disp_sec} {{#{sec_slug}}}")
        lines.append("")

        for item_idx, d in enumerate(doc_list, 1):
            lines.append(f"<!-- doc: {d['relative_path']} -->")
            
            # Normalize images
            norm_body = normalize_image_paths(d["body"], Path(d["file_path"]), root_dir, target_mode="pdf")
            
            # Translate body if target locale is not pt-BR
            if norm_locale != "pt-BR":
                norm_body = translate_text(norm_body, target_locale=norm_locale, source_locale="pt-BR", root_dir=root_dir)

            disp_title = d["title"]
            if norm_locale != "pt-BR":
                disp_title = translate_text(d["title"], target_locale=norm_locale, source_locale="pt-BR", root_dir=root_dir)

            # Format headings hierarchy
            formatted_body = format_doc_for_pdf(
                norm_body,
                slug=d["slug"],
                doc_title=disp_title,
                sec_num=sec_num,
                doc_idx=item_idx
            )

            lines.append(formatted_body)
            lines.append("")
            lines.append("")

    full_text = "\n".join(lines)
    output_path.write_text(full_text, encoding="utf-8")
    return full_text


def build_search_and_rag_index(docs: List[Dict[str, Any]], root_dir: Path) -> List[Dict[str, Any]]:
    """
    Generates search index and semantic chunks for RAG engine and client-side search.
    Cleanly strips raw code-block boxes and frontmatter from summaries.
    """
    index = []
    for doc in docs:
        chunks = re.split(r'\n(?=##?\s+)', doc["body"])
        for idx, chunk in enumerate(chunks):
            chunk_clean = chunk.strip()
            if not chunk_clean:
                continue
            
            m_h = re.match(r'^##?\s+(.+)$', chunk_clean, re.MULTILINE)
            chunk_title = m_h.group(1).strip() if m_h else doc["title"]
            
            # Remove raw code block diagrams from search summary text
            text_without_code = re.sub(r'```[\s\S]*?```', ' ', chunk_clean)
            text_plain = re.sub(r'[#*`_\[\]()!>]', ' ', text_without_code)
            text_plain = re.sub(r'\s+', ' ', text_plain).strip()

            if not text_plain:
                text_plain = doc["title"]

            index.append({
                "id": f"{doc['slug']}-{idx}",
                "doc_title": doc["title"],
                "section": doc["section"],
                "chunk_title": chunk_title,
                "slug": doc["slug"],
                "relative_path": doc["relative_path"],
                "text": text_plain[:600]
            })

    return index


def main():
    import argparse
    from scripts.core.config_loader import load_publication_config

    parser = argparse.ArgumentParser(description="DocShell Document Parser")
    parser.add_argument("-l", "--locale", help="Target locale for TOC and metadata (pt-BR, en-US, es, fr, de, it, zh-CN, ja, ru)", default="en-US")
    args = parser.parse_args()

    docs_dir = ROOT_DIR / "docs"
    pub_dir = ROOT_DIR / "publication"
    output_md = pub_dir / "documento-completo.md"
    search_json = pub_dir / "search_index.json"

    print(f"[DocShell] Scanning documentation in: {docs_dir} (Locale: {args.locale})")
    docs = scan_docs_directory(docs_dir)
    print(f"[DocShell] Found {len(docs)} documents.")

    config = load_publication_config()
    generate_consolidated_markdown(docs, config, output_md, ROOT_DIR, locale=args.locale)
    print(f"  [OK] Consolidated document generated: {output_md}")

    index = build_search_and_rag_index(docs, ROOT_DIR)
    search_json.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [OK] Search index generated: {search_json} ({len(index)} chunks)")


if __name__ == "__main__":
    main()
