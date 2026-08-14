---
title: "Visão Geral e Objetivos"
description: "Contexto, motivação e capacidades centrais do DocShell"
---

# Visão Geral do Sistema

O **DocShell** foi projetado para resolver a complexidade de manter documentações sincronizadas, profissionais e facilmente consumíveis por diferentes perfis de usuários (engenheiros, gestores, clientes e novos integrantes de equipe).

```
   +-------------------------------------------------------------+
   |                     DOCSHELL ENGINE                         |
   |                                                             |
   |   Markdown Docs (docs/) ---> Smart Numeric Parser           |
   |                                  |                          |
   |            +---------------------+---------------------+    |
   |            |                                           |    |
   |            v                                           v    |
   |    PDF Generator Engine                       Web Generators |
   |  (Pandoc + XeLaTeX / HTML)              (Python / PHP / JS)  |
   |            |                                           |    |
   |            v                                           v    |
   |     dist/pdf/*.pdf                            dist/webpage/  |
   |                                                             |
   +-------------------------------------------------------------+
```

## Principais Recursos

1. **Ordenação Numérica Automática**:
   Ao organizar os arquivos em pastas como `01-introducao.md`, `02-arquitetura/01-visao.md`, o motor identifica a sequência numérica e monta automaticamente a árvore de navegação e o sumário (TOC).

2. **Sumário Funcional com Âncoras**:
   Tanto na versão PDF quanto no Website, o sumário gerado contém âncoras funcionais diretas para cada seção e subseção do documento.

3. **Múltiplos Runtimes Web (-l / --lang)**:
   Possibilidade de gerar e executar o site através de **Python**, **PHP** ou **JavaScript (Node.js)**, mantendo paridade visual e funcional.

4. **Modelos de Design Selecionáveis (-m / --model)**:
   Temas pré-configurados:
   - **Glassmorphic**: Visual refinado com vidro fosco (*frosted glass*), gradientes e efeito blur.
   - **Corporate**: Estilo sóbrio, executivo e estruturado.
   - **Modern-Dark**: Visual escuro de alto contraste voltado para desenvolvedores.
   - **Minimal**: Foco em leitura limpa e ultrarrápida.

5. **IA e RAG (Retrieval-Augmented Generation)**:
   Indexação dos textos da documentação para busca semântica e respostas inteligentes através de LLMs locais com Ollama ou APIs de IA.
