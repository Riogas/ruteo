"""Test para verificar que esquinas diferentes dan coordenadas diferentes"""
import json
import sys
from urllib.request import Request, urlopen

def test_geocode(data, descripcion):
    """Prueba geocodificación con los datos dados"""
    url = "http://localhost:8080/api/v1/geocode"
    json_data = json.dumps(data).encode('utf-8')
    req = Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    
    try:
        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"{descripcion}")
            print(f"  Input: {data['street']} esquina {data.get('corner_1', 'N/A')}")
            print(f"  Output: lat={result['lat']:.6f}, lon={result['lon']:.6f}")
            return result
    except Exception as e:
        print(f"  Error: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST: ¿Esquinas diferentes dan coordenadas diferentes?")
    print("="*70 + "\n")
    
    # TEST 1: 18 de Julio esquina Ejido
    test1 = {
        "street": "Avenida 18 de Julio",
        "corner_1": "Ejido",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    result1 = test_geocode(test1, "1️⃣  18 de Julio esquina Ejido:")
    
    print()
    
    # TEST 2: 18 de Julio esquina Yí (diferente esquina, misma calle)
    test2 = {
        "street": "Avenida 18 de Julio",
        "corner_1": "Yí",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    result2 = test_geocode(test2, "2️⃣  18 de Julio esquina Yí:")
    
    print()
    
    # TEST 3: 18 de Julio esquina Río Negro (otra esquina más)
    test3 = {
        "street": "Avenida 18 de Julio",
        "corner_1": "Río Negro",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    result3 = test_geocode(test3, "3️⃣  18 de Julio esquina Río Negro:")
    
    print("\n" + "="*70)
    print("ANÁLISIS:")
    print("="*70)
    
    if result1 and result2:
        if result1['lat'] == result2['lat'] and result1['lon'] == result2['lon']:
            print("❌ PROBLEMA CONFIRMADO: Ejido y Yí dan las MISMAS coordenadas")
            print(f"   Ambas: lat={result1['lat']:.6f}, lon={result1['lon']:.6f}")
        else:
            print("✅ OK: Ejido y Yí dan coordenadas DIFERENTES")
            dist = ((result1['lat'] - result2['lat'])**2 + (result1['lon'] - result2['lon'])**2)**0.5
            print(f"   Distancia: {dist:.6f} grados (~{dist*111:.0f} km)")
    
    if result1 and result3:
        if result1['lat'] == result3['lat'] and result1['lon'] == result3['lon']:
            print("❌ PROBLEMA CONFIRMADO: Ejido y Río Negro dan las MISMAS coordenadas")
        else:
            print("✅ OK: Ejido y Río Negro dan coordenadas DIFERENTES")
    
    print()
