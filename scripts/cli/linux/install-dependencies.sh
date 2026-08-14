#!/usr/bin/env bash
# ==============================================================================
# DocShell Linux - Automated Dependency Installer
# Installs Python, Pandoc, TeX Live (XeLaTeX), Node.js, PHP, and pip requirements
# ==============================================================================
set -e
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

echo "================================================================="
echo "[DocShell] Automated Dependency Installer (Linux / macOS)"
echo "================================================================="

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get &>/dev/null; then
        echo "[+] Updating apt repositories and installing packages..."
        sudo apt-get update -y
        sudo apt-get install -y \
            python3 python3-pip python3-venv \
            pandoc texlive-xetex texlive-fonts-recommended texlive-plain-generic \
            nodejs npm php-cli git curl
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip pandoc texlive-xetex nodejs php-cli git curl
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy --noconfirm python python-pip pandoc texlive-core nodejs php git curl
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &>/dev/null; then
        echo "[+] Installing via Homebrew..."
        brew install python pandoc node php task git
        brew install --cask mactex-no-gui
    fi
fi

PYTHON=$(resolve_python)
if [ -f "$ROOT_DIR/scripts/requirements.txt" ]; then
    echo "[+] Installing Python requirements from scripts/requirements.txt..."
    $PYTHON -m pip install --upgrade pip --quiet || true
    $PYTHON -m pip install -r "$ROOT_DIR/scripts/requirements.txt"
fi

if command -v npm &>/dev/null; then
    if ! command -v mermaid-filter &>/dev/null; then
        echo "[+] Installing mermaid-filter globally for PDF diagram support..."
        npm install -g mermaid-filter --silent || true
    fi
fi

echo "================================================================="
echo "  [OK] Installation completed successfully!"
echo "================================================================="
