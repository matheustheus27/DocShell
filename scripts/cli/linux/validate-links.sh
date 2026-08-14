#!/usr/bin/env bash
# ==============================================================================
# DocShell Linux - Validate Links & Assets
# ==============================================================================
set -e
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

PYTHON=$(resolve_python)
$PYTHON "$ROOT_DIR/scripts/core/link_validator.py"
