#!/usr/bin/env bash
# ==============================================================================
# DocShell Linux - Generate Web Documentation (Python, PHP, JavaScript)
# ==============================================================================
set -e
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

LANG="python"
MODEL="glassmorphic"
LOCALE="en-US"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -l|--lang) LANG="$2"; shift ;;
        -m|--model) MODEL="$2"; shift ;;
        --locale|--loc) LOCALE="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

LANG_LOWER=$(echo "$LANG" | tr '[:upper:]' '[:lower:]')

# 0. Clean dist/webpage directory before building site
DIST_WEB="$ROOT_DIR/dist/webpage"
if [ -d "$DIST_WEB" ]; then
    echo "[DocShell] Cleaning dist/webpage directory..."
    rm -rf "${DIST_WEB:?}"/*
fi
mkdir -p "$DIST_WEB"

case "$LANG_LOWER" in
    py|python)
        PYTHON=$(resolve_python)
        echo "[DocShell] Building website via Python generator (Model: $MODEL, Locale: $LOCALE)..."
        $PYTHON "$ROOT_DIR/scripts/generators/python/build_site.py" -m "$MODEL" -l "$LOCALE"
        ;;
    php)
        PHP=$(resolve_php)
        echo "[DocShell] Building website via PHP generator (Model: $MODEL)..."
        $PHP "$ROOT_DIR/scripts/generators/php/build_site.php" "$MODEL"
        ;;
    js|javascript|node)
        NODE=$(resolve_node)
        echo "[DocShell] Building website via Node.js generator (Model: $MODEL)..."
        $NODE "$ROOT_DIR/scripts/generators/javascript/build_site.js" -m "$MODEL"
        ;;
    *)
        PYTHON=$(resolve_python)
        $PYTHON "$ROOT_DIR/scripts/generators/python/build_site.py" -m "$MODEL" -l "$LOCALE"
        ;;
esac
