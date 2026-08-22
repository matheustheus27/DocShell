---
title: "IA Generativa e RAG"
description: "Como funciona a busca semântica e o assistente de IA no GlassHub DocShell"
---

# Inteligência Artificial e RAG

<p>
  <img src="https://glass-hub-engine.vercel.app/api/badge?label=AI+Engine&text=RAG+%2B+Ollama&theme=glass-dark&icon=sparkles" alt="AI Engine" />
  <img src="https://glass-hub-engine.vercel.app/api/badge?label=Model&text=LLaMA+3.2&theme=glass-dark&icon=gear" alt="Model" />
  <img src="https://glass-hub-engine.vercel.app/api/badge?label=Translation&text=TranslateGemma&theme=glass-dark&icon=sparkles" alt="Translation" />
</p>

O **GlassHub DocShell** possui um assistente de IA integrado diretamente nas páginas da documentação web através do padrão **RAG (Retrieval-Augmented Generation)**.

## Arquitetura do RAG

```mermaid
flowchart TD
    subgraph Indexing [" 1. Ingestão & Embeddings "]
        A["📄 Documentos (.md)"] --> B["✂️ Chunking\n(600 chars)"]
        B --> C["🧠 Vector Embeddings\n(nomic-embed-text)"]
    end

    subgraph Retrieval [" 2. Recuperação & Busca "]
        D["👤 Pergunta do Usuário"] --> E["🔍 Busca Vetorial / BM25"]
        C -. Ingestão .-x E
    end

    subgraph Generation [" 3. Síntese & Geração "]
        E --> F["📝 Contexto Relevante + Prompt"]
        F --> G["🦙 LLM\n(Ollama / Llama 3.2)"]
        G --> H["💬 Resposta com Citações"]
    end

    %% Fundo transparente adaptável ao Dark/Light mode
    style Indexing fill:none,stroke-dasharray: 4 4,stroke-width:1.5px
    style Retrieval fill:none,stroke-dasharray: 4 4,stroke-width:1.5px
    style Generation fill:none,stroke-dasharray: 4 4,stroke-width:1.5px
```

## Como Usar o Assistente no Site

1. Ao abrir qualquer versão do site (`http://localhost:8000`), clique no botão flutuante **"Assistente IA"** no canto inferior direito.
2. Digite sua pergunta em linguagem natural (ex: *"Como funciona a ordenação numérica dos arquivos no DocShell?"*).
3. O assistente consultará o índice da documentação e fornecerá a resposta sintetizada via streaming WebSocket em tempo real, acompanhada de badges clicáveis com links diretos para as seções de onde a informação foi extraída.
4. **Persistência de Histórico**: As conversas ficam salvas no armazenamento local do navegador e só são reiniciadas se o usuário clicar no botão de lixeira (`🗑️`).

---

## 🌐 Tradução Dinâmica On-Demand (TranslateGemma)

O DocShell possui um pipeline de internacionalização inteligente:
1. Ao trocar o idioma no seletor do cabeçalho (ex: `en-US`, `es-ES`, `fr-FR`), o frontend verifica se a tradução completa já existe em cache (Redis ou SQLite).
2. Caso ainda não exista, a requisição é enfileirada no **RabbitMQ** para o **`docshell-worker`**.
3. O worker processa os documentos utilizando o modelo **`TranslateGemma`** no Ollama, dividindo textos extensos em blocos lógicos (`split_markdown_into_blocks`) para garantir 100% de integridade sem cortes de texto.
4. Enquanto a tradução ocorre em segundo plano, um **Chip Flutuante Minimizável** no canto inferior esquerdo exibe o progresso em tempo real (`🔄 en-US (45%)`), permitindo que o leitor continue navegando sem obstruções.

---

## Configuração do Provedor de IA

Em `publication/publication.yml`, você pode personalizar os modelos utilizados:

```yaml
ai_assistant:
  enabled: true
  provider: "ollama"
  ollama:
    host: "http://127.0.0.1:11434"
    chat_model: "llama3.2"
    embed_model: "nomic-embed-text"
    translate_model: "translategemma"
```
