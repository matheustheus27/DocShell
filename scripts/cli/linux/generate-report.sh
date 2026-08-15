#!/usr/bin/env bash
# ==============================================================================
# DocShell Linux - Datadog Telemetry Report Generator
# ==============================================================================
set -e
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

OUTPUT=""
FORMAT="markdown"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -o|--output) OUTPUT="$2"; shift ;;
        -f|--format) FORMAT="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

PYTHON=$(resolve_python)
REPORTER_SCRIPT="$ROOT_DIR/scripts/core/datadog_reporter.py"

if [ -f "$REPORTER_SCRIPT" ]; then
    if [ -n "$OUTPUT" ]; then
        $PYTHON "$REPORTER_SCRIPT" --summary --export "$FORMAT" --output "$OUTPUT"
    else
        $PYTHON "$REPORTER_SCRIPT" --summary --export "$FORMAT"
    fi
else
    echo "[DocShell] Reporter script not found: $REPORTER_SCRIPT"
    exit 1
fi
