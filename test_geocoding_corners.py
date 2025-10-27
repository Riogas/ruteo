#!/usr/bin/env python3
"""
Script de prueba para geocodificación con esquinas.

Prueba los nuevos campos corner_1 y corner_2 del endpoint de geocoding.
"""

import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

def test_geocode_with_corners():
    """Prueba geocodificación usando esquinas"""
    print("=" * 80)
    print("  🧪 TEST: GEOCODIFICACIÓN CON ESQUINAS")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "name": "Con número de puerta (tradicional)",
            "data": {
                "street": "Av. 18 de Julio 1234",
                "city": "Montevideo",
                "country": "Uruguay"
            }
        },
        {
            "name": "Con 2 esquinas (sin número)",
            "data": {
                "street": "Av. 18 de Julio",
                "corner_1": "Río Negro",
                "corner_2": "Ejido",
                "city": "Montevideo",
                "country": "Uruguay"
            }
        },
        {
            "name": "Con 1 esquina (sin número)",
            "data": {
                "street": "Av. 18 de Julio",
                "corner_1": "Río Negro",
                "city": "Montevideo",
                "country": "Uruguay"
            }
        },
        {
            "name": "Número + esquina (combinado)",
            "data": {
                "street": "Av. Italia 2500",
                "corner_1": "Bvar. Artigas",
                "city": "Montevideo",
                "country": "Uruguay"
            }
        },
        {
            "name": "Intersección céntrica",
            "data": {
                "street": "18 de Julio",
                "corner_1": "Ejido",
                "corner_2": "Río Negro",
                "city": "Montevideo",
                "country": "Uruguay"
            }
        },
        {
            "name": "Avenida sin número con esquinas",
            "data": {
                "street": "Bvar. Artigas",
                "corner_1": "Av. Italia",
                "corner_2": "Rivera",
                "city": "Montevideo",
                "country": "Uruguay"
            }
        }
    ]
    
    successful = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test['name']}")
        print(f"   📝 Dirección:")
        
        # Mostrar dirección construida
        street = test['data']['street']
        corner_1 = test['data'].get('corner_1')
        corner_2 = test['data'].get('corner_2')
        
        if corner_1 and corner_2:
            print(f"      {street} entre {corner_1} y {corner_2}")
        elif corner_1:
            print(f"      {street} esquina {corner_1}")
        else:
            print(f"      {street}")
        
        print(f"      {test['data']['city']}, {test['data']['country']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/geocode",
                json=test['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                coords = response.json()
                print(f"   ✅ ÉXITO")
                print(f"      Lat: {coords['lat']:.6f}")
                print(f"      Lon: {coords['lon']:.6f}")
                successful += 1
            else:
                print(f"   ❌ Error {response.status_code}")
                try:
                    error = response.json()
                    print(f"      {error.get('error', error.get('detail', 'Error desconocido'))}")
                except:
                    print(f"      {response.text[:100]}")
                failed += 1
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  TIMEOUT (>10s)")
            failed += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
        
        print()
    
    print("=" * 80)
    print(f"  📊 RESUMEN")
    print("=" * 80)
    print(f"  ✅ Exitosos: {successful}/{len(test_cases)}")
    print(f"  ❌ Fallidos:  {failed}/{len(test_cases)}")
    print("=" * 80)
    print()


def test_compare_formats():
    """Compara resultados entre formato con número vs con esquinas"""
    print()
    print("=" * 80)
    print("  🔄 TEST: COMPARACIÓN DE FORMATOS")
    print("=" * 80)
    print()
    
    # Test 1: Con número
    print("1️⃣  Geocodificando con NÚMERO DE PUERTA:")
    addr_with_number = {
        "street": "Av. 18 de Julio 1234",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/geocode",
            json=addr_with_number,
            timeout=10
        )
        
        if response.status_code == 200:
            coords1 = response.json()
            print(f"   ✅ ({coords1['lat']:.6f}, {coords1['lon']:.6f})")
        else:
            print(f"   ❌ Error {response.status_code}")
            coords1 = None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        coords1 = None
    
    print()
    
    # Test 2: Con esquinas cercanas
    print("2️⃣  Geocodificando con ESQUINAS (aproximado):")
    addr_with_corners = {
        "street": "Av. 18 de Julio",
        "corner_1": "Ejido",
        "corner_2": "Río Negro",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/geocode",
            json=addr_with_corners,
            timeout=10
        )
        
        if response.status_code == 200:
            coords2 = response.json()
            print(f"   ✅ ({coords2['lat']:.6f}, {coords2['lon']:.6f})")
        else:
            print(f"   ❌ Error {response.status_code}")
            coords2 = None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        coords2 = None
    
    print()
    
    # Comparar distancia
    if coords1 and coords2:
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1 = radians(coords1['lat']), radians(coords1['lon'])
        lat2, lon2 = radians(coords2['lat']), radians(coords2['lon'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = 6371000 * c  # Radio de la Tierra en metros
        
        print("📏 DISTANCIA ENTRE COORDENADAS:")
        print(f"   {distance:.1f} metros")
        print()
        
        if distance < 100:
            print("   ✅ Muy cercanas (< 100m) - Excelente precisión!")
        elif distance < 500:
            print("   ⚠️  Relativamente cercanas (< 500m) - Buena aproximación")
        else:
            print("   ⚠️  Distantes (> 500m) - Revisar esquinas")
    
    print()


def main():
    """Ejecuta todas las pruebas"""
    print()
    print("🗺️  PRUEBAS DE GEOCODIFICACIÓN CON ESQUINAS")
    print()
    
    # Verificar servidor
    try:
        response = requests.get("http://localhost:8080/health", timeout=2)
        if response.status_code != 200:
            print("❌ Servidor no disponible")
            return
    except Exception:
        print("❌ Servidor no disponible en http://localhost:8080")
        print("   Ejecuta: python start_server.py")
        return
    
    print("✅ Servidor activo")
    print()
    
    # Pruebas
    test_geocode_with_corners()
    test_compare_formats()
    
    print("=" * 80)
    print("  ✅ PRUEBAS COMPLETADAS")
    print("=" * 80)
    print()
    print("💡 Ventajas del sistema con esquinas:")
    print("   • Funciona sin número de puerta")
    print("   • Útil para direcciones ambiguas")
    print("   • Mejor cobertura en Uruguay")
    print("   • Múltiples formatos automáticos")
    print()


if __name__ == "__main__":
    main()
