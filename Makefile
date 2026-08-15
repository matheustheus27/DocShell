# ==============================================================================
# DocShell - Makefile for Linux, macOS and WSL
# ==============================================================================

.PHONY: default install document pdf site serve validate docs build clean report docker-python docker-php docker-node docker-up docker-down docker-logs

# Default parameters
LANG ?= python
MODEL ?= glassmorphic
PORT ?= 8000
ALL ?= 0

default:
	@echo "================================================================="
	@echo "DocShell - Available Commands:"
	@echo "  make install               Install all compilers, runtimes and libraries"
	@echo "  make document              Consolidate docs/ with numeric ordering and TOC"
	@echo "  make pdf [MODEL=theme]     Generate versioned PDF in dist/pdf/"
	@echo "  make site [LANG=py|php|js] [MODEL=theme] Generate Webdoc in dist/webpage/"
	@echo "  make serve [LANG=py|php|js] Start local web server with AI/RAG"
	@echo "  make validate              Validate links and image assets"
	@echo "  make docs                  Run documentation pipeline (validate + doc + pdf + site)"
	@echo "  make build [LANG=..] [MODEL=..] [ALL=1] Run complete build & deploy pipeline"
	@echo "  make report                Generate and export Datadog telemetry audit report"
	@echo "  make clean                 Clean generated build artifacts"
	@echo "  make docker-python         Start Python stack in Docker (port 8000)"
	@echo "  make docker-php            Start PHP stack in Docker (port 8000)"
	@echo "  make docker-node           Start Node.js stack in Docker (port 8000)"
	@echo "  make docker-up             Start default stack in Docker"
	@echo "  make docker-down           Stop all Docker containers"
	@echo "  make docker-logs           Follow Docker container logs"
	@echo "================================================================="

install:
	@bash ./scripts/cli/linux/install-dependencies.sh

document:
	@bash ./scripts/cli/linux/generate-document.sh

pdf:
	@bash ./scripts/cli/linux/generate-pdf.sh -m "$(MODEL)"

site:
	@bash ./scripts/cli/linux/generate-site.sh -l "$(LANG)" -m "$(MODEL)"

serve:
	@bash ./scripts/cli/linux/serve-site.sh -l "$(LANG)" -p "$(PORT)"

validate:
	@bash ./scripts/cli/linux/validate-links.sh

docs: validate document pdf site

build:
	@bash ./scripts/cli/linux/build.sh -l "$(LANG)" -m "$(MODEL)" $(if $(filter 1 true yes,$(ALL)),--all,)

report:
	@python3 -u ./scripts/core/datadog_reporter.py --summary

clean:
	@bash ./scripts/cli/linux/clean.sh

docker-python:
	@docker compose --profile python up -d

docker-php:
	@docker compose --profile php up -d

docker-node:
	@docker compose --profile node up -d

docker-up: docker-python

docker-down:
	@docker compose --profile python --profile php --profile node down

docker-logs:
	@docker compose logs -f

