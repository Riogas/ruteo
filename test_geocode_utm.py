"""
Test rápido para verificar geocodificación con coordenadas UTM
"""

import requests
import json

# URL del API
BASE_URL = "http://localhost:8080"

# Test 1: Geocodificación de dirección con número
print("=" * 60)
print("TEST 1: Geocodificar '18 de Julio 1234, Montevideo'")
print("=" * 60)

payload = {
    "street": "18 de Julio 1234",
    "city": "Montevideo",
    "country": "Uruguay"
}

response = requests.post(f"{BASE_URL}/api/v1/geocode", json=payload)

if response.status_code == 200:
    data = response.json()
    print("✅ Geocodificación exitosa:")
    print(f"   Latitud:  {data['lat']}")
    print(f"   Longitud: {data['lon']}")
    if 'utm_x' in data:
        print(f"   UTM X:    {data['utm_x']:.2f}")
        print(f"   UTM Y:    {data['utm_y']:.2f}")
        print(f"   Zona UTM: {data['utm_zone']}")
    else:
        print("   ⚠️  No se calcularon coordenadas UTM")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print()

# Test 2: Geocodificación de esquina
print("=" * 60)
print("TEST 2: Geocodificar esquina 'Gaboto y Magallanes'")
print("=" * 60)

payload = {
    "street": "18 de Julio",
    "corner_1": "Gaboto",
    "city": "Montevideo",
    "country": "Uruguay"
}

response = requests.post(f"{BASE_URL}/api/v1/geocode", json=payload)

if response.status_code == 200:
    data = response.json()
    print("✅ Geocodificación exitosa:")
    print(f"   Latitud:  {data['lat']}")
    print(f"   Longitud: {data['lon']}")
    if 'utm_x' in data:
        print(f"   UTM X:    {data['utm_x']:.2f}")
        print(f"   UTM Y:    {data['utm_y']:.2f}")
        print(f"   Zona UTM: {data['utm_zone']}")
    else:
        print("   ⚠️  No se calcularon coordenadas UTM")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print()

# Test 3: Reverse geocoding (también debería tener UTM)
print("=" * 60)
print("TEST 3: Reverse geocoding con coordenadas de Gaboto/Magallanes")
print("=" * 60)

payload = {
    "lat": -34.90297,
    "lon": -56.17886
}

response = requests.post(f"{BASE_URL}/api/v1/reverse-geocode", json=payload)

if response.status_code == 200:
    data = response.json()
    print("✅ Reverse geocoding exitoso:")
    print(f"   Calle:    {data.get('street')}")
    print(f"   Esquina1: {data.get('corner_1')}")
    print(f"   Esquina2: {data.get('corner_2')}")
    if 'coordinates' in data and data['coordinates']:
        coords = data['coordinates']
        print(f"   Latitud:  {coords['lat']}")
        print(f"   Longitud: {coords['lon']}")
        if 'utm_x' in coords:
            print(f"   UTM X:    {coords['utm_x']:.2f}")
            print(f"   UTM Y:    {coords['utm_y']:.2f}")
            print(f"   Zona UTM: {coords['utm_zone']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
