"""
Inicialización de la aplicación Flask
"""

from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import logging
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_compress import Compress
from flask_caching import Cache
from prometheus_flask_exporter import PrometheusMetrics

# Cargar variables de entorno
load_dotenv()

def create_app():
    """Factory function para crear la aplicación Flask"""
    
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'CAMBIA_ESTO')
    
    # Configuración de cache
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    app.config['CACHE_THRESHOLD'] = 1000  # Máximo 1000 items
    app.config['CACHE_KEY_PREFIX'] = 'hw_monitor'
    
    # Configurar logging global
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE', 'hardware_monitor.log')
    
    # Configurar logging estructurado
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # Habilitar CORS con configuración específica
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    if not CORS_ORIGINS or CORS_ORIGINS == ['']:
        CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']  # Fallback para desarrollo
    
    CORS(app, resources={
        r"/api/*": {
            "origins": CORS_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Inicializar JWT
    jwt = JWTManager(app)

    # Inicializar Rate Limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["100 per minute", "10 per second"],
        storage_uri="memory://"
    )
    
    # Inicializar Headers de Seguridad
    force_https = os.getenv('FORCE_HTTPS', 'false').lower() == 'true'
    Talisman(
        app,
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
            'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
            'img-src': ["'self'", "data:", "https:"],
        },
        force_https=force_https
    )
    
    # Inicializar Compresión
    Compress(app)
    
    # Inicializar Cache
    cache = Cache(app)
    
    # Inicializar Métricas Prometheus
    metrics = PrometheusMetrics(app, path='/metrics')

    # Handlers de errores JWT
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        from flask import jsonify
        return jsonify({'error': 'Token de acceso requerido', 'success': False}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        from flask import jsonify
        return jsonify({'error': 'Token inválido', 'success': False}), 422

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({'error': 'Token expirado', 'success': False}), 401
    
    # Middleware para trazabilidad de requests
    @app.before_request
    def before_request():
        from flask import request, g
        request_id = str(uuid.uuid4())
        g.request_id = request_id
        logging.info(f"Request {request_id} iniciado: {request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        from flask import g
        request_id = getattr(g, 'request_id', 'unknown')
        logging.info(f"Request {request_id} completado: {response.status_code}")
        response.headers['X-Request-ID'] = request_id
        return response
    
    # Registrar blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app 