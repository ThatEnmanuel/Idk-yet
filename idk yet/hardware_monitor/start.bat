@echo off
echo 🚀 Iniciando Hardware Monitor...
echo.

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo ❌ No se encontró el entorno virtual
    echo Ejecuta: python install.py
    pause
    exit /b 1
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate

REM Verificar si las dependencias están instaladas
python -c "import flask, psutil" 2>nul
if errorlevel 1 (
    echo ❌ Dependencias no instaladas
    echo Ejecutando instalación automática...
    pip install -r requirements.txt
)

REM Iniciar la aplicación
echo 📊 Iniciando Hardware Monitor...
echo.
echo 🌐 Dashboard: http://localhost:5000
echo 🔧 API: http://localhost:5000/api/stats
echo 💚 Health: http://localhost:5000/api/health
echo.
echo Presiona Ctrl+C para detener
echo.

python run.py

pause 