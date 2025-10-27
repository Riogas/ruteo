"""Test rápido de geocodificación con esquinas"""
import json
import sys

# Usar urllib en lugar de requests (está en stdlib)
try:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
except ImportError:
    print("Error: No se pudo importar urllib")
    sys.exit(1)

def test_geocode(data):
    """Prueba geocodificación con los datos dados"""
    url = "http://localhost:8080/api/v1/geocode"
    
    # Convertir a JSON
    json_data = json.dumps(data).encode('utf-8')
    
    # Crear request
    req = Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    
    try:
        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
    except HTTPError as e:
        print(f"Error HTTP {e.code}: {e.read().decode('utf-8')}")
        return None
    except URLError as e:
        print(f"Error de conexión: {e.reason}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("\n=== TEST 1: Geocoding con calle y esquina ===")
    data1 = {
        "street": "Avenida 18 de Julio",
        "corner_1": "Ejido",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    print(f"Input: {json.dumps(data1, indent=2, ensure_ascii=False)}")
    print("\nOutput:")
    test_geocode(data1)
    
    print("\n\n=== TEST 2: Geocoding con calle, dos esquinas ===")
    data2 = {
        "street": "Avenida 18 de Julio",
        "corner_1": "Ejido",
        "corner_2": "Yí",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    print(f"Input: {json.dumps(data2, indent=2, ensure_ascii=False)}")
    print("\nOutput:")
    test_geocode(data2)
    
    print("\n\n=== TEST 3: Geocoding solo con esquinas (sin calle) ===")
    data3 = {
        "street": "",
        "corner_1": "Ejido",
        "corner_2": "18 de Julio",
        "city": "Montevideo",
        "country": "Uruguay"
    }
    print(f"Input: {json.dumps(data3, indent=2, ensure_ascii=False)}")
    print("\nOutput:")
    test_geocode(data3)
