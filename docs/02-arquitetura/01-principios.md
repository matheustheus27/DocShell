---
title: "Princípios de Arquitetura"
description: "Pilares e diretrizes arquiteturais do DocShell"
---

# Princípios Arquiteturais

A arquitetura do DocShell é orientada aos seguintes princípios:

## 1. Modularidade e Arquitetura Atômica
Cada script possui responsabilidade única e bem delimitada. Essa separação impede scripts monolíticos e reduz falsos positivos de antivírus causados por padrões heurísticos complexos.

## 2. Paridade Multi-Plataforma
Garantia de funcionamento idêntico em ambientes **Windows** (PowerShell/CMD) e **Linux/macOS** (Bash/Zsh), orquestrados por `Taskfile.yml` e `Makefile`.

## 3. Desacoplamento de Conteúdo e Apresentação
O conteúdo em Markdown (`docs/`) é completamente desacoplado do motor de renderização (PDF/Web) e dos temas visuais (`models/`). O autor foca exclusivamente em escrever documentação clara.

## 4. Resolução Inteligente de Recursos
Imagens depositadas na pasta `images/` são resolvidas de forma relativa e copiadas automaticamente para os pacotes de distribuição sem perda de vínculos.
