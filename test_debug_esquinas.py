"""Test de debug para ver qué queries está haciendo Nominatim"""
import json
from urllib.request import Request, urlopen

def test_geocode_debug(data, descripcion):
    """Prueba geocodificación y muestra detalles"""
    url = "http://localhost:8080/api/v1/geocode"
    json_data = json.dumps(data).encode('utf-8')
    req = Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    
    print(f"\n{descripcion}")
    print(f"  Input JSON: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"  Output: lat={result['lat']:.6f}, lon={result['lon']:.6f}")
            return result
    except Exception as e:
        print(f"  Error: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST DE DEBUG - Ver logs del servidor para ver queries de Nominatim")
    print("="*70)
    
    # Test 1: Solo esquinas (sin calle principal)
    test1 = {
        "street": "",
        "corner_1": "Ejido",
        "corner_2": "18 de Julio",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    test_geocode_debug(test1, "🔍 TEST 1: Solo Ejido y 18 de Julio (sin calle)")
    
    print("\n" + "-"*70)
    
    # Test 2: Otras dos esquinas
    test2 = {
        "street": "",
        "corner_1": "Yí",
        "corner_2": "18 de Julio",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    test_geocode_debug(test2, "🔍 TEST 2: Solo Yí y 18 de Julio (sin calle)")
    
    print("\n" + "="*70)
    print("⚠️  REVISA LOS LOGS DEL SERVIDOR para ver:")
    print("   - Qué strings de dirección se están construyendo")
    print("   - En qué orden se están probando")
    print("   - Cuál formato está teniendo éxito")
    print("="*70 + "\n")
