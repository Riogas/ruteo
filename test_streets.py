"""
Test del endpoint de listado de calles por departamento/localidad
"""

import requests
import json

# URL del API
BASE_URL = "http://localhost:8080"

print("=" * 70)
print("TEST: Listar calles de Uruguay")
print("=" * 70)
print()

# Test 1: Departamento completo (Montevideo - puede tardar)
print("1️⃣  TEST 1: Listando calles de TODO Montevideo")
print("   ⚠️  Puede tardar 30-60 segundos...")
print("-" * 70)

payload = {
    "departamento": "Montevideo"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/streets",
        json=payload,
        timeout=90  # Timeout largo para consulta completa
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Consulta exitosa!")
        print(f"   Departamento: {data['departamento']}")
        print(f"   Total calles: {data['total_calles']}")
        print()
        print(f"   Primeras 20 calles:")
        for i, calle in enumerate(data['calles'][:20], 1):
            print(f"   {i:2d}. {calle}")
        
        if len(data['calles']) > 20:
            print(f"   ... y {len(data['calles']) - 20} calles más")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("❌ Timeout: La consulta tardó más de 90 segundos")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 70)

# Test 2: Localidad específica (más rápido)
print("2️⃣  TEST 2: Listando calles de Ciudad de la Costa, Canelones")
print("   ⏱️  Debería ser más rápido (10-30 segundos)...")
print("-" * 70)

payload = {
    "departamento": "Canelones",
    "localidad": "Ciudad de la Costa"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/streets",
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Consulta exitosa!")
        print(f"   Departamento: {data['departamento']}")
        print(f"   Localidad:    {data['localidad']}")
        print(f"   Total calles: {data['total_calles']}")
        print()
        print(f"   Primeras 15 calles:")
        for i, calle in enumerate(data['calles'][:15], 1):
            print(f"   {i:2d}. {calle}")
        
        if len(data['calles']) > 15:
            print(f"   ... y {len(data['calles']) - 15} calles más")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("❌ Timeout: La consulta tardó más de 60 segundos")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 70)

# Test 3: Localidad pequeña (muy rápido)
print("3️⃣  TEST 3: Listando calles de Punta del Este, Maldonado")
print("   ⚡ Consulta rápida...")
print("-" * 70)

payload = {
    "departamento": "Maldonado",
    "localidad": "Punta del Este"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/streets",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Consulta exitosa!")
        print(f"   Departamento: {data['departamento']}")
        print(f"   Localidad:    {data['localidad']}")
        print(f"   Total calles: {data['total_calles']}")
        print()
        print(f"   Todas las calles:")
        for i, calle in enumerate(data['calles'], 1):
            print(f"   {i:2d}. {calle}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("❌ Timeout: La consulta tardó más de 30 segundos")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 70)
print("✅ Tests completados")
print("=" * 70)
