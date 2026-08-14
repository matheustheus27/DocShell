#!/usr/bin/env bash
# ==============================================================================
# DocShell Linux - Serve Web Documentation & RAG Engine
# ==============================================================================
set -e
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

LANG="python"
PORT=8000

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -l|--lang) LANG="$2"; shift ;;
        -p|--port) PORT="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

LANG_LOWER=$(echo "$LANG" | tr '[:upper:]' '[:lower:]')

case "$LANG_LOWER" in
    py|python)
        PYTHON=$(resolve_python)
        echo "[DocShell] Starting Python server on port $PORT..."
        $PYTHON "$ROOT_DIR/scripts/generators/python/serve_site.py" -p "$PORT"
        ;;
    php)
        PHP=$(resolve_php)
        echo "[DocShell] Starting PHP server on port $PORT..."
        $PHP "$ROOT_DIR/scripts/generators/php/serve_site.php" "$PORT"
        ;;
    js|javascript|node)
        NODE=$(resolve_node)
        echo "[DocShell] Starting Node.js server on port $PORT..."
        $NODE "$ROOT_DIR/scripts/generators/javascript/serve_site.js" -p "$PORT"
        ;;
    *)
        PYTHON=$(resolve_python)
        $PYTHON "$ROOT_DIR/scripts/generators/python/serve_site.py" -p "$PORT"
        ;;
esac
