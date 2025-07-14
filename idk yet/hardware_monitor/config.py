"""
Configuración de la aplicación Hardware Monitor
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    
    # Configuración del servidor
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Configuración de seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'CAMBIA_ESTO')
    
    # Configuración de rate limiting
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per minute')
    RATE_LIMIT_STRICT = os.getenv('RATE_LIMIT_STRICT', '10 per second')
    RATE_LIMIT_LOGIN = os.getenv('RATE_LIMIT_LOGIN', '5 per minute')
    
    # Configuración de cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_KEY_PREFIX = os.getenv('CACHE_KEY_PREFIX', 'hardware_monitor')
    
    # Configuración de compresión
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml',
        'application/json', 'application/javascript'
    ]
    COMPRESS_LEVEL = int(os.getenv('COMPRESS_LEVEL', 6))
    COMPRESS_MIN_SIZE = int(os.getenv('COMPRESS_MIN_SIZE', 500))
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.getenv('LOG_FILE', 'hardware_monitor.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # Configuración de la aplicación
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 5000))
    MAX_DATA_POINTS = int(os.getenv('MAX_DATA_POINTS', 20))
    
    # Configuración de reintentos
    MAX_RETRIES_CRITICAL = int(os.getenv('MAX_RETRIES_CRITICAL', '3'))
    MAX_RETRIES_NORMAL = int(os.getenv('MAX_RETRIES_NORMAL', '2'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '1'))
    USE_EXPONENTIAL_BACKOFF = os.getenv('USE_EXPONENTIAL_BACKOFF', 'true').lower() == 'true'
    
    # Configuración de métricas
    METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
    METRICS_PATH = os.getenv('METRICS_PATH', '/metrics')
    
    # Configuración de health checks
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', 30))
    HEALTH_CHECK_TIMEOUT = int(os.getenv('HEALTH_CHECK_TIMEOUT', 5))
    
    # Umbrales de alerta
    CPU_ALERT_THRESHOLD = float(os.getenv('CPU_ALERT_THRESHOLD', 90.0))
    MEMORY_ALERT_THRESHOLD = float(os.getenv('MEMORY_ALERT_THRESHOLD', 90.0))
    DISK_ALERT_THRESHOLD = float(os.getenv('DISK_ALERT_THRESHOLD', 90.0))
    
    # Configuración de CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',')
    CORS_METHODS = ['GET', 'POST', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization']
    
    # Configuración de seguridad adicional
    FORCE_HTTPS = os.getenv('FORCE_HTTPS', 'false').lower() == 'true'
    CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
        'img-src': ["'self'", "data:", "https:"],
    }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    CACHE_TYPE = 'simple'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    CACHE_TYPE = 'redis'  # Cambiar a Redis en producción
    FORCE_HTTPS = True
    
    def __init__(self):
        super().__init__()
        # Validar variables críticas en producción
        if self.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError('SECRET_KEY debe ser cambiada en producción')
        if self.JWT_SECRET_KEY == 'CAMBIA_ESTO':
            raise ValueError('JWT_SECRET_KEY debe ser cambiada en producción')

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    CACHE_TYPE = 'simple'
    WTF_CSRF_ENABLED = False

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Obtener configuración por nombre"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default']) 