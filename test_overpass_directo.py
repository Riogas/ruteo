"""Test directo a Overpass API para ver qué está pasando"""
import requests
import time

# URL de Overpass API
overpass_url = "https://overpass-api.de/api/interpreter"

# Query simple para una calle en Montevideo
street_name = "Avenida 18 de Julio"
city = "Montevideo"

# Query optimizada con bounding box (MUCHO más rápido)
bbox = "-34.95,-56.25,-34.75,-56.05"  # Montevideo

query = f"""
[out:json][timeout:10][bbox:{bbox}];
way["highway"]["name"="{street_name}"];
out geom;
"""

print(f"\n🌐 Consultando Overpass API directamente...")
print(f"Calle: {street_name}")
print(f"Ciudad: {city}")
print(f"\nQuery:")
print(query)
print("\n" + "="*70)

start = time.time()

try:
    print("⏱️  Enviando request...")
    response = requests.post(overpass_url, data={"data": query}, timeout=15)
    
    elapsed = time.time() - start
    print(f"✅ Respuesta recibida en {elapsed:.2f} segundos")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nElementos encontrados: {len(data.get('elements', []))}")
        
        if data.get('elements'):
            print("\nPrimeros 3 elementos:")
            for i, elem in enumerate(data['elements'][:3]):
                print(f"\n  Elemento {i+1}:")
                print(f"    Type: {elem.get('type')}")
                print(f"    ID: {elem.get('id')}")
                print(f"    Geometría: {len(elem.get('geometry', []))} nodos")
                if elem.get('tags'):
                    print(f"    Tags: {elem['tags'].get('name', 'N/A')}")
        else:
            print("\n⚠️ No se encontraron elementos!")
            print("Respuesta completa:")
            print(data)
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f"⏱️ TIMEOUT después de {elapsed:.2f} segundos")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Error después de {elapsed:.2f} segundos: {e}")

print("\n" + "="*70 + "\n")
