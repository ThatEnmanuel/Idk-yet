# 🪖 HARDWARE MONITOR - TACTICAL OPS

> **MISIÓN**: Monitoreo táctico de hardware en tiempo real con defensa cibernética avanzada

[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-blue.svg)](https://flask.palletsprojects.com)
[![Security](https://img.shields.io/badge/Security-DEFCON--5-green.svg)](https://en.wikipedia.org/wiki/DEFCON)
[![Status](https://img.shields.io/badge/Status-OPERATIONAL-green.svg)](https://github.com)

## 🎯 OBJETIVO DE LA MISIÓN

Sistema de monitoreo de hardware con estética militar/táctica que proporciona:

- **Vigilancia en tiempo real** de CPU, RAM, Disco y Red
- **Alertas DEFCON** automáticas basadas en umbrales críticos
- **Autenticación JWT** con seguridad militar
- **Circuit Breaker** para resiliencia táctica
- **Logging estructurado** con códigos militares
- **UI Centro de Comando** con gauges militares
- **Health Checks** avanzados con estados OPERATIONAL/DEGRADED/OFFLINE

## 🚀 DESPLIEGUE TÁCTICO

### Requisitos del Sistema
```bash
# Sistema operativo compatible
- Windows 10/11
- Linux (Ubuntu 20.04+)
- macOS 10.15+

# Python 3.8+ requerido
python --version
```

### Instalación de Armas (Dependencias)
```bash
# Clonar repositorio
git clone https://github.com/your-repo/hardware_monitor.git
cd hardware_monitor

# Instalar dependencias tácticas
pip install -r requirements.txt

# Verificar instalación
python -c "import psutil, flask, jwt; print('✅ ARSENAL CARGADO')"
```

### Configuración de Misión
```bash
# Variables de entorno críticas
export FLASK_ENV=production
export SECRET_KEY="your-super-secret-military-key"
export JWT_SECRET_KEY="your-jwt-military-secret"

# Configuración de red táctica
export HOST=0.0.0.0
export PORT=5000
```

## ⚡ COMANDOS DE MISIÓN

### Inicio de Operaciones
```bash
# Iniciar servidor táctico
python run.py

# O con configuración personalizada
FLASK_ENV=production python run.py --host 0.0.0.0 --port 5000
```

### Verificación de Estado
```bash
# Health check básico
curl -u admin:admin http://localhost:5000/api/health/basic

# Health check avanzado (requiere JWT)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:5000/api/health

# Estado de misión militar
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:5000/api/mission-status
```

### Autenticación Táctica
```bash
# Obtener token JWT
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Usar token para acceso
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:5000/api/stats
```

## 🎖️ ARQUITECTURA MILITAR

### Componentes Tácticos

```
🪖 HARDWARE MONITOR - TACTICAL OPS
├── 🎯 Frontend (Centro de Comando)
│   ├── UI Militar con gauges
│   ├── Alertas DEFCON
│   ├── Mission Log
│   └── Radar sweep animations
├── 🔒 Backend (Cuartel General)
│   ├── SafeHardwareMonitor
│   ├── MilitaryCircuitBreaker
│   ├── MilitaryErrorHandler
│   └── JWT Authentication
├── 📊 APIs (Comunicaciones)
│   ├── /api/stats - Datos tácticos
│   ├── /api/mission-status - Estado de misión
│   ├── /api/mission-logs - Logs de operación
│   └── /api/health - Verificación de salud
└── 🛡️ Seguridad (Defensa)
    ├── Rate Limiting
    ├── Input Sanitization
    ├── Security Headers
    └── CORS Protection
```

### Códigos DEFCON

| Nivel | Estado | Descripción | Acción Requerida |
|-------|--------|-------------|------------------|
| **DEFCON-5** | 🟢 Normal | Operación normal | Monitoreo estándar |
| **DEFCON-4** | 🟡 Elevado | Atención aumentada | Verificación adicional |
| **DEFCON-3** | 🟠 Alto | Fuerza aérea lista en 15 min | Preparación táctica |
| **DEFCON-2** | 🔴 Crítico | Fuerzas listas en 6 horas | Acción inmediata |
| **DEFCON-1** | ⚫ Máximo | Guerra nuclear inminente | Evacuación inmediata |

## 🔧 CONFIGURACIÓN TÁCTICA

### Archivo de Configuración (`config.py`)
```python
class MilitaryConfig:
    # Configuración de seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY', 'military-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-military-secret')
    
    # Configuración de red
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Umbrales de alerta
    CPU_THRESHOLD = 80
    MEMORY_THRESHOLD = 85
    DISK_THRESHOLD = 90
    
    # Configuración de rate limiting
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = "memory://"
```

### Variables de Entorno Críticas
```bash
# Seguridad
SECRET_KEY=your-super-secret-military-key
JWT_SECRET_KEY=your-jwt-military-secret

# Red
HOST=0.0.0.0
PORT=5000

# Monitoreo
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

## 🧪 PRUEBAS TÁCTICAS

### Smoke Tests
```bash
# Ejecutar pruebas de humo
python smoke_test.py

# Verificar endpoints críticos
python -m pytest tests/ -v
```

### Tests de Integración
```bash
# Tests completos
python -m pytest tests/test_integration.py -v

# Tests de seguridad
python -m pytest tests/test_security.py -v
```

### Tests de Performance
```bash
# Test de carga
python -m pytest tests/test_performance.py -v

# Benchmark de endpoints
python benchmark.py
```

## 🐳 DESPLIEGUE CONTAINERIZADO

### Docker Táctico
```bash
# Construir imagen militar
docker build -t hardware-monitor-military .

# Ejecutar contenedor
docker run -d \
  --name tactical-ops \
  -p 5000:5000 \
  -e SECRET_KEY="your-secret" \
  hardware-monitor-military

# Con Docker Compose
docker-compose up -d
```

### Docker Compose (Operaciones Complejas)
```yaml
version: '3.8'
services:
  tactical-ops:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## 📊 MONITOREO Y MÉTRICAS

### Endpoints de Monitoreo
- `GET /api/health` - Estado de salud avanzado
- `GET /api/mission-status` - Estado de misión militar
- `GET /api/metrics` - Métricas Prometheus
- `GET /api/mission-logs` - Logs de operación

### Métricas Clave
- **CPU Usage**: Porcentaje de uso del procesador
- **Memory Usage**: Uso de memoria RAM
- **Disk Usage**: Uso de espacio en disco
- **Network I/O**: Tráfico de red
- **Response Time**: Tiempo de respuesta de APIs
- **Error Rate**: Tasa de errores

## 🔒 SEGURIDAD MILITAR

### Características de Seguridad
- ✅ **JWT Authentication** - Autenticación basada en tokens
- ✅ **Rate Limiting** - Protección contra ataques de fuerza bruta
- ✅ **Input Sanitization** - Sanitización de entradas
- ✅ **Security Headers** - Headers de seguridad HTTP
- ✅ **CORS Protection** - Protección contra CORS
- ✅ **Error Handling** - Manejo seguro de errores

### Mejores Prácticas
1. **Cambiar credenciales por defecto** en producción
2. **Usar HTTPS** en entornos de producción
3. **Configurar firewall** apropiadamente
4. **Monitorear logs** regularmente
5. **Actualizar dependencias** frecuentemente

## 🚨 PROCEDIMIENTOS DE EMERGENCIA

### Sistema Degradado (DEFCON-3)
```bash
# Verificar logs
tail -f logs/app.log | grep "DEFCON-3"

# Reiniciar servicios críticos
docker-compose restart tactical-ops

# Verificar health checks
curl http://localhost:5000/api/health
```

### Sistema Crítico (DEFCON-1)
```bash
# Evacuación inmediata
docker-compose down

# Backup de datos críticos
tar -czf backup-$(date +%Y%m%d).tar.gz logs/ data/

# Reinicio completo
docker-compose up -d --force-recreate
```

## 🤝 CONTRIBUCIÓN TÁCTICA

### Protocolo de Contribución
1. **Fork** el repositorio
2. **Crear** rama de feature (`git checkout -b feature/tactical-improvement`)
3. **Commit** cambios (`git commit -am 'Add tactical feature'`)
4. **Push** a la rama (`git push origin feature/tactical-improvement`)
5. **Crear** Pull Request

### Estándares de Código
- **Python**: PEP 8 compliance
- **JavaScript**: ESLint configuration
- **Documentación**: Docstrings en español
- **Tests**: Cobertura mínima 80%

## 📞 SOPORTE TÁCTICO

### Canales de Comunicación
- **Issues**: [GitHub Issues](https://github.com/your-repo/hardware_monitor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/hardware_monitor/discussions)
- **Wiki**: [Documentación táctica](https://github.com/your-repo/hardware_monitor/wiki)

### Reporte de Bugs
```bash
# Información del sistema
python -c "import platform, psutil; print(f'OS: {platform.system()}'); print(f'Python: {platform.python_version()}'); print(f'CPU: {psutil.cpu_count()} cores')"

# Logs de error
tail -n 50 logs/app.log | grep "ERROR\|CRITICAL"
```

## 📄 LICENCIA MILITAR

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

**🪖 MANTÉNGASE VIGILANTE - LA SEGURIDAD ES NUESTRA PRIORIDAD** 🪖

*Hardware Monitor - Tactical Operations Center* 