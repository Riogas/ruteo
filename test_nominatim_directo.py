"""Test directo a Nominatim para entender cómo geocodifica intersecciones"""
from geopy.geocoders import Nominatim
import time

# Configurar Nominatim igual que en el código
geolocator = Nominatim(
    user_agent="ruteo_test_v1.0",
    timeout=10,
    domain="nominatim.riogas.uy",
    scheme="http"
)

# Probar diferentes formatos
queries = [
    "Avenida 18 de Julio, Montevideo, Uruguay",
    "Ejido & 18 de Julio, Montevideo, Uruguay",
    "18 de Julio & Ejido, Montevideo, Uruguay",
    "Ejido y 18 de Julio, Montevideo, Uruguay",
    "Yí & 18 de Julio, Montevideo, Uruguay",
    "18 de Julio & Yí, Montevideo, Uruguay",
]

print("\n" + "="*70)
print("TEST DIRECTO A NOMINATIM - ¿Cómo maneja intersecciones?")
print("="*70 + "\n")

for query in queries:
    print(f"Query: {query}")
    try:
        location = geolocator.geocode(query)
        if location:
            print(f"  ✓ lat={location.latitude:.6f}, lon={location.longitude:.6f}")
            print(f"  📍 {location.address}")
        else:
            print(f"  ✗ No encontrado")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    time.sleep(1.1)  # Rate limit

print("="*70)
print("CONCLUSIÓN:")
print("Si todas dan las mismas coordenadas, el problema es que Nominatim")
print("NO está interpretando las intersecciones correctamente.")
print("="*70 + "\n")
