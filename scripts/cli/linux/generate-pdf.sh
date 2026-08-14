#!/usr/bin/env bash
# ==============================================================================
# DocShell Linux - Generate PDF with Visual Design Model & Localization
# ==============================================================================
set -e
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

MODEL="glassmorphic"
LOCALE="en-US"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -m|--model) MODEL="$2"; shift ;;
        -l|--locale) LOCALE="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

PYTHON=$(resolve_python)
echo "[DocShell] Compiling PDF via Python Engine (Model: $MODEL, Locale: $LOCALE)..."
$PYTHON "$ROOT_DIR/scripts/core/pdf_engine.py" -m "$MODEL" -l "$LOCALE"
