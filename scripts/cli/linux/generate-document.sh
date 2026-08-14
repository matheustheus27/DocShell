#!/usr/bin/env bash
# ==============================================================================
# DocShell Linux - Generate Consolidated Document & Functional TOC
# ==============================================================================
set -e
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

PYTHON=$(resolve_python)
echo "[DocShell] Running Smart Doc Parser..."
$PYTHON "$ROOT_DIR/scripts/core/doc_parser.py"
echo "  [OK] Document consolidation and TOC built successfully."
