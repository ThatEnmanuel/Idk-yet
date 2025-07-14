# Usar imagen base de Python con versión específica
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema y limpiar cache
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app \
    && chmod +x /app/run.py \
    && chmod +x /app/smoke_test.py

# Cambiar al usuario no-root
USER app

# Exponer puerto
EXPOSE 5000

# Variables de entorno por defecto para producción
ENV HOST=0.0.0.0
ENV PORT=5000
ENV DEBUG=False
ENV SECRET_KEY=change-me-in-production
ENV JWT_SECRET_KEY=change-jwt-secret-in-production
ENV LOG_LEVEL=INFO
ENV CACHE_TYPE=redis
ENV METRICS_ENABLED=true
ENV FORCE_HTTPS=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health/basic -u admin:admin || exit 1

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--preload", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:create_app()"] 