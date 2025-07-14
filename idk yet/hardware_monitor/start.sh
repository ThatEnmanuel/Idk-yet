#!/bin/bash

echo "🚀 Iniciando Hardware Monitor..."
echo

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ No se encontró el entorno virtual"
    echo "Ejecuta: python install.py"
    exit 1
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Verificar si las dependencias están instaladas
python -c "import flask, psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencias no instaladas"
    echo "Ejecutando instalación automática..."
    pip install -r requirements.txt
fi

# Iniciar la aplicación
echo "📊 Iniciando Hardware Monitor..."
echo
echo "🌐 Dashboard: http://localhost:5000"
echo "🔧 API: http://localhost:5000/api/stats"
echo "💚 Health: http://localhost:5000/api/health"
echo
echo "Presiona Ctrl+C para detener"
echo

python run.py 