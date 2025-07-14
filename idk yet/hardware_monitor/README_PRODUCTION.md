# 🪖 HARDWARE MONITOR - GUÍA DE DESPLIEGUE A PRODUCCIÓN

> **MISIÓN CRÍTICA**: Despliegue seguro y optimizado para entornos de producción

## 🚨 PREPARACIÓN PREVIA

### 1. **Verificación de Requisitos**
```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar Python (para desarrollo local)
python --version
pip --version
```

### 2. **Configuración de Variables de Entorno**
```bash
# Copiar archivo de ejemplo
cp env.production.example .env

# EDITAR .env con valores seguros:
SECRET_KEY=tu-clave-secreta-super-segura-de-64-caracteres
JWT_SECRET_KEY=tu-jwt-secret-super-seguro-de-64-caracteres
ADMIN_USERNAME=admin
ADMIN_PASSWORD=tu-contraseña-super-segura
CORS_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

### 3. **Generación de Claves Seguras**
```bash
# Generar claves secretas seguras
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))"
```

## 🚀 DESPLIEGUE AUTOMATIZADO

### **Opción 1: Script de Despliegue (Recomendado)**

#### **Linux/macOS:**
```bash
# Hacer ejecutable el script
chmod +x deploy.sh

# Ejecutar despliegue
./deploy.sh
```

#### **Windows:**
```cmd
# Ejecutar script de despliegue
deploy.bat
```

### **Opción 2: Despliegue Manual**

#### **1. Construir Imagen**
```bash
docker build -t hardware-monitor:prod .
```

#### **2. Crear Directorios**
```bash
mkdir -p logs data ssl
```

#### **3. Iniciar Servicios**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### **4. Verificar Despliegue**
```bash
# Verificar contenedores
docker-compose -f docker-compose.prod.yml ps

# Verificar health check
curl -u admin:tu-contraseña http://localhost:5000/api/health/basic

# Verificar métricas
curl http://localhost:5000/metrics
```

## 🔧 CONFIGURACIÓN AVANZADA

### **Configuración de Nginx (Opcional)**
```bash
# Copiar configuración de Nginx
cp nginx.conf /etc/nginx/nginx.conf

# Configurar SSL (requerido para producción)
# Colocar certificados en ./ssl/
# - ssl/cert.pem (certificado público)
# - ssl/key.pem (clave privada)
```

### **Configuración de Redis (Opcional)**
```bash
# Para usar Redis externo, modificar .env:
CACHE_TYPE=redis
REDIS_URL=redis://tu-redis-server:6379/0
```

### **Configuración de Logs**
```bash
# Configurar rotación de logs
# En .env:
LOG_FILE=/app/logs/hardware_monitor.log
LOG_LEVEL=INFO
```

## 📊 MONITOREO POST-DESPLIEGUE

### **Endpoints de Verificación**
- **Health Check Básico**: `GET /api/health/basic`
- **Health Check Avanzado**: `GET /api/health` (requiere JWT)
- **Métricas Prometheus**: `GET /metrics`
- **Estado de Misión**: `GET /api/mission-status` (requiere JWT)

### **Comandos de Monitoreo**
```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f hardware-monitor

# Ver estado de contenedores
docker-compose -f docker-compose.prod.yml ps

# Ver uso de recursos
docker stats

# Verificar conectividad
curl -f http://localhost:5000/api/health/basic -u admin:tu-contraseña
```

### **Alertas y Métricas**
```bash
# Configurar alertas para:
# - CPU > 90%
# - Memoria > 90%
# - Disco > 90%
# - Health check fallido
# - Tiempo de respuesta > 5s
```

## 🔒 SEGURIDAD EN PRODUCCIÓN

### **Checklist de Seguridad**
- [ ] Cambiar todas las claves secretas por defecto
- [ ] Configurar HTTPS/TLS
- [ ] Configurar firewall
- [ ] Habilitar rate limiting
- [ ] Configurar CORS apropiadamente
- [ ] Implementar backup de logs
- [ ] Configurar monitoreo de seguridad

### **Configuración de Firewall**
```bash
# Permitir solo puertos necesarios
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 22/tcp   # SSH (solo si es necesario)
ufw enable
```

### **Configuración de SSL/TLS**
```bash
# Generar certificado auto-firmado (solo para pruebas)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Para producción, usar certificados de CA confiable
# (Let's Encrypt, etc.)
```

## 🚨 PROCEDIMIENTOS DE EMERGENCIA

### **Reinicio de Servicios**
```bash
# Reinicio completo
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Reinicio individual
docker-compose -f docker-compose.prod.yml restart hardware-monitor
```

### **Rollback de Versión**
```bash
# Volver a versión anterior
docker tag hardware-monitor:previous hardware-monitor:prod
docker-compose -f docker-compose.prod.yml up -d
```

### **Backup de Datos**
```bash
# Backup de logs
tar -czf backup-logs-$(date +%Y%m%d).tar.gz logs/

# Backup de configuración
tar -czf backup-config-$(date +%Y%m%d).tar.gz .env nginx.conf ssl/
```

## 📈 OPTIMIZACIÓN DE RENDIMIENTO

### **Configuración de Gunicorn**
```bash
# En Dockerfile, optimizar workers:
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--preload", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:create_app()"]
```

### **Configuración de Redis**
```bash
# Optimizar Redis para cache
redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

## 🔍 TROUBLESHOOTING

### **Problemas Comunes**

#### **1. Contenedor no inicia**
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs hardware-monitor

# Verificar variables de entorno
docker-compose -f docker-compose.prod.yml config
```

#### **2. Health check falla**
```bash
# Verificar conectividad interna
docker exec -it hw-monitor-prod curl http://localhost:5000/api/health/basic

# Verificar autenticación
docker exec -it hw-monitor-prod curl -u admin:tu-contraseña http://localhost:5000/api/health/basic
```

#### **3. Problemas de memoria**
```bash
# Verificar uso de memoria
docker stats hw-monitor-prod

# Ajustar límites en docker-compose.prod.yml
```

#### **4. Problemas de red**
```bash
# Verificar conectividad de red
docker exec -it hw-monitor-prod ping google.com

# Verificar puertos
netstat -tulpn | grep 5000
```

## 📞 SOPORTE

### **Información de Contacto**
- **Issues**: [GitHub Issues](https://github.com/your-repo/hardware_monitor/issues)
- **Documentación**: [Wiki](https://github.com/your-repo/hardware_monitor/wiki)

### **Información de Debug**
```bash
# Información del sistema
docker exec -it hw-monitor-prod python -c "
import platform, psutil
print(f'OS: {platform.system()}')
print(f'Python: {platform.python_version()}')
print(f'CPU: {psutil.cpu_count()} cores')
print(f'Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB')
"

# Logs de error
docker-compose -f docker-compose.prod.yml logs --tail=50 hardware-monitor | grep "ERROR\|CRITICAL"
```

---

**🪖 MANTÉNGASE VIGILANTE - LA SEGURIDAD ES NUESTRA PRIORIDAD** 🪖

*Hardware Monitor - Tactical Operations Center - Production Deployment Guide* 