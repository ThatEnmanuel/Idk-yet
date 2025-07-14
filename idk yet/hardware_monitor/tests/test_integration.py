"""
Tests de integración para Hardware Monitor
"""

import pytest
import json
import time
from flask import Flask
from app import create_app
from app.utils import get_cpu_usage, get_ram_usage, get_disk_usage, get_network_stats, sanitize_output

@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Headers de autenticación para tests"""
    # Primero obtener token
    return {'Content-Type': 'application/json'}

def get_auth_token(client):
    """Obtener token de autenticación"""
    response = client.post('/api/login', 
                          json={'username': 'admin', 'password': 'admin'},
                          headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    data = json.loads(response.data)
    return data['access_token']

def test_index_page(client):
    """Test de la página principal"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hardware Monitor' in response.data

def test_login_success(client):
    """Test de login exitoso"""
    response = client.post('/api/login', 
                          json={'username': 'admin', 'password': 'admin'},
                          headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert data['success'] == True

def test_login_failure(client):
    """Test de login fallido"""
    response = client.post('/api/login', 
                          json={'username': 'admin', 'password': 'wrong'},
                          headers={'Content-Type': 'application/json'})
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['success'] == False

def test_api_stats_with_auth(client):
    """Test de endpoint /api/stats con autenticación"""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    
    response = client.get('/api/stats', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verificar estructura de respuesta
    assert 'cpu' in data
    assert 'ram' in data
    assert 'disk' in data
    assert 'network' in data
    assert 'request_id' in data
    assert 'response_time_ms' in data
    assert data['success'] == True

def test_api_stats_without_auth(client):
    """Test de endpoint /api/stats sin autenticación"""
    response = client.get('/api/stats')
    assert response.status_code == 401

def test_api_health_with_auth(client):
    """Test de endpoint /api/health con autenticación"""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    
    response = client.get('/api/health', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verificar estructura de health check
    assert 'status' in data
    assert 'timestamp' in data
    assert 'request_id' in data
    assert 'system' in data
    assert 'application' in data
    assert 'network' in data
    assert 'checks' in data

def test_api_health_basic_auth(client):
    """Test de endpoint /api/health/basic con autenticación HTTP Basic"""
    from base64 import b64encode
    
    credentials = b64encode(b'admin:admin').decode('utf-8')
    headers = {'Authorization': f'Basic {credentials}'}
    
    response = client.get('/api/health/basic', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_individual_endpoints(client):
    """Test de endpoints individuales para lazy loading"""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test CPU endpoint
    response = client.get('/api/cpu', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cpu' in data
    assert 'request_id' in data
    
    # Test RAM endpoint
    response = client.get('/api/ram', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'ram' in data
    assert 'request_id' in data
    
    # Test Disk endpoint
    response = client.get('/api/disk', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'disk' in data
    assert 'request_id' in data
    
    # Test Network endpoint
    response = client.get('/api/network', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'network' in data
    assert 'request_id' in data

def test_rate_limiting(client):
    """Test de rate limiting"""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    
    # Hacer múltiples requests rápidos
    for i in range(15):  # Más del límite por segundo
        response = client.get('/api/stats', headers=headers)
        if response.status_code == 429:  # Too Many Requests
            break
    
    # Al menos uno debería ser bloqueado
    assert any(response.status_code == 429 for response in [client.get('/api/stats', headers=headers) for _ in range(5)])

def test_sanitization():
    """Test de sanitización de outputs"""
    # Test con datos que contienen rutas sensibles
    test_data = {
        'mountpoint': 'C:\\Users\\admin\\Documents\\sensitive\\file.txt',
        'error': 'Error accessing C:\\Users\\admin\\Documents\\sensitive\\file.txt',
        'normal_field': 'normal_value'
    }
    
    sanitized = sanitize_output(test_data)
    
    # Verificar que las rutas fueron sanitizadas
    assert sanitized['mountpoint'] == 'C:\\'
    assert '***' in sanitized['error']
    assert sanitized['normal_field'] == 'normal_value'

def test_utils_functions():
    """Test de funciones de utilidad"""
    # Test CPU
    cpu_data = get_cpu_usage()
    assert 'usage' in cpu_data
    assert 'cores' in cpu_data
    assert 'timestamp' in cpu_data
    assert 0 <= cpu_data['usage'] <= 100 or cpu_data['usage'] == -1
    
    # Test RAM
    ram_data = get_ram_usage()
    assert 'usage' in ram_data
    assert 'total' in ram_data
    assert 'used' in ram_data
    assert 'free' in ram_data
    assert 'timestamp' in ram_data
    assert 0 <= ram_data['usage'] <= 100 or ram_data['usage'] == -1
    
    # Test Disk
    disk_data = get_disk_usage()
    assert 'usage' in disk_data
    assert 'total' in disk_data
    assert 'used' in disk_data
    assert 'free' in disk_data
    assert 'mountpoint' in disk_data
    assert 'timestamp' in disk_data
    assert 0 <= disk_data['usage'] <= 100 or disk_data['usage'] == -1
    
    # Test Network
    network_data = get_network_stats()
    assert 'sent_mb' in network_data
    assert 'received_mb' in network_data
    assert 'packets_sent' in network_data
    assert 'packets_recv' in network_data
    assert 'timestamp' in network_data

def test_metrics_endpoint(client):
    """Test del endpoint de métricas Prometheus"""
    response = client.get('/metrics')
    assert response.status_code == 200
    # Verificar que contiene métricas básicas
    assert b'flask_http_requests_total' in response.data

def test_request_tracing(client):
    """Test de trazabilidad de requests"""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    
    response = client.get('/api/stats', headers=headers)
    assert response.status_code == 200
    
    # Verificar que se incluye el header X-Request-ID
    assert 'X-Request-ID' in response.headers
    request_id = response.headers['X-Request-ID']
    assert len(request_id) > 0
    
    # Verificar que el request_id está en la respuesta JSON
    data = json.loads(response.data)
    assert data['request_id'] == request_id 