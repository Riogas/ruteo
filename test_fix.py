"""
Test simple para verificar el orden de las zonas después del fix
"""
import sys
sys.path.insert(0, 'app')

from zones import load_zones, find_zones_by_coordinates

# Cargar zonas
print("Cargando zonas...")
load_zones()

# Test con coordenadas del centro de Montevideo
lat, lon = -34.9055, -56.1913

print(f"\n📍 Probando coordenadas: ({lat}, {lon})")
print("="*60)

result = find_zones_by_coordinates(lat, lon)

print(f"\n🎯 RESULTADOS:")
print(f"-"*60)

if result.get('flete'):
    flete = result['flete']
    print(f"📦 Zona de Flete: {flete['codigo']} - {flete['name']}")
    print(f"   Área: {flete['area']:,.0f} m²")
else:
    print("📦 Zona de Flete: No detectada")

if result.get('global'):
    glob = result['global']
    print(f"🌍 Zona Global: {glob['codigo']} - {glob['name']}")
    print(f"   Área: {glob['area']:,.0f} m²")
else:
    print("🌍 Zona Global: No detectada")

print(f"\n" + "="*60)
