# 🐚 DocShell - Intelligent Documentation Framework (PDF & Web)

> **Unified, modern, decoupled platform for generating technical documentation in versioned PDF and interactive Websites across multiple runtimes (Python, PHP, JavaScript) with semantic search, RAG/AI assistant, Docker support, and customizable visual themes.**

---

## 📑 Table of Contents

- [Overview & Architecture](#-overview--architecture)
- [Key Features](#-key-features)
- [Project Directory Structure](#-project-directory-structure)
- [Prerequisites & Installation](#-prerequisites--installation)
- [CLI Quickstart Guide](#-cli-quickstart-guide)
  - [Taskfile Commands (Recommended)](#taskfile-commands-recommended)
  - [Makefile Commands (Alternative)](#makefile-commands-alternative)
- [Document Structuring Guide (`docs/`)](#-document-structuring-guide-docs)
- [Images & Visual Assets (`images/`)](#-images--visual-assets-images)
- [Themes & Visual Models (`models/`)](#-themes--visual-models-models)
- [Publication Settings (`publication/`)](#-publication-settings-publication)
- [RAG & AI Assistant](#-rag--ai-assistant)
- [Docker & Container Orchestration](#-docker--container-orchestration)
- [License](#-license)

---

## 🔭 Overview & Architecture

**DocShell** transforms Markdown files organized in the `docs/` folder into publication-grade deliverables:
1. **Executive & Versioned PDF Document** (`dist/pdf/{basename}-{release}.pdf`) using Pandoc and XeLaTeX.
2. **Modern Interactive Website** (`dist/webpage/`) with real-time search filtering, dynamic sidebar, responsive typography, and an **embedded AI Assistant Chatbot powered by RAG (Ollama / Llama 3.2)**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DOCSHELL ARCHITECTURE                         │
│                                                                         │
│   docs/ (Markdown) ──▶ Smart Numeric Parser ──▶ Table of Contents (TOC) │
│                                │                                        │
│            ┌───────────────────┴───────────────────┐                    │
│            ▼                                       ▼                    │
│      PDF Engine (XeLaTeX)                  Web Generators               │
│    (dist/pdf/*.pdf)             ┌──────────────────┼──────────────────┐ │
│                                 ▼                  ▼                  ▼ │
│                            Python 🐍            PHP 🐘           Node.js ⚡
│                                 │                  │                  │ │
│                                 └──────────────────┴──────────────────┘ │
│                                                    │                    │
│                                                    ▼                    │
│                                        dist/webpage/ + RAG Engine       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

- 🔢 **Smart Reader & Natural Numeric Ordering**: Recursively scans `docs/` directories and files based on their leading numbers (`00-`, `01-`, `02-`), automatically generating section hierarchies and page order.
- 🎯 **Functional Table of Contents (TOC)**: Automatically builds navigable TOCs with clickable anchor links (`#section-slug`) in both PDF and Web editions.
- 🌐 **3 Web Documentation Runtimes (`-l / --lang`)**: Generate and serve the website using **Python**, **PHP**, or **JavaScript (Node.js)** via simple CLI flags.
- 🎨 **Selectable Design Models (`-m / --model`)**:
  - `Glassmorphic` *(Default)*: Translucent frosted glass effect (*backdrop-filter: blur*), indigo/cyan modern gradients, and refined dark mode.
  - `Corporate`: Clean navy blue and slate palette designed for formal reports and governance.
  - `Modern-Dark`: High-contrast deep obsidian theme tailored for developers and API specs.
  - `Minimal`: Distraction-free Swiss typography focused on fast reading.
- 🤖 **Embedded Generative AI & RAG**: Floating interactive AI Chatbot widget, chunk-based indexing (`search_index.json`), and native connection to **Ollama**.
- 🛡️ **Atomic Component Architecture**: Single-responsibility scripts prevent antivirus heuristic false positives on Windows and Linux.
- 🐳 **Docker & Docker Compose**: Ready-to-use container configurations for all runtimes, RAG microservices, and Ollama.

---

## 📁 Project Directory Structure

```
DocShell/
├── docs/                        # Markdown documents with numeric ordering
│   ├── 00-capa.md
│   ├── 01-visao-geral.md
│   ├── 02-arquitetura/
│   │   ├── 01-principios.md
│   │   └── 02-componentes.md
│   ├── 03-guia-de-uso/
│   ├── 04-ia-e-rag/
│   ├── 05-docker/
│   └── 99-conclusao.md
├── images/                      # Project image assets (*.svg, *.png, *.jpg)
├── models/                      # Visual themes and templates
│   ├── glassmorphic/            # Glassmorphism Theme (Default)
│   ├── corporate/               # Corporate Theme
│   ├── modern-dark/             # Modern Dark Theme
│   └── minimal/                 # Minimalist Theme
├── publication/                 # Publication configuration
│   ├── publication.yml          # Metadata, author, colors, release, etc.
│   └── templates/               # Base LaTeX and HTML templates
├── scripts/                     # Atomic Component Architecture
│   ├── core/                    # Core engines (parser, config, validator, RAG, PDF)
│   │   ├── doc_parser.py        # Numeric parser and TOC builder
│   │   ├── config_loader.py     # YAML configuration loader
│   │   ├── link_validator.py    # Link and image validator
│   │   ├── rag_engine.py        # Semantic search and RAG engine
│   │   └── pdf_engine.py        # PDF compiler engine
│   ├── generators/              # Web generators per language runtime
│   │   ├── python/              # Python generator and server
│   │   ├── php/                 # PHP generator and server
│   │   └── javascript/          # Node.js generator and server
│   ├── cli/                     # Automation scripts per OS
│   │   ├── windows/             # PowerShell scripts (generate-site.ps1, generate-pdf.ps1, etc.)
│   │   └── linux/               # Bash scripts (generate-site.sh, generate-pdf.sh, etc.)
│   ├── docker/                  # Dockerfiles and container configurations
│   └── requirements.txt         # Python dependencies
├── dist/                        # Build output artifacts
│   ├── pdf/                     # Compiled versioned PDF ({basename}-{release}.pdf)
│   └── webpage/                 # Website files + assets + search index + AI widget
├── Taskfile.yml                 # Cross-platform task automation (Task)
├── Makefile                     # GNU Make automation
├── docker-compose.yml           # Multi-service container orchestration
├── README.md                    # Project guide
└── LICENSE                      # Non-commercial permissive license
```

---

## 🛠️ Prerequisites & Installation

### Automated Installation (Recommended)

Run the automated installer to download and configure all compilers, runtimes, and dependencies:

```bash
# Windows / Linux / macOS
task install
```
*(or `make install` on Linux/macOS)*

### Manual Prerequisites

| Tool | Purpose | Windows Installation | Linux Installation (Ubuntu/Debian) |
|---|---|---|---|
| **Taskfile** | CLI Automation | `winget install Task.Task` | `sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d` |
| **Python** | Runtime & Parser | `winget install Python.Python.3.12` | `sudo apt install python3 python3-pip` |
| **Pandoc & MiKTeX/XeLaTeX** | PDF Compilation | `winget install JohnMacFarlane.Pandoc MiKTeX.MiKTeX` | `sudo apt install pandoc texlive-xetex` |
| **Node.js** (Optional) | JS Runtime | `winget install OpenJS.NodeJS` | `sudo apt install nodejs npm` |
| **PHP** (Optional) | PHP Runtime | `winget install PHP.PHP` | `sudo apt install php php-cli` |
| **Docker** | Containerization | `winget install Docker.DockerDesktop` | `sudo apt install docker.io docker-compose` |

---

## 🚀 CLI Quickstart Guide

### Taskfile Commands (Recommended)

| Command | Description | Example |
|---|---|---|
| `task install` | Downloads and installs all runtimes, PDF compilers, and libraries | `task install` |
| `task site` | Generates Web documentation using default runtime and theme | `task site` |
| `task site -- -l <Lang>` | Generates site specifying runtime language (`Py`, `PHP`, `JS`) | `task site -- -l "PHP"` |
| `task site -- -m <Model>` | Generates site specifying visual theme model | `task site -- -m "Corporate"` |
| `task site -- -l <Lang> -m <Model>` | Combines language runtime and theme model | `task site -- -l "JS" -m "Glassmorphic"` |
| `task pdf` | Compiles the versioned PDF document | `task pdf` |
| `task pdf -- -m <Model>` | Compiles PDF with specified theme model | `task pdf -- -m "Corporate"` |
| `task serve` | Starts local documentation server with AI/RAG on port 8000 | `task serve` |
| `task serve -- -l <Lang> -p <Port>` | Starts server with custom runtime and port | `task serve -- -l "PHP" -p 8080` |
| `task validate` | Validates internal markdown links and image assets | `task validate` |
| `task docs` | Runs complete build pipeline (validate + pdf + site) | `task docs` |
| `task clean` | Removes build directories (`dist/`) and temporary files | `task clean` |

---

### Makefile Commands (Alternative)

```bash
# Install dependencies
make install

# Web generation
make site LANG=py MODEL=glassmorphic
make site LANG=php MODEL=corporate
make site LANG=js MODEL=modern-dark

# PDF compilation
make pdf MODEL=corporate

# Local server
make serve LANG=py PORT=8000

# Validation & Cleanup
make validate
make clean
```

---

## 📖 Document Structuring Guide (`docs/`)

Place all your `.md` files in the `docs/` directory. The parser uses natural numeric sorting:

```
docs/
├── 00-capa.md               # 1st document (Cover)
├── 01-visao-geral.md        # 2nd document
├── 02-arquitetura/          # Creates Section "Arquitetura"
│   ├── 01-principios.md     # Subsection 2.1
│   └── 02-componentes.md    # Subsection 2.2
├── 03-guia-de-uso/          # Creates Section "Guia De Uso"
│   ├── 01-instalacao.md     # Subsection 3.1
│   └── 02-comandos-cli.md   # Subsection 3.2
└── 99-conclusao.md          # Final document
```

### Frontmatter Metadata (Optional)

You can add YAML metadata to the top of any document:

```markdown
---
title: "Custom Document Title"
description: "Brief summary of this section"
---

# Document Heading...
```

---

## 🖼️ Images & Visual Assets (`images/`)

1. Add your image files (`.png`, `.svg`, `.jpg`, `.webp`) to the `images/` directory.
2. Reference images inside Markdown using standard syntax:
   ```markdown
   ![Architecture Diagram](images/architecture-diagram.svg)
   ```
3. DocShell automatically normalizes paths so images resolve properly in both compiled PDFs and the web dist output (`dist/webpage/images/`).

---

## 🎨 Themes & Visual Models (`models/`)

Themes are located in `models/<model-name>/`:

| Theme | Key Features | Best Used For |
|---|---|---|
| **`glassmorphic`** | Frosted glass (*blur*), indigo/cyan gradients, Outfit/Inter typography | Modern developer portals, tech platforms |
| **`corporate`** | Navy blue and slate palette, structured layout | Executive reports, governance, audits |
| **`modern-dark`** | Deep obsidian background, high contrast, JetBrains Mono | API references, engineering docs |
| **`minimal`** | Clean monochrome typography, distraction-free | Formal specifications, rapid reading |

---

## ⚙️ Publication Settings (`publication/`)

Customize metadata and document parameters in `publication/publication.yml`:

```yaml
document:
  title: "DocShell - Technical Documentation"
  subtitle: "Architecture and Engineering Guide"
  author: "Matheus Ferreira"
  version: "1.0.0"
  release: "v1.0"
  output:
    pdf:
      basename: "DocShell-Technical-Documentation"
      directory: "dist/pdf"
    website:
      directory: "dist/webpage"
      default_runtime: "python"
      port: 8000

theme:
  default_model: "glassmorphic"

ai_assistant:
  enabled: true
  provider: "ollama"
  ollama:
    host: "http://127.0.0.1:11434"
    chat_model: "llama3.2"
```

---

## 🤖 RAG & AI Assistant

DocShell includes real-time search and an **Interactive AI Assistant Chatbot** on all web versions:
1. Splits all markdown documents into semantic chunks saved to `search_index.json`.
2. When a question is asked, the engine retrieves matching context using semantic/BM25 search.
3. The context is passed to **Ollama** (e.g., `llama3.2`) to synthesize an accurate answer with source citations.
4. If Ollama is offline, the interface seamlessly falls back to offline semantic excerpt search without breaking the UI.

---

## 🐳 Docker & Container Orchestration

Run the complete multi-service stack in isolated containers:

```bash
# Start all containers in background
task docker:up
# or
docker-compose up -d

# View live logs
task docker:logs

# Stop containers
task docker:down
```

---

## 📜 License

This project is licensed under the **Non-Commercial License**.

- ✅ **Allowed:** Personal, academic, research, copying, modification, and internal organization use.
- ❌ **Prohibited:** Commercial sale, commercial licensing, or direct commercial exploitation of this software or its derivative works.

See the [LICENSE](/LICENSE) file for the full legal terms.
