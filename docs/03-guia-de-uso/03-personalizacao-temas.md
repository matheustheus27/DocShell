---
title: "Personalização de Temas e Modelos"
description: "Como criar e customizar modelos visuais no DocShell"
---

# Personalização de Temas e Modelos

A pasta `models/` é o local onde ficam armazenadas as definições visuais do DocShell. Cada subpasta representa um tema independente.

## Estrutura de um Modelo

```
models/meu-tema/
├── model.json        # Metadados e variáveis de cores do tema
├── web/
│   ├── style.css     # Estilos CSS específicos do site
│   └── script.js     # Comportamentos e animações JS
└── pdf/
    ├── header.tex    # Cabeçalho LaTeX com paleta de cores e tipografia
    └── style.css     # Estilos alternativos para geradores HTML-to-PDF
```

## Modelos Disponíveis Nativamente

1. **`glassmorphic`**: Design translúcido moderno, efeito de vidro fosco (`backdrop-filter: blur(12px)`), gradientes suaves em tons índigo e ciano.
2. **`corporate`**: Cores sóbrias (azul escuro, cinza ardósia, tipografia limpa), ideal para relatórios formais e auditorias.
3. **`modern-dark`**: Modo escuro profundo com destaque em código e bordas de contraste neon.
4. **`minimal`**: Layout suíço ultra-simplificado, focado em leitura rápida sem distrações visuais.
