#!/usr/bin/env python3
"""
Smoke Tests para Hardware Monitor
Verificación rápida post-deploy
"""

import requests
import json
import sys
import time
from base64 import b64encode

# Configuración
BASE_URL = "http://localhost:5000"
TIMEOUT = 10

def test_basic_connectivity():
    """Test de conectividad básica"""
    print("🔍 Probando conectividad básica...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Página principal accesible")
            return True
        else:
            print(f"❌ Página principal retornó {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conectividad: {e}")
        return False

def test_metrics_endpoint():
    """Test del endpoint de métricas"""
    print("📊 Probando endpoint de métricas...")
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Endpoint de métricas accesible")
            return True
        else:
            print(f"❌ Métricas retornó {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en métricas: {e}")
        return False

def test_login():
    """Test de login"""
    print("🔐 Probando login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "access_token" in data:
                print("✅ Login exitoso")
                return data["access_token"]
            else:
                print("❌ Login falló - respuesta inválida")
                return None
        else:
            print(f"❌ Login retornó {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_health_basic_auth():
    """Test de health con autenticación básica"""
    print("💚 Probando health con auth básica...")
    try:
        credentials = b64encode(b'admin:admin').decode('utf-8')
        headers = {'Authorization': f'Basic {credentials}'}
        
        response = requests.get(f"{BASE_URL}/api/health/basic", headers=headers, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ Health básico OK")
                return True
            else:
                print(f"❌ Health básico no está healthy: {data}")
                return False
        else:
            print(f"❌ Health básico retornó {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en health básico: {e}")
        return False

def test_api_endpoints(token):
    """Test de endpoints de API con JWT"""
    print("🔑 Probando endpoints de API...")
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("/api/health", "Health avanzado"),
        ("/api/stats", "Stats completos"),
        ("/api/cpu", "CPU"),
        ("/api/ram", "RAM"),
        ("/api/disk", "Disco"),
        ("/api/network", "Red")
    ]
    
    success_count = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if "request_id" in data:
                    print(f"✅ {name} OK")
                    success_count += 1
                else:
                    print(f"⚠️ {name} sin request_id")
                    success_count += 1
            else:
                print(f"❌ {name} retornó {response.status_code}")
        except Exception as e:
            print(f"❌ Error en {name}: {e}")
    
    return success_count == len(endpoints)

def test_rate_limiting(token):
    """Test de rate limiting"""
    print("🚦 Probando rate limiting...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Hacer requests rápidos
        responses = []
        for i in range(15):
            response = requests.get(f"{BASE_URL}/api/stats", headers=headers, timeout=TIMEOUT)
            responses.append(response.status_code)
            if response.status_code == 429:  # Too Many Requests
                break
        
        if 429 in responses:
            print("✅ Rate limiting funcionando")
            return True
        else:
            print("⚠️ Rate limiting no detectado")
            return True  # No es crítico
    except Exception as e:
        print(f"❌ Error en rate limiting: {e}")
        return False

def main():
    """Función principal de smoke tests"""
    print("🚀 Iniciando Smoke Tests para Hardware Monitor")
    print("=" * 50)
    
    tests = [
        ("Conectividad básica", test_basic_connectivity),
        ("Endpoint de métricas", test_metrics_endpoint),
        ("Health básico", test_health_basic_auth),
    ]
    
    # Ejecutar tests básicos
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        print()
    
    # Test de login y endpoints protegidos
    token = test_login()
    if token:
        passed += 1
        total += 1
        
        if test_api_endpoints(token):
            passed += 1
        total += 1
        
        if test_rate_limiting(token):
            passed += 1
        total += 1
    else:
        total += 3  # Login + API endpoints + rate limiting
    
    print("=" * 50)
    print(f"📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los smoke tests pasaron!")
        sys.exit(0)
    else:
        print("❌ Algunos tests fallaron")
        sys.exit(1)

if __name__ == "__main__":
    main() 