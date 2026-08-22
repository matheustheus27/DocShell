---
title: "Comandos CLI e Automação"
description: "Referência completa de comandos do Taskfile e Makefile no GlassHub DocShell"
---

# Comandos CLI e Automação

<p>
  <img src="https://glass-hub-engine.vercel.app/api/badge?label=CLI&text=Taskfile+%26+Makefile&theme=glass-dark&icon=terminal" alt="CLI" />
  <img src="https://glass-hub-engine.vercel.app/api/badge?label=Automation&text=Cross-Platform&theme=glass-dark&icon=gear" alt="Automation" />
</p>

O **GlassHub DocShell** suporta passagem de parâmetros flexíveis para escolha de runtime e modelo visual.

## Comandos com Taskfile

### 1. Geração de PDF
```bash
# Gerar PDF com o modelo padrão (definido em publication.yml)
task pdf

# Gerar PDF especificando modelo visual
task pdf -- -m "Corporate"
# ou
task pdf -- -m "Glassmorphic"
```

### 2. Geração de Site Web
```bash
# Gerar site em Python com tema padrão
task site -- -l "Py"

# Gerar site em PHP com tema Corporate
task site -- -l "PHP" -m "Corporate"

# Gerar site em JavaScript com tema Glassmorphic
task site -- -l "JS" -m "Glassmorphic"
```

### 3. Servidor Local e IA Assistente
```bash
# Iniciar servidor local na porta 8000
task serve

# Iniciar servidor específico (ex: PHP)
task serve -- -l "PHP"
```

### 4. Pipeline Completo de Build
```bash
# Executa build padrão (Python + Glassmorphic + Containers Python na porta 8000)
task build

# Build especificando linguagem e tema visual
task build -- -l "PHP" -m "Corporate"
task build -- -l "JS" -m "Glassmorphic"

# Build completo de todos os perfis e linguagens
task build -- --all
```

### 5. Containers Docker por Linguagem
```bash
# Iniciar stack Python (padrão)
task docker:python

# Iniciar stack PHP
task docker:php

# Iniciar stack Node.js
task docker:node

# Parar contêineres
task docker:down
```

### 6. Relatório e Auditoria Datadog
```bash
# Gerar relatório consolidado de telemetria e integridade
task report
```

### 7. Validação e Limpeza
```bash
# Validar integridade de links e referências a imagens
task validate

# Limpar artefatos gerados
task clean
```

---

## 📦 Pacote Standalone Autocontido (`dist/webpage/`)

A pasta `dist/webpage/` gerada pelo build é **100% autocontida e portátil**. Qualquer pessoa pode copiar apenas essa pasta para outro ambiente e executar:

```bash
cd dist/webpage
docker compose up -d
```

O compose local iniciará automaticamente o frontend, backend FastAPI, worker RabbitMQ, Redis e Ollama na porta **8000**.

---

## Comandos com Makefile (Alternativa)

```bash
# Geração de PDF
make pdf MODEL=corporate

# Geração de Site Web
make site LANG=py MODEL=glassmorphic
make site LANG=php MODEL=corporate
make site LANG=js MODEL=modern-dark

# Executar pipeline completo (Docs + PDF + Site + Docker)
make build
make build LANG=php MODEL=corporate
make build ALL=1

# Executar servidor local
make serve LANG=py

# Relatório Datadog
make report

# Containers Docker por profile
make docker-python
make docker-php
make docker-node
make docker-down

# Validação e limpeza
make validate
make clean
```
