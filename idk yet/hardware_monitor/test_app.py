#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de Hardware Monitor
"""

import requests
import json
import time
import sys
from urllib.parse import urljoin

def test_endpoint(base_url, endpoint, description):
    """Probar un endpoint específico"""
    url = urljoin(base_url, endpoint)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {description}: OK")
            return True
        else:
            print(f"❌ {description}: Error {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False

def test_api_data(base_url, endpoint, description):
    """Probar endpoint y verificar datos JSON"""
    url = urljoin(base_url, endpoint)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and not data.get('error'):
                print(f"✅ {description}: OK (datos válidos)")
                return True
            else:
                print(f"⚠️ {description}: Datos con error - {data.get('error', 'Error desconocido')}")
                return False
        else:
            print(f"❌ {description}: Error {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Hardware Monitor - Pruebas de Funcionalidad")
    print("=" * 50)
    
    # Configuración
    base_url = "http://localhost:5000"
    
    # Lista de pruebas
    tests = [
        ("/", "Página principal"),
        ("/api/health", "Health check"),
        ("/api/stats", "Estadísticas de hardware"),
    ]
    
    # Ejecutar pruebas
    passed = 0
    total = len(tests)
    
    for endpoint, description in tests:
        if endpoint == "/":
            success = test_endpoint(base_url, endpoint, description)
        else:
            success = test_api_data(base_url, endpoint, description)
        
        if success:
            passed += 1
        
        time.sleep(0.5)  # Pausa entre pruebas
    
    # Resultados
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron!")
        print("✅ Hardware Monitor está funcionando correctamente")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron")
        print("🔧 Revisa que la aplicación esté ejecutándose en http://localhost:5000")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 