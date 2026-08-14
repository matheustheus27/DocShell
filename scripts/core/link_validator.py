#!/usr/bin/env python3
"""
DocShell Core - Link & Image Validator
Valida referências de links internos, arquivos Markdown e existência de imagens na pasta images/.
"""

import os
import re
import sys
from pathlib import Path


def validate_links_and_images(root_dir: Path) -> int:
    docs_dir = root_dir / "docs"
    images_dir = root_dir / "images"

    if not docs_dir.exists():
        print(f"❌ Diretório docs/ não encontrado em {docs_dir}")
        return 1

    errors = 0
    warnings = 0
    checked_files = 0
    checked_links = 0
    checked_images = 0

    print("=================================================================")
    print("🔍 DocShell Link & Asset Validator")
    print("=================================================================")

    for md_path in docs_dir.rglob("*.md"):
        checked_files += 1
        content = md_path.read_text(encoding="utf-8")
        rel_md = md_path.relative_to(root_dir)

        # 1. Verifica referências de imagens: ![alt](path)
        img_matches = re.findall(r'!\[(.*?)\]\((.*?)\)', content)
        for alt, src in img_matches:
            checked_images += 1
            src_clean = src.strip().split(" ")[0].replace("\\", "/")
            if src_clean.startswith("http://") or src_clean.startswith("https://") or src_clean.startswith("data:"):
                continue

            # Resolve se for images/nome.png ou ../images/nome.png
            img_target = None
            if "images/" in src_clean:
                img_name = src_clean.split("images/")[-1]
                img_target = images_dir / img_name
            else:
                img_target = (md_path.parent / src_clean).resolve()

            if not img_target.exists():
                print(f"❌ [IMAGEM AUSENTE] em {rel_md}: '{src}' (procurado em {img_target})")
                errors += 1
            else:
                # OK
                pass

        # 2. Verifica links Markdown normais: [texto](link)
        link_matches = re.findall(r'(?<!!)\[(.*?)\]\((.*?)\)', content)
        for text, href in link_matches:
            checked_links += 1
            href_clean = href.strip().split(" ")[0]
            if href_clean.startswith("http://") or href_clean.startswith("https://") or href_clean.startswith("#") or href_clean.startswith("mailto:"):
                continue

            # Link para arquivo .md local
            link_target = (md_path.parent / href_clean).resolve()
            if not link_target.exists():
                print(f"⚠️ [LINK QUEBRADO] em {rel_md}: [{text}]({href}) -> {link_target}")
                warnings += 1

    print("-----------------------------------------------------------------")
    print(f"📊 Resumo da Validação:")
    print(f"   Arquivos Markdown analisados: {checked_files}")
    print(f"   Imagens verificadas: {checked_images}")
    print(f"   Links verificados: {checked_links}")
    print(f"   Erros críticos: {errors}")
    print(f"   Avisos: {warnings}")
    print("=================================================================")

    if errors > 0:
        print("❌ A validação falhou devido a arquivos/imagens ausentes.")
        return 1
    
    print("✅ Todos os recursos e imagens foram validados com sucesso!")
    return 0


if __name__ == "__main__":
    current = Path(__file__).resolve()
    root = current.parent
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            root = p
            break
    exit_code = validate_links_and_images(root)
    sys.exit(exit_code)
