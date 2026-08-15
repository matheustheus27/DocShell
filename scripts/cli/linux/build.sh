#!/usr/bin/env bash
# ==============================================================================
# DocShell Linux/macOS - Full Build & Deploy Orchestrator
# Builds docs, PDF, web frontend, atomic backend, worker and Docker containers
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

LANGUAGE="python"
MODEL="glassmorphic"
ALL_PROFILES=false
LOCALE="pt-BR"

while [[ $# -gt 0 ]]; do
  case $1 in
    -l|--lang|--language)
      LANGUAGE="$2"
      shift 2
      ;;
    -m|--model)
      MODEL="$2"
      shift 2
      ;;
    -a|--all)
      ALL_PROFILES=true
      shift
      ;;
    --locale)
      LOCALE="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

echo "================================================================="
echo "[DocShell] Full Build Pipeline Orchestrator (Linux/macOS)"
if [ "$ALL_PROFILES" = true ]; then
  echo "   Language Runtime : ALL (Python, PHP, Node.js)"
else
  echo "   Language Runtime : $LANGUAGE"
fi
echo "   Theme Model      : $MODEL"
echo "   Target Locale    : $LOCALE"
echo "================================================================="

# 1. Validate internal links
echo -e "\n[1/5] Validating internal links and assets..."
bash "$SCRIPT_DIR/validate-links.sh"

# 2. Consolidate documents
echo -e "\n[2/5] Consolidating documents (documento-completo.md)..."
bash "$SCRIPT_DIR/generate-document.sh"

# 3. Generate PDF
echo -e "\n[3/5] Compiling PDF ($MODEL)..."
bash "$SCRIPT_DIR/generate-pdf.sh" -m "$MODEL"

# 4. Generate Web, Backend & Worker
echo -e "\n[4/5] Generating Web, Backend & Worker ($LANGUAGE, $MODEL)..."
if [ "$ALL_PROFILES" = true ]; then
  bash "$SCRIPT_DIR/generate-site.sh" -l "py" -m "$MODEL"
else
  bash "$SCRIPT_DIR/generate-site.sh" -l "$LANGUAGE" -m "$MODEL"
fi

# 5. Build and start Docker container stack
echo -e "\n[5/5] Building and launching Docker container stack..."
cd "$ROOT_DIR"
if [ "$ALL_PROFILES" = true ]; then
  echo "Starting all Docker profiles: python, php, node..."
  docker compose --profile python --profile php --profile node up -d --build
else
  NORM_LANG="$(echo "$LANGUAGE" | tr '[:upper:]' '[:lower:]' | xargs)"
  if [ "$NORM_LANG" = "php" ]; then
    echo "Starting PHP stack on port 8000..."
    docker compose --profile php up -d --build
  elif [ "$NORM_LANG" = "js" ] || [ "$NORM_LANG" = "javascript" ] || [ "$NORM_LANG" = "node" ]; then
    echo "Starting Node.js stack on port 8000..."
    docker compose --profile node up -d --build
  else
    echo "Starting Python stack on port 8000..."
    docker compose --profile python up -d --build
  fi
fi

echo "================================================================="
echo "[OK] Full build completed successfully!"
echo "   Web Interface: http://localhost:8000"
echo "   RAG API Gateway: http://localhost:8080"
echo "   RabbitMQ UI: http://localhost:15672 (guest/guest)"
echo "================================================================="
