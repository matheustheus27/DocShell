---
title: "Componentes do Sistema"
description: "Detalhamento dos módulos do DocShell"
---

# Componentes do Sistema

Abaixo está o diagrama representativo da arquitetura de componentes do DocShell:

![Diagrama de Arquitetura](images/architecture-diagram.svg)

## Descrição dos Módulos

### Módulo Core (`scripts/core/`)
- **`doc_parser.py`**: Localiza recursivamente todos os arquivos Markdown sob `docs/`, ordena numericamente pastas e arquivos, extrai títulos e gera o sumário estruturado.
- **`config_loader.py`**: Carrega e valida configurações de `publication/publication.yml` e modelos de `models/`.
- **`link_validator.py`**: Checa integridade de links internos e referências de imagens.
- **`rag_engine.py`**: Segmenta o texto em chunks, gera embeddings e responde consultas via LLM.

### Módulos Geradores (`scripts/generators/`)
- **Python Generator**: Compila o site em HTML estático e provê servidor com endpoint RAG FastAPI/HTTP.
- **PHP Generator**: Renderiza templates dinâmicos ou estáticos em PHP com busca e interface de chat IA.
- **JavaScript Generator**: Construtor Node.js para empacotamento rápido com servidor Express e API.
