---
title: "IA Generativa e RAG"
description: "Como funciona a busca semântica e o assistente de IA"
---

# Inteligência Artificial e RAG

O DocShell possui um assistente de IA integrado diretamente nas páginas da documentação web através do padrão **RAG (Retrieval-Augmented Generation)**.

## Arquitetura do RAG

```
   1. Documentos (.md) ---> Chunking (600 chars) ---> Vector Embeddings (nomic-embed-text)
                                                            |
   2. Pergunta do Usuario ---> Busca Vetorial / BM25 -------+
                                    |
                                    v
   3. Contexto Relevante + Prompt ---> LLM (Ollama / Llama 3.2) ---> Resposta com Citacoes
```

## Como Usar o Assistente no Site

1. Ao abrir qualquer versão do site (`http://localhost:8000`), clique no botão flutuante **"Assistente IA"** no canto inferior direito.
2. Digite sua pergunta em linguagem natural (ex: *"Como funciona a ordenação numérica dos arquivos no DocShell?"*).
3. O assistente consultará o índice da documentação e fornecerá a resposta sintetizada, acompanhada dos links das seções de onde a informação foi extraída.

## Configuração do Provedor de IA

Em `publication/publication.yml`, você pode personalizar o modelo do Ollama ou chave de API externa:

```yaml
ai_assistant:
  enabled: true
  provider: "ollama"
  ollama:
    host: "http://127.0.0.1:11434"
    chat_model: "llama3.2"
    embed_model: "nomic-embed-text"
```
