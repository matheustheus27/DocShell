---
title: "Personalização de Temas e Modelos"
description: "Como criar e customizar modelos visuais e a Arquitetura Atômica no GlassHub DocShell"
---

# Personalização de Temas e Modelos

<p>
  <img src="https://glass-hub-engine.vercel.app/api/badge?label=Design&text=Glassmorphic+Atomic+Tokens&theme=glass-dark&icon=palette" alt="Design System" />
  <img src="https://glass-hub-engine.vercel.app/api/badge?label=Engine&text=GlassHub+Engine+SVG&theme=glass-dark&icon=sparkles" alt="Engine" />
</p>

A pasta `models/` é o local onde ficam armazenadas as definições visuais do **GlassHub DocShell**. Cada subpasta representa um tema independente baseado em **Arquitetura Atômica**.

## Estrutura de um Modelo

```text
🎨 models/meu-tema/
├── ⚙️ model.json       # Metadados e variáveis de cores do tema
├── 🌐 web/
│   ├── 🎨 style.css     # Estilos CSS (Atoms, Molecules, Organisms, Templates)
│   └── ⚡ script.js    # Comportamentos e animações JS
└── 📕 pdf/
    ├── 📑 header.tex    # Cabeçalho LaTeX com paleta de cores e tipografia
    └── 🎨 style.css     # Estilos alternativos para geradores HTML-to-PDF
```

## Modelos Disponíveis Nativamente

1. **`glassmorphic`**: Design translúcido cósmico (`backdrop-filter: blur(16px)`), gradientes neon cyan/violeta, reflexos de vidro (`glass-sheen`), bordas iluminadas e suporte a componentes dinâmicos do **GlassHub Engine**.
2. **`corporate`**: Cores sóbrias (azul escuro, cinza ardósia, tipografia limpa), ideal para relatórios formais e auditorias.
3. **`modern-dark`**: Modo escuro profundo com destaque em código e bordas de contraste neon.
4. **`minimal`**: Layout suíço ultra-simplificado, focado em leitura rápida sem distrações visuais.
