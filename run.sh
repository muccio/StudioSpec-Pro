#!/usr/bin/env bash
# StudioSpec Pro - macOS & Linux Launcher
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Check for python3
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v uv >/dev/null 2>&1; then
    PY_CMD="uv run python"
else
    echo "Errore: Python 3 non trovato. Installa Python per avviare StudioSpec Pro."
    exit 1
fi

echo "🎛️ Avvio di StudioSpec Pro..."
$PY_CMD main.py "$@"
