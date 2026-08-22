---
title: "Docker e Orquestração de Containers"
description: "Execução simplificada em containers Docker no GlassHub DocShell"
---

# Docker e Orquestração de Containers

Todas as versões do **GlassHub DocShell** (Python, PHP, JavaScript e serviço de RAG) possuem imagens Docker otimizadas.

## Subindo o Ambiente por Linguagem (Compose Profiles)

O **GlassHub DocShell** suporta **Docker Compose Profiles** inteligentes, permitindo subir apenas os serviços da linguagem desejada em porta unificada (`8000`):

```bash
# Iniciar stack Python (Nginx + FastAPI + Worker + RabbitMQ + Redis + Ollama + Datadog)
task docker:python

# Iniciar stack PHP (PHP-FPM/Nginx + Redis + Ollama + Datadog)
task docker:php

# Iniciar stack Node.js (Express + Redis + Ollama + Datadog)
task docker:node

# Parar todos os contêineres
task docker:down
```

## Arquitetura de Contêineres

![GlassHub DocShell Container Services](https://glass-hub-engine.vercel.app/api/table?title=GlassHub+DocShell+Container+Orchestration&columns=Service,Exposed+Port,Image+%2F+Stack,Purpose&rows=docshell-web,8000,Nginx+Alpine,Frontend+Web+%26+Proxy;docshell-rag,8080,FastAPI+Python+3.12,API+Gateway+%26+RAG;docshell-worker,-,Python+3.12+Worker,TranslateGemma+Consumer;docshell-rabbitmq,5672+%2F+15672,RabbitMQ+Management,AMQP+Message+Broker&theme=glass-dark)

| Serviço | Porta Exposta | Stack / Imagem | Função |
| :--- | :---: | :--- | :--- |
| **`docshell-web`** | `8000` | Nginx Alpine / PHP / Node | Servidor web frontend e proxy reverso |
| **`docshell-rag`** | `8080` | FastAPI Python 3.12 | Gateway da API, streaming WebSocket e RAG |
| **`docshell-worker`** | - | Python 3.12 Worker | Processador de tradução assíncrona TranslateGemma |
| **`docshell-mongo`** | `27017` | MongoDB 7.0 | Banco de dados orientado a documentos e logs de auditoria |
| **`docshell-rabbitmq`** | `5672` / `15672` | RabbitMQ Management | Fila AMQP e orquestração de tarefas com DLQ |
| **`docshell-redis`** | `6379` | Redis 7 Alpine | Cache em memória para traduções e embeddings |
| **`docshell-ollama`** | `11434` | Ollama | Inferência local dos modelos LLaMA 3.2 e TranslateGemma |
| **`docshell-datadog`** | `8125` / `8126` | Datadog Agent 7 | Coleta de telemetria, APM, traces e DogStatsD |

## Relatório de Telemetria e Auditoria

Para auditar a saúde de todos os contêineres e métricas de desempenho:

```bash
task report
```

O comando exporta um relatório consolidado em `dist/reports/datadog_report.md`.
