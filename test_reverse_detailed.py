"""Test de geocodificación inversa con las coordenadas calculadas"""
import json
from urllib.request import Request, urlopen

def test_reverse(lat, lon, descripcion):
    """Prueba reverse geocoding"""
    url = "http://localhost:8080/api/v1/reverse-geocode"
    data = {"lat": lat, "lon": lon}
    json_data = json.dumps(data).encode('utf-8')
    req = Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    
    print(f"{descripcion}")
    print(f"  Input: lat={lat:.6f}, lon={lon:.6f}")
    try:
        with urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"  ✅ Dirección: {result.get('street', 'N/A')}")
            if result.get('corner_1') or result.get('corner_2'):
                c1 = result.get('corner_1', '?')
                c2 = result.get('corner_2', '?')
                print(f"  📍 Esquinas: entre {c1} y {c2}")
            else:
                print(f"  ⚠️  Sin esquinas detectadas")
            print(f"  📋 Ciudad: {result.get('city', 'N/A')}")
            return result
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None
    finally:
        print()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST DE GEOCODIFICACIÓN INVERSA")
    print("="*70 + "\n")
    
    # Test 1: Coordenadas de 18 de Julio y Ejido (calculadas con Overpass)
    print("Test 1: Coordenadas de 18 de Julio y Ejido")
    test_reverse(-34.905111, -56.186918, "1️⃣  18 de Julio y Ejido (Overpass):")
    
    # Test 2: Coordenadas de 18 de Julio y Yí (calculadas con fallback)
    print("Test 2: Coordenadas de 18 de Julio y Yí")
    test_reverse(-34.904269, -56.187903, "2️⃣  18 de Julio y Yí (Fallback):")
    
    # Test 3: Coordenadas de 18 de Julio y Río Negro
    print("Test 3: Coordenadas de 18 de Julio y Río Negro")
    test_reverse(-34.906067, -56.193614, "3️⃣  18 de Julio y Río Negro (Overpass):")
    
    # Test 4: Punto conocido - Obelisco (18 de Julio y Artigas)
    print("Test 4: Obelisco (18 de Julio y Artigas)")
    test_reverse(-34.905586, -56.165340, "4️⃣  Obelisco (18 de Julio y Artigas):")
    
    # Test 5: Palacio Legislativo
    print("Test 5: Palacio Legislativo")
    test_reverse(-34.8919, -56.1865, "5️⃣  Palacio Legislativo:")
    
    print("="*70)
    print("VERIFICAR:")
    print("  • ¿Detecta las esquinas correctamente?")
    print("  • ¿El formato es 'Calle entre Esquina1 y Esquina2'?")
    print("  • ¿Las esquinas corresponden a la ubicación real?")
    print("="*70 + "\n")
