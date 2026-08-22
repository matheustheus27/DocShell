---
title: "Componentes do Sistema"
description: "Detalhamento dos módulos e componentes atômicos do GlassHub DocShell"
---

# Componentes do Sistema

Abaixo está a matriz de componentes e a hierarquia funcional do **GlassHub DocShell**:

![GlassHub DocShell Component Hierarchy](https://glass-hub-engine.vercel.app/api/table?title=GlassHub+DocShell+Component+Hierarchy&columns=Component,Atomic+Level,Tech+Stack,Function&rows=DocParser,Core+Atom,Python,Numeric+Doc+Parser;WebGenerators,Organism,Py+%2F+PHP+%2F+Node,Tripartite+Site+Builder;RAGEngine,Organism,FastAPI+%2F+VectorDB,Semantic+Search+%26+LLM;TranslationWorker,Organism,RabbitMQ+%2F+Gemma,Background+i18n;ThemeSystem,Atomic+CSS,Glassmorphic+Design,Tokens+%26+Cosmic+UI&theme=glass-dark)

## Descrição dos Módulos

### Módulo Core (`scripts/core/`)
- **`doc_parser.py`**: Localiza recursivamente todos os arquivos Markdown sob `docs/`, ordena numericamente pastas e arquivos, extrai títulos e gera o sumário estruturado.
- **`config_loader.py`**: Carrega e valida configurações de `publication/publication.yml` e modelos de `models/`.
- **`link_validator.py`**: Checa integridade de links internos e referências de imagens.
- **`rag_engine.py`**: Segmenta o texto em chunks, gera embeddings e responde consultas via LLM.
- **`datadog_reporter.py`**: Consolida eventos de telemetria e gera relatórios de auditoria em Markdown/JSON.

### Módulo RAG & Microsserviços (`scripts/rag/`)
- **`routers/`**: Rotas da API FastAPI para busca semântica, streaming WebSocket de chat (`/api/ws/chat`), documentação (`/api/docs`) e status de tradução (`/api/translations/status`).
- **`services/`**:
  - `translation_worker.py`: Orquestrador de tarefas assíncronas de tradução com chunking e enfileiramento no RabbitMQ.
  - `ollama_service.py`: Comunicação com instâncias Ollama locais (LLaMA 3.2 e TranslateGemma).
  - `cache_service.py`: Gerenciamento de cache em Redis com fallback transparente em SQLite.

### Módulo Worker Dedicado (`scripts/worker/`)
- **`worker.py`**: Consumidor RabbitMQ da fila `docshell_translation_tasks`, com política de 3 tentativas, backoff exponencial, deadline de 180s e Dead Letter Queue (`docshell_translation_dlq`).

### Módulos Geradores (`scripts/generators/`)
- **Python Generator**: Compila a estrutura tripartida (`dist/webpage/frontend`, `backend`, `worker`) e provê servidor FastAPI.
- **PHP Generator**: Renderiza templates em PHP com router integrado e busca indexada.
- **JavaScript Generator**: Construtor Node.js para empacotamento rápido com servidor Express e API.
