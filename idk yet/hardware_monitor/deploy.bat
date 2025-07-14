@echo off
REM 🪖 HARDWARE MONITOR - SCRIPT DE DESPLIEGUE TÁCTICO PARA WINDOWS
REM Script para desplegar la aplicación a producción

echo 🪖 INICIANDO DESPLIEGUE TÁCTICO...

REM Verificar que estamos en el directorio correcto
if not exist "run.py" (
    echo [ERROR] No se encontró run.py. Ejecutar desde el directorio del proyecto.
    exit /b 1
)

REM Verificar que Docker está disponible
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no está instalado o no está en el PATH
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose no está instalado o no está en el PATH
    exit /b 1
)

REM Verificar archivo de variables de entorno
if not exist ".env" (
    echo [WARN] No se encontró archivo .env. Creando desde ejemplo...
    if exist "env.production.example" (
        copy env.production.example .env
        echo [WARN] Archivo .env creado. POR FAVOR EDITAR LAS VARIABLES DE ENTORNO ANTES DE CONTINUAR
        echo [WARN] Especialmente las claves secretas: SECRET_KEY, JWT_SECRET_KEY, ADMIN_PASSWORD
        pause
        exit /b 1
    ) else (
        echo [ERROR] No se encontró archivo de ejemplo de variables de entorno
        exit /b 1
    )
)

echo [INFO] Variables de entorno verificadas correctamente

REM Crear directorios necesarios
echo [INFO] Creando directorios necesarios...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "ssl" mkdir ssl

REM Detener contenedores existentes si están corriendo
echo [INFO] Deteniendo contenedores existentes...
docker-compose -f docker-compose.prod.yml down --remove-orphans

REM Limpiar imágenes antiguas
echo [INFO] Limpiando imágenes antiguas...
docker system prune -f

REM Construir imagen de producción
echo [INFO] Construyendo imagen de producción...
docker build -t hardware-monitor:prod .

REM Verificar que la imagen se construyó correctamente
if errorlevel 1 (
    echo [ERROR] Error al construir la imagen Docker
    exit /b 1
)

echo [INFO] Imagen construida correctamente

REM Iniciar servicios
echo [INFO] Iniciando servicios de producción...
docker-compose -f docker-compose.prod.yml up -d

REM Esperar a que los servicios estén listos
echo [INFO] Esperando a que los servicios estén listos...
timeout /t 30 /nobreak >nul

REM Verificar estado de los contenedores
echo [INFO] Verificando estado de los contenedores...
docker-compose -f docker-compose.prod.yml ps

REM Verificar health checks
echo [INFO] Verificando health checks...
for /l %%i in (1,1,10) do (
    curl -f -u "admin:admin" http://localhost:5000/api/health/basic >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Health check exitoso
        goto :health_ok
    ) else (
        echo [WARN] Health check falló, intento %%i/10
        timeout /t 10 /nobreak >nul
    )
)

:health_ok
REM Verificar endpoints críticos
echo [INFO] Verificando endpoints críticos...

REM Health check básico
curl -f -u "admin:admin" http://localhost:5000/api/health/basic >nul 2>&1
if not errorlevel 1 (
    echo ✅ Health check básico: OK
) else (
    echo ❌ Health check básico: FALLÓ
)

REM Métricas
curl -f http://localhost:5000/metrics >nul 2>&1
if not errorlevel 1 (
    echo ✅ Métricas: OK
) else (
    echo ❌ Métricas: FALLÓ
)

REM Verificar logs
echo [INFO] Verificando logs de la aplicación...
docker-compose -f docker-compose.prod.yml logs --tail=20 hardware-monitor

echo [INFO] 🪖 DESPLIEGUE TÁCTICO COMPLETADO
echo [INFO] 📊 Dashboard: http://localhost:5000
echo [INFO] 🔧 API: http://localhost:5000/api/stats
echo [INFO] 💚 Health Check: http://localhost:5000/api/health
echo [INFO] 📈 Métricas: http://localhost:5000/metrics

echo.
echo [INFO] COMANDOS ÚTILES:
echo   Ver logs: docker-compose -f docker-compose.prod.yml logs -f
echo   Reiniciar: docker-compose -f docker-compose.prod.yml restart
echo   Detener: docker-compose -f docker-compose.prod.yml down
echo   Ver estado: docker-compose -f docker-compose.prod.yml ps

pause 