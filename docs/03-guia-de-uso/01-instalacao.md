---
title: "Guia de Instalação e Pré-requisitos"
description: "Como preparar o ambiente para utilizar o GlassHub DocShell"
---

# Guia de Instalação e Pré-requisitos

O **GlassHub DocShell** foi construído para funcionar com o mínimo de fricção. Escolha o seu ambiente de desenvolvimento habitual.

## Pré-requisitos Básicos

![GlassHub DocShell Prerequisites Matrix](https://glass-hub-engine.vercel.app/api/table?title=GlassHub+DocShell+Prerequisites&columns=Tool,Purpose,Windows+Install,Linux+Install&rows=Taskfile,CLI+Automation,winget+install+Task.Task,curl+install.sh;Python+3.12,Runtime+%26+Parser,winget+install+Python,apt+install+python3;Docker,Containerization,winget+install+Docker,apt+install+docker.io;Pandoc,PDF+Compiler,winget+install+Pandoc,apt+install+pandoc&theme=glass-dark)

| Ferramenta | Uso | Instalação no Windows | Instalação no Linux (Ubuntu/Debian) |
|---|---|---|---|
| **Taskfile** (Recomendado) | Automação CLI | `winget install Task.Task` | `sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d` |
| **Make** (Opcional) | Automação alternativa | `winget install GnuWin32.Make` | `sudo apt install make` |
| **Python** | Runtime & Parser | `winget install Python.Python.3.12` | `sudo apt install python3 python3-pip` |
| **Node.js** (Opcional) | Runtime JS | `winget install OpenJS.NodeJS` | `sudo apt install nodejs npm` |
| **PHP** (Opcional) | Runtime PHP | `winget install PHP.PHP` | `sudo apt install php php-cli` |
| **Pandoc & MiKTeX/XeLaTeX** | Geração de PDF | `winget install JohnMacFarlane.Pandoc MiKTeX.MiKTeX` | `sudo apt install pandoc texlive-xetex` |
| **Docker** | Execução isolada | `winget install Docker.DockerDesktop` | `sudo apt install docker.io docker-compose` |

## Clonando e Iniciando

```bash
git clone https://github.com/matheustheus27/GlassHubDocShell.git
cd GlassHubDocShell

# Listar tarefas disponíveis
task --list
```
