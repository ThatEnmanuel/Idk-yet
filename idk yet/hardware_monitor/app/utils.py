"""
Utilidades para obtener información del hardware
"""

import psutil
import time
import logging
import os
import re
from functools import wraps
from datetime import datetime
from flask import g

def sanitize_output(data):
    """Sanitizar outputs para evitar exponer información sensible"""
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if key == 'mountpoint' and isinstance(value, str):
                # Ocultar rutas completas, mostrar solo el nombre del drive
                if ':' in value:  # Windows drive
                    sanitized[key] = value.split(':')[0] + ':\\'
                else:  # Unix path
                    sanitized[key] = '/'
            elif key == 'error' and isinstance(value, str):
                # Sanitizar mensajes de error de forma simple
                sanitized[key] = value.replace('\\', '/').replace('C:/', '***/')
            else:
                sanitized[key] = value
        return sanitized
    return data

def sanitize_log_message(message):
    """Sanitizar mensajes de log para evitar exposición de datos sensibles"""
    import re
    sensitive_patterns = [
        r'password["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'secret["\']?\s*[:=]\s*["\']?[^"\']+["\']?'
    ]
    
    for pattern in sensitive_patterns:
        message = re.sub(pattern, '***REDACTED***', message, flags=re.IGNORECASE)
    
    return message

def retry_on_failure(max_retries=3, delay=1, exponential_backoff=True):
    """Decorador para reintentos automáticos con delay configurable"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    current_delay = delay * (2 ** attempt) if exponential_backoff else delay
                    logging.warning(f"Intento {attempt + 1}/{max_retries} falló en {func.__name__}: {e}")
                    
                    if attempt == max_retries - 1:
                        logging.error(f"Todos los intentos fallaron en {func.__name__}")
                        raise
                    
                    time.sleep(current_delay)
            return None
        return wrapper
    return decorator

# Configuración desde variables de entorno
MAX_RETRIES_CRITICAL = int(os.getenv('MAX_RETRIES_CRITICAL', '3'))
MAX_RETRIES_NORMAL = int(os.getenv('MAX_RETRIES_NORMAL', '2'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '1'))
USE_EXPONENTIAL_BACKOFF = os.getenv('USE_EXPONENTIAL_BACKOFF', 'true').lower() == 'true'

@retry_on_failure(max_retries=MAX_RETRIES_CRITICAL, delay=RETRY_DELAY, exponential_backoff=USE_EXPONENTIAL_BACKOFF)
def get_cpu_usage():
    """Obtener uso de CPU en porcentaje"""
    try:
        # Obtener uso de CPU con intervalo de 1 segundo para mayor precisión
        cpu_percent = psutil.cpu_percent(interval=1)
        # Validar rango
        cpu_percent = max(0.0, min(100.0, cpu_percent))
        return {
            'usage': round(cpu_percent, 1),
            'cores': psutil.cpu_count(),
            'timestamp': time.time()
        }
    except Exception as e:
        error_msg = sanitize_log_message(str(e))
        logging.error(f"Error obteniendo CPU usage: {error_msg}")
        return {
            'usage': -1,
            'cores': 0,
            'error': 'Error interno del sistema',
            'timestamp': time.time()
        }

@retry_on_failure(max_retries=MAX_RETRIES_CRITICAL, delay=RETRY_DELAY, exponential_backoff=USE_EXPONENTIAL_BACKOFF)
def get_ram_usage():
    """Obtener uso de RAM en porcentaje"""
    try:
        memory = psutil.virtual_memory()
        # Validar rango
        usage_percent = max(0.0, min(100.0, memory.percent))
        return {
            'usage': round(usage_percent, 1),
            'total': max(0, memory.total),
            'used': max(0, memory.used),
            'free': max(0, memory.free),
            'timestamp': time.time()
        }
    except Exception as e:
        logging.error(f"Error obteniendo RAM usage: {str(e)}")
        return {
            'usage': -1,
            'total': 0,
            'used': 0,
            'free': 0,
            'error': str(e),
            'timestamp': time.time()
        }

@retry_on_failure(max_retries=MAX_RETRIES_CRITICAL, delay=RETRY_DELAY, exponential_backoff=USE_EXPONENTIAL_BACKOFF)
def get_disk_usage():
    """Obtener uso de disco en porcentaje"""
    try:
        # Obtener la partición principal (generalmente C: en Windows o / en Linux)
        disk_partitions = psutil.disk_partitions()
        
        # Buscar la partición principal
        main_partition = None
        for partition in disk_partitions:
            # En Windows, buscar C: o la primera unidad disponible
            if os.name == 'nt':  # Windows
                if partition.mountpoint == 'C:\\':
                    main_partition = partition
                    break
                elif not main_partition and ':' in partition.mountpoint:
                    main_partition = partition
            else:  # Unix/Linux
                if partition.mountpoint == '/':
                    main_partition = partition
                    break
                elif not main_partition:
                    main_partition = partition
        
        # Si no se encuentra la partición principal, usar la primera disponible
        if not main_partition and disk_partitions:
            main_partition = disk_partitions[0]
        
        if main_partition:
            try:
                usage = psutil.disk_usage(main_partition.mountpoint)
                # Validar rango
                usage_percent = max(0.0, min(100.0, usage.percent))
                return {
                    'usage': round(usage_percent, 1),
                    'total': max(0, usage.total),
                    'used': max(0, usage.used),
                    'free': max(0, usage.free),
                    'mountpoint': main_partition.mountpoint,
                    'timestamp': time.time()
                }
            except (OSError, PermissionError) as e:
                logging.warning(f"No se pudo acceder a {main_partition.mountpoint}: {e}")
                # Intentar con una ruta alternativa
                if os.name == 'nt':
                    try:
                        usage = psutil.disk_usage('C:\\')
                        usage_percent = max(0.0, min(100.0, usage.percent))
                        return {
                            'usage': round(usage_percent, 1),
                            'total': max(0, usage.total),
                            'used': max(0, usage.used),
                            'free': max(0, usage.free),
                            'mountpoint': 'C:\\',
                            'timestamp': time.time()
                        }
                    except Exception:
                        pass
                raise e
        else:
            logging.error("No se encontró ninguna partición de disco")
            return {
                'usage': -1,
                'total': 0,
                'used': 0,
                'free': 0,
                'error': 'No se encontró ninguna partición de disco',
                'timestamp': time.time()
            }
    except Exception as e:
        logging.error(f"Error obteniendo disk usage: {str(e)}")
        return {
            'usage': -1,
            'total': 0,
            'used': 0,
            'free': 0,
            'error': str(e),
            'timestamp': time.time()
        }

@retry_on_failure(max_retries=MAX_RETRIES_NORMAL, delay=RETRY_DELAY, exponential_backoff=False)
def get_network_stats():
    """Obtener estadísticas de red (MB enviados y recibidos)"""
    try:
        # Obtener contadores de red
        net_io = psutil.net_io_counters()
        
        # Convertir bytes a MB y validar
        bytes_sent_mb = max(0, round(net_io.bytes_sent / (1024 * 1024), 2))
        bytes_recv_mb = max(0, round(net_io.bytes_recv / (1024 * 1024), 2))
        
        return {
            'sent_mb': bytes_sent_mb,
            'received_mb': bytes_recv_mb,
            'packets_sent': max(0, net_io.packets_sent),
            'packets_recv': max(0, net_io.packets_recv),
            'timestamp': time.time()
        }
    except Exception as e:
        logging.error(f"Error obteniendo network stats: {str(e)}")
        return {
            'sent_mb': -1,
            'received_mb': -1,
            'packets_sent': 0,
            'packets_recv': 0,
            'error': str(e),
            'timestamp': time.time()
        }

def format_bytes(bytes_value):
    """Formatear bytes en unidades legibles (KB, MB, GB, etc.)"""
    if bytes_value == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while bytes_value >= 1024 and i < len(size_names) - 1:
        bytes_value /= 1024.0
        i += 1
    
    return f"{bytes_value:.2f} {size_names[i]}" 

# Clase wrapper adicional para mayor robustez
class SafeHardwareMonitor:
    """Clase wrapper para monitoreo seguro de hardware con fallback y reintentos"""
    
    def __init__(self):
        self.last_good_data = {}
        self.error_count = 0
        
    def safe_call(self, func_name: str, *args, **kwargs):
        """Llamada segura a funciones de psutil con fallback"""
        try:
            func = getattr(psutil, func_name)
            result = func(*args, **kwargs)
            self.error_count = 0  # Resetear contador en éxito
            self.last_good_data[func_name] = result
            return result
        except Exception as e:
            self.error_count += 1
            logging.error(f"Error en {func_name}: {str(e)}")
            # Usar datos previos si están disponibles
            if func_name in self.last_good_data:
                logging.warning(f"Usando datos cached para {func_name}")
                return self.last_good_data[func_name]
            return None
    
    def get_cpu_usage_safe(self):
        """Versión más segura de get_cpu_usage con reintentos"""
        return get_cpu_usage()  # Usar la función mejorada
    
    def get_ram_usage_safe(self):
        """Versión más segura de get_ram_usage con reintentos"""
        return get_ram_usage()  # Usar la función mejorada
    
    def get_disk_usage_safe(self):
        """Versión más segura de get_disk_usage con reintentos"""
        return get_disk_usage()  # Usar la función mejorada
    
    def get_network_stats_safe(self):
        """Versión más segura de get_network_stats con reintentos"""
        return get_network_stats()  # Usar la función mejorada

# Instancia global para uso en la aplicación
hardware_monitor = SafeHardwareMonitor() 

class MilitaryErrorHandler:
    """Manejador de errores con estética militar y códigos DEFCON"""
    
    def __init__(self):
        self.defcon_levels = {
            'DEFCON-5': 'Normal readiness',
            'DEFCON-4': 'Above normal readiness',
            'DEFCON-3': 'Air Force ready to mobilize in 15 minutes',
            'DEFCON-2': 'Armed Forces ready to deploy and engage in less than 6 hours',
            'DEFCON-1': 'Maximum readiness - Nuclear war is imminent'
        }
    
    def handle_error(self, error, context=None):
        """Maneja errores con formato militar"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'defcon_level': self._determine_defcon_level(error),
            'context': context or {},
            'request_id': getattr(g, 'request_id', 'unknown'),
            'military_code': self._generate_military_code(error)
        }
        
        # Log militar estructurado
        self._log_military_error(error_info)
        
        return error_info
    
    def _determine_defcon_level(self, error):
        """Determina el nivel DEFCON basado en el tipo de error"""
        if isinstance(error, (SystemError, OSError, IOError)):
            return 'DEFCON-1'  # Error crítico del sistema
        elif isinstance(error, (ValueError, TypeError, AttributeError)):
            return 'DEFCON-3'  # Error de datos/programación
        elif isinstance(error, (ConnectionError, TimeoutError)):
            return 'DEFCON-2'  # Error de conectividad
        elif isinstance(error, (PermissionError, FileNotFoundError)):
            return 'DEFCON-4'  # Error de permisos/archivos
        else:
            return 'DEFCON-5'  # Error menor
    
    def _generate_military_code(self, error):
        """Genera código militar para el error"""
        import hashlib
        error_hash = hashlib.md5(str(error).encode()).hexdigest()[:8].upper()
        return f"ERR-{error_hash}"
    
    def _log_military_error(self, error_info):
        """Log del error en formato militar"""
        defcon_desc = self.defcon_levels.get(error_info['defcon_level'], 'Unknown')
        
        log_message = f"""
🪖 MILITARY ERROR REPORT 🪖
DEFCON LEVEL: {error_info['defcon_level']} - {defcon_desc}
MILITARY CODE: {error_info['military_code']}
ERROR TYPE: {error_info['error_type']}
MESSAGE: {error_info['error_message']}
TIMESTAMP: {error_info['timestamp']}
REQUEST ID: {error_info['request_id']}
CONTEXT: {error_info['context']}
        """.strip()
        
        if error_info['defcon_level'] in ['DEFCON-1', 'DEFCON-2']:
            logging.critical(log_message)
        elif error_info['defcon_level'] == 'DEFCON-3':
            logging.error(log_message)
        else:
            logging.warning(log_message)
    
    def create_military_response(self, error_info, status_code=500):
        """Crea respuesta de error con formato militar"""
        response_data = {
            'status': 'MISSION_FAILED',
            'defcon_level': error_info['defcon_level'],
            'military_code': error_info['military_code'],
            'error': {
                'type': error_info['error_type'],
                'message': error_info['error_message'],
                'context': error_info['context']
            },
            'timestamp': error_info['timestamp'],
            'request_id': error_info['request_id'],
            'alert': self._get_defcon_alert(error_info['defcon_level'])
        }
        
        return response_data, status_code
    
    def _get_defcon_alert(self, defcon_level):
        """Obtiene mensaje de alerta basado en nivel DEFCON"""
        alerts = {
            'DEFCON-1': '🚨 CRITICAL SYSTEM FAILURE - IMMEDIATE ACTION REQUIRED',
            'DEFCON-2': '⚠️ SYSTEM DEGRADED - HIGH PRIORITY ATTENTION NEEDED',
            'DEFCON-3': '🔶 SYSTEM WARNING - MONITORING REQUIRED',
            'DEFCON-4': '🔸 MINOR ISSUE DETECTED - STANDARD MONITORING',
            'DEFCON-5': '✅ NORMAL OPERATION - NO ACTION REQUIRED'
        }
        return alerts.get(defcon_level, 'UNKNOWN ALERT LEVEL')

# Instancia global del manejador de errores militar
military_error_handler = MilitaryErrorHandler() 