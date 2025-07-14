#!/bin/bash

# 🪖 HARDWARE MONITOR - SCRIPT DE DESPLIEGUE TÁCTICO
# Script para desplegar la aplicación a producción

set -e  # Salir en caso de error

echo "🪖 INICIANDO DESPLIEGUE TÁCTICO..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "run.py" ]; then
    log_error "No se encontró run.py. Ejecutar desde el directorio del proyecto."
    exit 1
fi

# Verificar que Docker está disponible
if ! command -v docker &> /dev/null; then
    log_error "Docker no está instalado o no está en el PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose no está instalado o no está en el PATH"
    exit 1
fi

# Verificar archivo de variables de entorno
if [ ! -f ".env" ]; then
    log_warn "No se encontró archivo .env. Creando desde ejemplo..."
    if [ -f "env.production.example" ]; then
        cp env.production.example .env
        log_warn "Archivo .env creado. POR FAVOR EDITAR LAS VARIABLES DE ENTORNO ANTES DE CONTINUAR"
        log_warn "Especialmente las claves secretas: SECRET_KEY, JWT_SECRET_KEY, ADMIN_PASSWORD"
        exit 1
    else
        log_error "No se encontró archivo de ejemplo de variables de entorno"
        exit 1
    fi
fi

# Verificar variables críticas
source .env

if [ "$SECRET_KEY" = "your-super-secret-production-key-change-this" ]; then
    log_error "SECRET_KEY debe ser cambiada en el archivo .env"
    exit 1
fi

if [ "$JWT_SECRET_KEY" = "your-jwt-production-secret-change-this" ]; then
    log_error "JWT_SECRET_KEY debe ser cambiada en el archivo .env"
    exit 1
fi

if [ "$ADMIN_PASSWORD" = "your-secure-production-password" ]; then
    log_error "ADMIN_PASSWORD debe ser cambiada en el archivo .env"
    exit 1
fi

log_info "Variables de entorno verificadas correctamente"

# Crear directorios necesarios
log_info "Creando directorios necesarios..."
mkdir -p logs data ssl

# Detener contenedores existentes si están corriendo
log_info "Deteniendo contenedores existentes..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Limpiar imágenes antiguas
log_info "Limpiando imágenes antiguas..."
docker system prune -f

# Construir imagen de producción
log_info "Construyendo imagen de producción..."
docker build -t hardware-monitor:prod .

# Verificar que la imagen se construyó correctamente
if [ $? -ne 0 ]; then
    log_error "Error al construir la imagen Docker"
    exit 1
fi

log_info "Imagen construida correctamente"

# Iniciar servicios
log_info "Iniciando servicios de producción..."
docker-compose -f docker-compose.prod.yml up -d

# Esperar a que los servicios estén listos
log_info "Esperando a que los servicios estén listos..."
sleep 30

# Verificar estado de los contenedores
log_info "Verificando estado de los contenedores..."
docker-compose -f docker-compose.prod.yml ps

# Verificar health checks
log_info "Verificando health checks..."
for i in {1..10}; do
    if curl -f -u "$ADMIN_USERNAME:$ADMIN_PASSWORD" http://localhost:5000/api/health/basic > /dev/null 2>&1; then
        log_info "Health check exitoso"
        break
    else
        log_warn "Health check falló, intento $i/10"
        sleep 10
    fi
done

# Verificar endpoints críticos
log_info "Verificando endpoints críticos..."

# Health check básico
if curl -f -u "$ADMIN_USERNAME:$ADMIN_PASSWORD" http://localhost:5000/api/health/basic > /dev/null 2>&1; then
    log_info "✅ Health check básico: OK"
else
    log_error "❌ Health check básico: FALLÓ"
fi

# Métricas
if curl -f http://localhost:5000/metrics > /dev/null 2>&1; then
    log_info "✅ Métricas: OK"
else
    log_error "❌ Métricas: FALLÓ"
fi

# Verificar logs
log_info "Verificando logs de la aplicación..."
docker-compose -f docker-compose.prod.yml logs --tail=20 hardware-monitor

log_info "🪖 DESPLIEGUE TÁCTICO COMPLETADO"
log_info "📊 Dashboard: http://localhost:5000"
log_info "🔧 API: http://localhost:5000/api/stats"
log_info "💚 Health Check: http://localhost:5000/api/health"
log_info "📈 Métricas: http://localhost:5000/metrics"

echo ""
log_info "COMANDOS ÚTILES:"
echo "  Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Reiniciar: docker-compose -f docker-compose.prod.yml restart"
echo "  Detener: docker-compose -f docker-compose.prod.yml down"
echo "  Ver estado: docker-compose -f docker-compose.prod.yml ps" 