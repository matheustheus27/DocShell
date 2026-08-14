#!/usr/bin/env bash
# ==============================================================================
# DocShell Linux CLI - Common Utilities
# ==============================================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

resolve_python() {
    if command -v python3 &>/dev/null; then
        echo "python3"
    elif command -v python &>/dev/null; then
        echo "python"
    else
        echo "python3"
    fi
}

resolve_node() {
    if command -v node &>/dev/null; then
        echo "node"
    elif command -v nodejs &>/dev/null; then
        echo "nodejs"
    else
        echo "node"
    fi
}

resolve_php() {
    if command -v php &>/dev/null; then
        echo "php"
    else
        echo "php"
    fi
}
