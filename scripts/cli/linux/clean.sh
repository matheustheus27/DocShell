#!/usr/bin/env bash
# ==============================================================================
# DocShell Linux - Cleanup Generated Artifacts
# ==============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

echo "[DocShell] Cleaning up build artifacts..."
rm -rf "$ROOT_DIR/dist"
rm -f "$ROOT_DIR/publication/documento-completo.md"
rm -f "$ROOT_DIR/publication/.pdf-meta.tex"
rm -f "$ROOT_DIR/publication/search_index.json"
echo "  [OK] Cleanup completed."
