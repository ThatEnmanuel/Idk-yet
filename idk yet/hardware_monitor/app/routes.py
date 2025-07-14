"""
Rutas de la aplicación
"""

import logging
import time
import psutil
import os
from functools import wraps
from flask import Blueprint, render_template, jsonify, request, g, current_app
from flask_jwt_extended import create_access_token, jwt_required
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from flask_httpauth import HTTPBasicAuth
from app.utils import get_cpu_usage, get_ram_usage, get_disk_usage, get_network_stats, sanitize_output, military_error_handler
import os

# Crear blueprint principal
main_bp = Blueprint('main', __name__)

# Autenticación básica opcional
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    """Verificar credenciales para autenticación básica"""
    # Usar variables de entorno para credenciales
    admin_user = os.getenv('ADMIN_USERNAME', 'admin')
    admin_pass = os.getenv('ADMIN_PASSWORD', 'admin')
    return username == admin_user and password == admin_pass

# Decorador para manejo global de errores militar
def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Usar MilitaryErrorHandler para manejo de errores
            error_info = military_error_handler.handle_error(e, {
                'function': f.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            })
            response_data, status_code = military_error_handler.create_military_response(error_info)
            return jsonify(response_data), status_code
    return decorated_function

@main_bp.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')

@main_bp.route('/api/login', methods=['POST'])
@handle_exceptions
def login():
    """Endpoint de login para obtener token JWT con validación mejorada"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos JSON requeridos', 'success': False}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos', 'success': False}), 400
    
    # Validar longitud y caracteres
    if len(username) > 50 or len(password) > 100:
        return jsonify({'error': 'Credenciales demasiado largas', 'success': False}), 400
    
    # Usar variables de entorno para credenciales
    admin_user = os.getenv('ADMIN_USERNAME', 'admin')
    admin_pass = os.getenv('ADMIN_PASSWORD', 'admin')
    
    if username == admin_user and password == admin_pass:
        access_token = create_access_token(identity=username)
        return jsonify({
            'access_token': access_token,
            'success': True
        }), 200
    else:
        return jsonify({
            'error': 'Credenciales inválidas',
            'success': False
        }), 401

@main_bp.route('/api/stats')
@jwt_required()
@handle_exceptions
def api_stats():
    """API para obtener estadísticas de hardware con sanitización"""
    try:
        start_time = time.time()
        
        # Obtener datos de hardware
        cpu_usage = get_cpu_usage()
        ram_usage = get_ram_usage()
        try:
            disk_usage = get_disk_usage()
        except Exception as disk_error:
            disk_usage = {'usage': -1, 'error': str(disk_error), 'timestamp': time.time()}
            logging.error(f"Error obteniendo disk usage en stats: {disk_error}")
        network_stats = get_network_stats()
        
        # Sanitizar outputs
        cpu_usage = sanitize_output(cpu_usage)
        ram_usage = sanitize_output(ram_usage)
        disk_usage = sanitize_output(disk_usage)
        network_stats = sanitize_output(network_stats)
        
        # Calcular tiempo de respuesta
        response_time = round((time.time() - start_time) * 1000, 2)
        
        # Retornar datos en formato JSON con request_id
        return jsonify({
            'cpu': cpu_usage,
            'ram': ram_usage,
            'disk': disk_usage,
            'network': network_stats,
            'request_id': getattr(g, 'request_id', 'unknown'),
            'response_time_ms': response_time,
            'success': True
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'request_id': getattr(g, 'request_id', 'unknown'),
            'success': False
        }), 500

@main_bp.route('/api/health')
@jwt_required()
@handle_exceptions
def api_health():
    """Endpoint de salud avanzado con métricas detalladas"""
    try:
        # Métricas básicas del sistema
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Usar la función mejorada de disco
        try:
            disk_data = get_disk_usage()
            disk_percent = disk_data.get('usage', -1)
        except Exception as disk_error:
            disk_percent = -1
            logging.error(f"Error obteniendo disk usage en health: {disk_error}")
        
        # Información del proceso
        process = psutil.Process()
        
        # Métricas de red
        net_io = psutil.net_io_counters()
        
        health_data = {
            'status': 'healthy',
            'timestamp': time.time(),
            'request_id': getattr(g, 'request_id', 'unknown'),
            'system': {
                'cpu_usage': round(cpu_percent, 1),
                'memory_usage': round(memory.percent, 1),
                'disk_usage': disk_percent,
                'uptime_seconds': time.time() - psutil.boot_time()
            },
            'application': {
                'memory_mb': round(process.memory_info().rss / 1024 / 1024, 2),
                'cpu_percent': round(process.cpu_percent(), 1),
                'threads': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections())
            },
            'network': {
                'bytes_sent_mb': round(net_io.bytes_sent / 1024 / 1024, 2),
                'bytes_recv_mb': round(net_io.bytes_recv / 1024 / 1024, 2),
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            },
            'checks': {
                'cpu_ok': cpu_percent < 90,
                'memory_ok': memory.percent < 90,
                'disk_ok': disk_percent >= 0 and disk_percent < 90,
                'process_ok': process.is_running()
            }
        }
        
        if disk_percent == -1:
            health_data['system']['disk_error'] = 'No se pudo obtener el uso de disco.'
            
        # Determinar estado general
        all_checks_ok = all(health_data['checks'].values())
        health_data['status'] = 'healthy' if all_checks_ok else 'degraded'
        return jsonify(health_data)
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'request_id': getattr(g, 'request_id', 'unknown'),
            'timestamp': time.time()
        }), 500

@main_bp.route('/api/health/basic')
@auth.login_required
def api_health_basic():
    """Endpoint de salud básico con autenticación HTTP Basic"""
    return jsonify({
        'status': 'healthy',
        'message': 'Hardware Monitor funcionando correctamente',
        'timestamp': time.time()
    })

@main_bp.route('/api/mission-status')
@jwt_required()
@handle_exceptions
def api_mission_status():
    """Endpoint de estado de misión militar con health checks avanzados"""
    try:
        from datetime import datetime
        import time
        
        # Tiempo de misión (desde el inicio del servidor)
        mission_start = getattr(current_app, 'mission_start_time', time.time())
        if not hasattr(current_app, 'mission_start_time'):
            setattr(current_app, 'mission_start_time', mission_start)
        
        mission_elapsed = time.time() - mission_start
        
        # Health checks del sistema
        health_checks = {}
        
        # CPU Check
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            health_checks['cpu'] = {
                'status': 'OPERATIONAL' if cpu_percent < 90 else 'DEGRADED',
                'value': round(cpu_percent, 1),
                'threshold': 90
            }
        except Exception as e:
            health_checks['cpu'] = {
                'status': 'OFFLINE',
                'error': str(e),
                'value': -1
            }
        
        # Memory Check
        try:
            memory = psutil.virtual_memory()
            health_checks['memory'] = {
                'status': 'OPERATIONAL' if memory.percent < 90 else 'DEGRADED',
                'value': round(memory.percent, 1),
                'threshold': 90
            }
        except Exception as e:
            health_checks['memory'] = {
                'status': 'OFFLINE',
                'error': str(e),
                'value': -1
            }
        
        # Disk Check
        try:
            disk_data = get_disk_usage()
            disk_percent = disk_data.get('usage', -1)
            health_checks['disk'] = {
                'status': 'OPERATIONAL' if disk_percent >= 0 and disk_percent < 90 else 'DEGRADED',
                'value': disk_percent,
                'threshold': 90
            }
        except Exception as e:
            health_checks['disk'] = {
                'status': 'OFFLINE',
                'error': str(e),
                'value': -1
            }
        
        # Network Check
        try:
            net_io = psutil.net_io_counters()
            health_checks['network'] = {
                'status': 'OPERATIONAL',
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
        except Exception as e:
            health_checks['network'] = {
                'status': 'OFFLINE',
                'error': str(e)
            }
        
        # Determinar estado general de la misión
        operational_count = sum(1 for check in health_checks.values() if check['status'] == 'OPERATIONAL')
        degraded_count = sum(1 for check in health_checks.values() if check['status'] == 'DEGRADED')
        offline_count = sum(1 for check in health_checks.values() if check['status'] == 'OFFLINE')
        
        if offline_count > 0:
            mission_status = 'OFFLINE'
        elif degraded_count > 0:
            mission_status = 'DEGRADED'
        else:
            mission_status = 'OPERATIONAL'
        
        # Formatear tiempo de misión
        hours = int(mission_elapsed // 3600)
        minutes = int((mission_elapsed % 3600) // 60)
        seconds = int(mission_elapsed % 60)
        mission_time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        mission_data = {
            'mission_status': mission_status,
            'mission_time': mission_time_formatted,
            'mission_elapsed_seconds': int(mission_elapsed),
            'mission_start': datetime.fromtimestamp(mission_start).isoformat(),
            'current_time': datetime.now().isoformat(),
            'request_id': getattr(g, 'request_id', 'unknown'),
            'health_checks': health_checks,
            'summary': {
                'operational': operational_count,
                'degraded': degraded_count,
                'offline': offline_count,
                'total': len(health_checks)
            },
            'alert_level': 'DEFCON-5' if mission_status == 'OPERATIONAL' else 'DEFCON-3' if mission_status == 'DEGRADED' else 'DEFCON-1'
        }
        
        return jsonify(mission_data)
    except Exception as e:
        return jsonify({
            'mission_status': 'OFFLINE',
            'error': str(e),
            'request_id': getattr(g, 'request_id', 'unknown'),
            'alert_level': 'DEFCON-1'
        }), 500

@main_bp.route('/api/mission-logs')
@jwt_required()
@handle_exceptions
def api_mission_logs():
    """Endpoint para obtener logs de misión militar"""
    try:
        from datetime import datetime
        
        # Simular logs de misión (en producción, esto vendría de una base de datos o archivo)
        mission_logs = getattr(current_app, 'mission_logs', [])
        
        # Agregar log de la consulta actual
        current_log = {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': f'MISSION LOGS REQUESTED - Request ID: {getattr(g, "request_id", "unknown")}',
            'request_id': getattr(g, 'request_id', 'unknown')
        }
        
        if not hasattr(current_app, 'mission_logs'):
            setattr(current_app, 'mission_logs', [])
        
        mission_logs = getattr(current_app, 'mission_logs', [])
        mission_logs.append(current_log)
        setattr(current_app, 'mission_logs', mission_logs)
        
        # Mantener solo los últimos 100 logs
        if len(mission_logs) > 100:
            mission_logs = mission_logs[-100:]
            setattr(current_app, 'mission_logs', mission_logs)
        
        return jsonify({
            'logs': mission_logs,
            'total_logs': len(mission_logs),
            'request_id': getattr(g, 'request_id', 'unknown'),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'logs': [],
            'request_id': getattr(g, 'request_id', 'unknown')
        }), 500

@main_bp.route('/api/mission-logs/add', methods=['POST'])
@jwt_required()
@handle_exceptions
def api_add_mission_log():
    """Endpoint para agregar logs de misión militar"""
    try:
        from datetime import datetime
        
        data = request.get_json()
        log_level = data.get('level', 'INFO')
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Crear log de misión
        mission_log = {
            'timestamp': datetime.now().isoformat(),
            'level': log_level.upper(),
            'message': message,
            'request_id': getattr(g, 'request_id', 'unknown')
        }
        
        if not hasattr(current_app, 'mission_logs'):
            setattr(current_app, 'mission_logs', [])
        
        mission_logs = getattr(current_app, 'mission_logs', [])
        mission_logs.append(mission_log)
        setattr(current_app, 'mission_logs', mission_logs)
        
        # Mantener solo los últimos 100 logs
        if len(mission_logs) > 100:
            mission_logs = mission_logs[-100:]
            setattr(current_app, 'mission_logs', mission_logs)
        
        # Log también en el sistema de logging de Python
        if log_level.upper() == 'ERROR':
            logging.error(f"MISSION LOG: {message}")
        elif log_level.upper() == 'WARNING':
            logging.warning(f"MISSION LOG: {message}")
        else:
            logging.info(f"MISSION LOG: {message}")
        
        return jsonify({
            'success': True,
            'log_added': mission_log,
            'total_logs': len(mission_logs),
            'request_id': getattr(g, 'request_id', 'unknown')
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'request_id': getattr(g, 'request_id', 'unknown')
        }), 500

# Endpoints individuales para lazy loading
@main_bp.route('/api/cpu')
@jwt_required()
@handle_exceptions
def api_cpu():
    """Endpoint específico para datos de CPU"""
    cpu_data = sanitize_output(get_cpu_usage())
    return jsonify({
        'cpu': cpu_data,
        'request_id': getattr(g, 'request_id', 'unknown'),
        'success': True
    })

@main_bp.route('/api/ram')
@jwt_required()
@handle_exceptions
def api_ram():
    """Endpoint específico para datos de RAM"""
    ram_data = sanitize_output(get_ram_usage())
    return jsonify({
        'ram': ram_data,
        'request_id': getattr(g, 'request_id', 'unknown'),
        'success': True
    })

@main_bp.route('/api/disk')
@jwt_required()
@handle_exceptions
def api_disk():
    """Endpoint específico para datos de disco"""
    disk_data = sanitize_output(get_disk_usage())
    return jsonify({
        'disk': disk_data,
        'request_id': getattr(g, 'request_id', 'unknown'),
        'success': True
    })

@main_bp.route('/api/network')
@jwt_required()
@handle_exceptions
def api_network():
    """Endpoint específico para datos de red"""
    network_data = sanitize_output(get_network_stats())
    return jsonify({
        'network': network_data,
        'request_id': getattr(g, 'request_id', 'unknown'),
        'success': True
    }) 