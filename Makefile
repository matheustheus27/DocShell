# ==============================================================================
# DocShell - Makefile for Linux, macOS and WSL
# ==============================================================================

.PHONY: default install document pdf site serve validate docs clean docker-up docker-down docker-logs

# Default parameters
LANG ?= python
MODEL ?= glassmorphic
PORT ?= 8000

default:
	@echo "================================================================="
	@echo "DocShell - Available Commands:"
	@echo "  make install               Install all compilers, runtimes and libraries"
	@echo "  make document              Consolidate docs/ with numeric ordering and TOC"
	@echo "  make pdf [MODEL=theme]     Generate versioned PDF in dist/pdf/"
	@echo "  make site [LANG=py|php|js] [MODEL=theme] Generate Webdoc in dist/webpage/"
	@echo "  make serve [LANG=py|php|js] Start local web server with AI/RAG"
	@echo "  make validate              Validate links and image assets"
	@echo "  make docs                  Run full build pipeline (validate + pdf + site)"
	@echo "  make clean                 Clean generated build artifacts"
	@echo "  make docker-up             Start Docker containers"
	@echo "  make docker-down           Stop Docker containers"
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

clean:
	@bash ./scripts/cli/linux/clean.sh

docker-up:
	@docker-compose up -d

docker-down:
	@docker-compose down

docker-logs:
	@docker-compose logs -f
