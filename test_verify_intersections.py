"""Test para verificar que las intersecciones calculadas son correctas"""
import json
from urllib.request import Request, urlopen

def test_and_verify(data, descripcion, lat_esperada=None, lon_esperada=None):
    """Prueba geocodificación y muestra la dirección completa"""
    url = "http://localhost:8080/api/v1/geocode"
    json_data = json.dumps(data).encode('utf-8')
    req = Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    
    print(f"{descripcion}")
    try:
        # Timeout aumentado a 60s para Overpass + fallback
        with urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            lat, lon = result['lat'], result['lon']
            print(f"  Resultado: lat={lat:.6f}, lon={lon:.6f}")
            
            # Hacer reverse geocoding para ver qué dirección es
            reverse_url = "http://localhost:8080/api/v1/reverse-geocode"
            reverse_data = json.dumps({"lat": lat, "lon": lon}).encode('utf-8')
            reverse_req = Request(reverse_url, data=reverse_data, headers={'Content-Type': 'application/json'})
            
            with urlopen(reverse_req, timeout=15) as reverse_response:
                address = json.loads(reverse_response.read().decode('utf-8'))
                print(f"  Dirección: {address.get('street', 'N/A')}")
                if address.get('corner_1') and address.get('corner_2'):
                    print(f"  Esquinas: entre {address['corner_1']} y {address['corner_2']}")
            
            # Verificar si está cerca de lo esperado
            if lat_esperada and lon_esperada:
                dist = ((lat - lat_esperada)**2 + (lon - lon_esperada)**2)**0.5
                if dist < 0.001:  # ~100 metros
                    print(f"  ✅ Ubicación correcta (dist={dist:.6f})")
                else:
                    print(f"  ⚠️  Verificar ubicación (dist={dist:.6f})")
            
            return result
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None
    finally:
        print()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("VERIFICACIÓN DE INTERSECCIONES CALCULADAS")
    print("="*70 + "\n")
    
    # Test 1: 18 de Julio y Ejido
    test1 = {
        "street": "Avenida 18 de Julio",
        "corner_1": "Ejido",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    test_and_verify(test1, "1️⃣  18 de Julio y Ejido:", -34.9055, -56.1866)
    
    # Test 2: 18 de Julio y Yí (el problemático)
    test2 = {
        "street": "Avenida 18 de Julio",
        "corner_1": "Yí",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    # Coordenadas reales de 18 de Julio y Yí: -34.9043, -56.1879
    test_and_verify(test2, "2️⃣  18 de Julio y Yí:", -34.9043, -56.1879)
    
    # Test 3: 18 de Julio y Río Negro
    test3 = {
        "street": "Avenida 18 de Julio",
        "corner_1": "Río Negro",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    test_and_verify(test3, "3️⃣  18 de Julio y Río Negro:", -34.9058, -56.1900)
    
    print("="*70)
    print("NOTA: Revisa las direcciones de reverse geocoding")
    print("      para confirmar que las coordenadas están en el lugar correcto")
    print("="*70 + "\n")
