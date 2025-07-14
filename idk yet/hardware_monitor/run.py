#!/usr/bin/env python3
"""
Script de ejecución para Hardware Monitor
Permite ejecutar la aplicación con diferentes configuraciones
"""

import os
import sys
import signal
import argparse
import threading
import time
from app import create_app

# Variable global para controlar el shutdown
shutdown_event = threading.Event()

def signal_handler(signum, frame):
    """Manejador de señales para graceful shutdown"""
    print(f"\n🛑 Recibida señal {signum}. Iniciando graceful shutdown...")
    shutdown_event.set()

def graceful_shutdown(app):
    """Función para shutdown graceful"""
    print("⏳ Esperando que los requests activos terminen...")
    
    # Dar tiempo para que los requests activos terminen
    time.sleep(2)
    
    print("✅ Shutdown completado")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='Hardware Monitor - Monitoreo de Sistema')
    parser.add_argument('--host', default='0.0.0.0', help='Host para ejecutar el servidor')
    parser.add_argument('--port', type=int, default=5000, help='Puerto para ejecutar el servidor')
    parser.add_argument('--debug', action='store_true', help='Ejecutar en modo debug')
    parser.add_argument('--reload', action='store_true', help='Recargar automáticamente en cambios')
    parser.add_argument('--config', choices=['development', 'production', 'testing'], 
                       default='development', help='Configuración a usar')
    
    args = parser.parse_args()
    
    # Configurar variables de entorno desde argumentos
    if args.debug:
        os.environ['DEBUG'] = 'True'
    if args.reload:
        os.environ['FLASK_ENV'] = 'development'
    
    # Configurar manejo de señales para graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Crear la aplicación Flask
    app = create_app()
    
    print("🚀 Iniciando Hardware Monitor...")
    print(f"📊 Dashboard: http://{args.host}:{args.port}")
    print(f"🔧 API: http://{args.host}:{args.port}/api/stats")
    print(f"💚 Health Check: http://{args.host}:{args.port}/api/health")
    print(f"📈 Métricas: http://{args.host}:{args.port}/metrics")
    print(f"🔐 Health Básico: http://{args.host}:{args.port}/api/health/basic")
    print("=" * 50)
    
    try:
        # Ejecutar en un thread separado para permitir graceful shutdown
        def run_server():
            app.run(
                host=args.host,
                port=args.port,
                debug=args.debug or os.getenv('DEBUG', 'False').lower() == 'true',
                use_reloader=False  # Deshabilitar reloader para graceful shutdown
            )
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Esperar hasta que se solicite shutdown
        while not shutdown_event.is_set():
            time.sleep(1)
        
        # Iniciar graceful shutdown
        graceful_shutdown(app)
        
    except KeyboardInterrupt:
        print("\n👋 Hardware Monitor detenido por el usuario")
        graceful_shutdown(app)
    except Exception as e:
        print(f"❌ Error al iniciar Hardware Monitor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 