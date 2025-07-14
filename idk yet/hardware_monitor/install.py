#!/usr/bin/env python3
"""
Script de instalación automática para Hardware Monitor
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Salida de error: {e.stderr}")
        return False

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def create_virtual_environment():
    """Crear entorno virtual"""
    if os.path.exists("venv"):
        print("✅ Entorno virtual ya existe")
        return True
    
    return run_command("python -m venv venv", "Creando entorno virtual")

def activate_virtual_environment():
    """Activar entorno virtual"""
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_script = "venv/bin/activate"
    
    if os.path.exists(activate_script):
        print("✅ Entorno virtual listo para activar")
        return True
    else:
        print("❌ No se pudo encontrar el script de activación")
        return False

def install_dependencies():
    """Instalar dependencias"""
    pip_cmd = "venv\\Scripts\\pip" if os.name == 'nt' else "venv/bin/pip"
    return run_command(f"{pip_cmd} install -r requirements.txt", "Instalando dependencias")

def create_env_file():
    """Crear archivo .env si no existe"""
    if os.path.exists(".env"):
        print("✅ Archivo .env ya existe")
        return True
    
    if os.path.exists("env.example"):
        shutil.copy("env.example", ".env")
        print("✅ Archivo .env creado desde env.example")
        return True
    else:
        print("❌ No se encontró env.example")
        return False

def test_installation():
    """Probar la instalación"""
    print("🧪 Probando instalación...")
    
    # Verificar que psutil funciona
    try:
        import psutil
        print("✅ psutil importado correctamente")
    except ImportError:
        print("❌ Error importando psutil")
        return False
    
    # Verificar que Flask funciona
    try:
        import flask
        print("✅ Flask importado correctamente")
    except ImportError:
        print("❌ Error importando Flask")
        return False
    
    return True

def main():
    """Función principal de instalación"""
    print("🚀 Instalador de Hardware Monitor")
    print("=" * 40)
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Crear entorno virtual
    if not create_virtual_environment():
        print("❌ No se pudo crear el entorno virtual")
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies():
        print("❌ No se pudieron instalar las dependencias")
        sys.exit(1)
    
    # Crear archivo .env
    if not create_env_file():
        print("❌ No se pudo crear el archivo .env")
        sys.exit(1)
    
    # Probar instalación
    if not test_installation():
        print("❌ La instalación no se completó correctamente")
        sys.exit(1)
    
    print("\n🎉 ¡Instalación completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Activar el entorno virtual:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("2. Ejecutar la aplicación:")
    print("   python run.py")
    print("   o")
    print("   python run.py --debug")
    
    print("3. Abrir en el navegador:")
    print("   http://localhost:5000")
    
    print("\n📚 Para más información, consulta el README.md")

if __name__ == "__main__":
    main() 