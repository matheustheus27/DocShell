---
title: "Comandos CLI e Automação"
description: "Referência completa de comandos do Taskfile e Makefile"
---

# Comandos CLI e Automação

O DocShell suporta passagem de parâmetros flexíveis para escolha de runtime e modelo visual.

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

### 4. Validação e Limpeza
```bash
# Validar integridade de links e referências a imagens
task validate

# Limpar artefatos gerados
task clean
```

---

## Comandos com Makefile (Alternativa)

```bash
# Geração de PDF
make pdf MODEL=corporate

# Geração de Site Web
make site LANG=py MODEL=glassmorphic
make site LANG=php MODEL=corporate
make site LANG=js MODEL=modern-dark

# Executar servidor
make serve LANG=py

# Validação e limpeza
make validate
make clean
```
