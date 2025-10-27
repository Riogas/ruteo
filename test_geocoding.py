#!/usr/bin/env python3
"""
Script de prueba para los endpoints de geocodificación.

Prueba:
1. Geocoding: Dirección → Coordenadas
2. Reverse Geocoding: Coordenadas → Dirección
"""

import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

def test_geocode():
    """Prueba: Dirección → Coordenadas"""
    print("=" * 70)
    print("  TEST 1: GEOCODING (Dirección → Coordenadas)")
    print("=" * 70)
    print()
    
    # Direcciones de prueba en Montevideo
    addresses = [
        {
            "street": "18 de Julio 1234",
            "city": "Montevideo",
            "country": "Uruguay"
        },
        {
            "street": "Av. Italia 2500",
            "city": "Montevideo",
            "country": "Uruguay"
        },
        {
            "street": "Bvar. Artigas 1856",
            "city": "Montevideo",
            "country": "Uruguay"
        }
    ]
    
    results = []
    
    for i, addr in enumerate(addresses, 1):
        print(f"{i}. Geocodificando: {addr['street']}, {addr['city']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/geocode",
                json=addr,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                coords = response.json()
                print(f"   ✅ Coordenadas: ({coords['lat']:.6f}, {coords['lon']:.6f})")
                results.append((addr, coords))
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    return results


def test_reverse_geocode(coordinates_list):
    """Prueba: Coordenadas → Dirección"""
    print("=" * 70)
    print("  TEST 2: REVERSE GEOCODING (Coordenadas → Dirección)")
    print("=" * 70)
    print()
    
    if not coordinates_list:
        # Si no hay resultados del test anterior, usar coordenadas fijas
        coordinates_list = [
            ({"street": "Test"}, {
                "lat": -34.9011,
                "lon": -56.1645,
                "address": "Montevideo, Uruguay"
            })
        ]
    
    for i, (original_addr, coords) in enumerate(coordinates_list, 1):
        print(f"{i}. Reverse geocoding: ({coords['lat']:.6f}, {coords['lon']:.6f})")
        print(f"   Dirección original: {original_addr['street']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/reverse-geocode",
                json=coords,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                address = response.json()
                print(f"   ✅ Dirección encontrada:")
                print(f"      Calle: {address.get('street', 'N/A')}")
                print(f"      Ciudad: {address.get('city', 'N/A')}")
                print(f"      País: {address.get('country', 'N/A')}")
                print(f"      Dirección completa: {address.get('full_address', 'N/A')}")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()


def test_round_trip():
    """Prueba: Dirección → Coordenadas → Dirección (round trip)"""
    print("=" * 70)
    print("  TEST 3: ROUND TRIP (Dirección → Coordenadas → Dirección)")
    print("=" * 70)
    print()
    
    original_address = {
        "street": "Colón 1234",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    
    print(f"📍 Dirección original: {original_address['street']}, {original_address['city']}")
    print()
    
    # Paso 1: Geocoding
    print("1️⃣  Geocoding...")
    try:
        response = requests.post(
            f"{BASE_URL}/geocode",
            json=original_address,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"   ❌ Error en geocoding: {response.status_code}")
            return
        
        coords = response.json()
        print(f"   ✅ Coordenadas: ({coords['lat']:.6f}, {coords['lon']:.6f})")
        print()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Paso 2: Reverse Geocoding
    print("2️⃣  Reverse Geocoding...")
    try:
        response = requests.post(
            f"{BASE_URL}/reverse-geocode",
            json=coords,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"   ❌ Error en reverse geocoding: {response.status_code}")
            return
        
        final_address = response.json()
        print(f"   ✅ Dirección recuperada:")
        print(f"      {final_address.get('full_address', 'N/A')}")
        print()
        
        # Comparación
        print("📊 COMPARACIÓN:")
        print(f"   Original: {original_address['street']}")
        print(f"   Recuperada: {final_address.get('street', 'N/A')}")
        
        if original_address['street'].lower() in final_address.get('street', '').lower():
            print("   ✅ COINCIDENCIA PARCIAL")
        else:
            print("   ⚠️  DIRECCIONES DIFERENTES (normal por geocodificación)")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Ejecuta todas las pruebas"""
    print()
    print("🧪 PRUEBAS DE GEOCODIFICACIÓN")
    print()
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:8080/health", timeout=2)
        if response.status_code != 200:
            print("❌ Servidor no disponible en http://localhost:8080")
            print("   Ejecuta: python start_server.py")
            return
    except Exception:
        print("❌ Servidor no disponible en http://localhost:8080")
        print("   Ejecuta: python start_server.py")
        return
    
    print("✅ Servidor activo")
    print()
    
    # Test 1: Geocoding
    coords_results = test_geocode()
    
    # Test 2: Reverse Geocoding
    test_reverse_geocode(coords_results)
    
    # Test 3: Round trip
    test_round_trip()
    
    print()
    print("=" * 70)
    print("  ✅ TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 70)
    print()
    print("💡 Tip: Puedes probar manualmente en http://localhost:8080/docs")
    print()


if __name__ == "__main__":
    main()
