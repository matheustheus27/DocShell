---
title: "Fluxo de Execução e Dados"
description: "Como os dados transitam desde a escrita até a distribuição final no GlassHub DocShell"
---

# Fluxo de Execução e Dados

<p>
  <img src="https://glass-hub-engine.vercel.app/api/badge?label=Pipeline&text=Deterministic+Data+Flow&theme=glass-dark&icon=sparkles" alt="Pipeline" />
  <img src="https://glass-hub-engine.vercel.app/api/badge?label=Engine&text=GlassHub+DocShell&theme=glass-dark&icon=glasshub" alt="Engine" />
</p>

O pipeline do **GlassHub DocShell** segue um fluxo determinístico dividido em etapas:

## 1. Descoberta e Parsing (Discovery Phase)
O parser examina a raiz `docs/`, lê a numeração das pastas (ex: `01-`, `02-`) e arquivos, remove prefixos numéricos para apresentação amigável e extrai metadados do cabeçalho YAML.

## 2. Consolidação e Sumário (TOC Building)
Gera `publication/documento-completo.md` concatenando os documentos com âncoras automáticas padronizadas (`#secao-slug`), inserindo quebras de página controladas e gerando a árvore de sumário no topo ou na barra lateral.

## 3. Aplicação do Modelo Visual (Theming)
Os tokens do modelo selecionado (ex: `glassmorphic`, `corporate`) são injetados nos templates CSS/JS do site e nos cabeçalhos TeX/CSS do PDF.

## 4. Compilação e Distribuição (Build Phase)
- **PDF**: Compilado para `dist/pdf/{basename}-{release}.pdf`.
- **Webpage**: Compilado para `dist/webpage/` com ativos estáticos, imagens, índice de busca e widget de IA com streaming WebSocket.
