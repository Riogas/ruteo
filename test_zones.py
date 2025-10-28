"""
Test del endpoint de detección de zonas.
Prueba tanto con direcciones como con coordenadas directas.
"""

import requests
import json

BASE_URL = "http://localhost:8080/api/v1"


def print_separator(title: str = ""):
    """Imprime un separador visual"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)
    print()


def test_zone_with_address(address: str):
    """Prueba detección de zona con dirección"""
    print(f"🔍 Probando dirección: {address}")
    
    payload = {"address": address}
    
    try:
        response = requests.post(
            f"{BASE_URL}/zone",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Geocodificación exitosa")
            print(f"   📍 Coordenadas: ({data['coordinates']['lat']:.6f}, {data['coordinates']['lon']:.6f})")
            print(f"   🗺️  UTM: ({data['coordinates']['utm_x']:.2f}, {data['coordinates']['utm_y']:.2f}) Zona {data['coordinates']['utm_zone']}")
            
            if data['zone_found']:
                print(f"   🎯 ZONA ENCONTRADA:")
                print(f"      - Nombre: {data['zone_name']}")
                print(f"      - ID: {data['zone_id']}")
            else:
                print(f"   ℹ️  No está en ninguna zona registrada")
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Exception: {e}")


def test_zone_with_coordinates(lat: float, lon: float, description: str = ""):
    """Prueba detección de zona con coordenadas"""
    if description:
        print(f"🔍 Probando: {description}")
    print(f"📍 Coordenadas: ({lat}, {lon})")
    
    payload = {"lat": lat, "lon": lon}
    
    try:
        response = requests.post(
            f"{BASE_URL}/zone",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Consulta exitosa")
            print(f"   🗺️  UTM: ({data['coordinates']['utm_x']:.2f}, {data['coordinates']['utm_y']:.2f}) Zona {data['coordinates']['utm_zone']}")
            
            if data['zone_found']:
                print(f"   🎯 ZONA ENCONTRADA:")
                print(f"      - Nombre: {data['zone_name']}")
                print(f"      - ID: {data['zone_id']}")
            else:
                print(f"   ℹ️  No está en ninguna zona registrada")
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Exception: {e}")


def main():
    """Ejecuta todos los tests"""
    
    print_separator("TEST DE DETECCIÓN DE ZONAS")
    print("API URL:", BASE_URL)
    print("\nZonas disponibles:")
    print("  • Salto")
    print("  • Termas del Daymán")
    print("  • Arenitas Blancas")
    
    # ========================================
    # TEST 1: Con direcciones
    # ========================================
    print_separator("TEST 1: Detección con DIRECCIONES")
    
    test_zone_with_address("18 de Julio 1234, Salto, Uruguay")
    print()
    
    test_zone_with_address("Termas del Daymán, Salto, Uruguay")
    print()
    
    test_zone_with_address("Arenitas Blancas, Salto, Uruguay")
    print()
    
    test_zone_with_address("Av. 18 de Julio, Montevideo, Uruguay")  # Fuera de zonas
    print()
    
    # ========================================
    # TEST 2: Con coordenadas directas
    # ========================================
    print_separator("TEST 2: Detección con COORDENADAS")
    
    # Coordenadas dentro de Salto
    test_zone_with_coordinates(-31.3820, -57.9640, "Centro de Salto")
    print()
    
    # Coordenadas de Termas del Daymán
    test_zone_with_coordinates(-31.4450, -57.9350, "Termas del Daymán")
    print()
    
    # Coordenadas de Arenitas Blancas
    test_zone_with_coordinates(-31.4180, -57.9600, "Arenitas Blancas")
    print()
    
    # Coordenadas en Montevideo (fuera de zonas)
    test_zone_with_coordinates(-34.9059, -56.1894, "Montevideo (fuera de zonas)")
    print()
    
    # ========================================
    # TEST 3: Validación de errores
    # ========================================
    print_separator("TEST 3: Validación de ERRORES")
    
    print("🔍 Probando: Sin address ni coordenadas (debe fallar)")
    try:
        response = requests.post(
            f"{BASE_URL}/zone",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()
    
    print("🔍 Probando: Address Y coordenadas al mismo tiempo (debe fallar)")
    try:
        response = requests.post(
            f"{BASE_URL}/zone",
            json={"address": "Salto", "lat": -31.38, "lon": -57.96},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()
    
    print_separator("TESTS COMPLETADOS")


if __name__ == "__main__":
    main()
