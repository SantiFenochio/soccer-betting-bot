#!/bin/bash

# Archivo para ejecutar el bot en Linux/Mac

echo "======================================"
echo "  SOCCER BETTING BOT"
echo "======================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 no está instalado"
    echo "Por favor instala Python 3.8 o superior"
    exit 1
fi

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "Activando entorno virtual..."
    source venv/bin/activate
fi

# Ejecutar bot
echo "Iniciando bot..."
python3 main.py
