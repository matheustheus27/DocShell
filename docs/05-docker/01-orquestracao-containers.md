---
title: "Docker e Orquestração de Containers"
description: "Execução simplificada em containers Docker"
---

# Docker e Orquestração de Containers

Todas as versões do DocShell (Python, PHP, JavaScript e serviço de RAG) possuem imagens Docker otimizadas.

## Subindo o Ambiente Completo

Para iniciar o servidor web juntamente com o serviço RAG e Ollama:

```bash
docker-compose up -d
```

## Serviços Disponíveis

| Serviço | Porta | Descrição |
|---|---|---|
| `web-python` | `8000` | Site documentação em Python com API RAG integrada |
| `web-php` | `8001` | Site documentação em PHP com busca e chat |
| `web-node` | `8002` | Site documentação em Node.js com Express |
| `rag-service` | `8080` | Microsserviço Python FastAPI de embeddings e busca vetorial |
| `ollama` | `11434` | Instância local do Ollama para inferência de LLMs |

## Comandos Docker via Taskfile

```bash
# Subir containers em background
task docker:up

# Ver logs
task docker:logs

# Parar containers
task docker:down
```
