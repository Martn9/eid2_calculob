#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 no esta instalado."
    exit 1
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

venv/bin/python -m pip install --upgrade pip
venv/bin/python -m pip install -r requirements.txt

echo ""
echo "Entorno listo. Para ejecutar el programa:"
echo "  venv/bin/python main.py"
