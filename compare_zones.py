import json
from shapely.geometry import shape
from shapely.validation import explain_validity

print("="*70)
print("📊 COMPARACIÓN: ZONA 0 ORIGINAL vs CORREGIDA")
print("="*70)

def analyze_zone0(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    zona0 = [f for f in data['features'] if f['properties']['Codigo'] == 0][0]
    geom = zona0['geometry']
    
    # Orientación del primer anillo
    def is_clockwise(coords):
        area = 0
        for i in range(len(coords) - 1):
            area += (coords[i+1][0] - coords[i][0]) * (coords[i+1][1] + coords[i][1])
        return area > 0
    
    first_ring = geom['coordinates'][0][0]
    cw = is_clockwise(first_ring)
    
    # Validación con Shapely
    poly_shape = shape(geom)
    
    return {
        'valid': poly_shape.is_valid,
        'area': poly_shape.area,
        'clockwise': cw,
        'bounds': poly_shape.bounds,
        'num_polygons': len(geom['coordinates']),
        'num_coords': len(first_ring)
    }

print("\n🔴 ARCHIVO ORIGINAL:")
print("-"*70)
original = analyze_zone0('app/data/ZONAS_F.geojson')
print(f"   ✓ Válido: {'SÍ ✅' if original['valid'] else 'NO ❌'}")
print(f"   📏 Área: {original['area']:,.2f}")
print(f"   🔄 Orientación: {'Horario ⟳ (MAL)' if original['clockwise'] else 'Antihorario ⟲ (BIEN)'}")
print(f"   📊 Polígonos: {original['num_polygons']}")
print(f"   📍 Coordenadas primer anillo: {original['num_coords']}")

print("\n🟢 ARCHIVO CORREGIDO:")
print("-"*70)
fixed = analyze_zone0('app/data/ZONAS_F_fixed.geojson')
print(f"   ✓ Válido: {'SÍ ✅' if fixed['valid'] else 'NO ❌'}")
print(f"   📏 Área: {fixed['area']:,.2f}")
print(f"   🔄 Orientación: {'Horario ⟳ (MAL)' if fixed['clockwise'] else 'Antihorario ⟲ (BIEN)'}")
print(f"   📊 Polígonos: {fixed['num_polygons']}")
print(f"   📍 Coordenadas primer anillo: {fixed['num_coords']}")

print("\n📊 CAMBIOS:")
print("-"*70)
if original['clockwise'] != fixed['clockwise']:
    print("   ✅ Orientación CORREGIDA")
else:
    print("   ⚠️  Orientación SIN CAMBIOS")

if original['area'] != fixed['area']:
    print(f"   ✅ Área cambió de {original['area']:,.2f} a {fixed['area']:,.2f}")
else:
    print("   ℹ️  Área sin cambios")

print("\n" + "="*70)
print("💡 RECOMENDACIÓN:")
print("="*70)
if not fixed['clockwise'] and fixed['valid']:
    print("   ✅ El archivo corregido está LISTO para usar")
    print("   Puedes reemplazar el original con seguridad.")
    print()
    print("   Comandos para reemplazar:")
    print("   copy app\\data\\ZONAS_F.geojson app\\data\\ZONAS_F_backup.geojson")
    print("   copy app\\data\\ZONAS_F_fixed.geojson app\\data\\ZONAS_F.geojson")
    print("   copy app\\data\\ZONAS_4.geojson app\\data\\ZONAS_4_backup.geojson")
    print("   copy app\\data\\ZONAS_4_fixed.geojson app\\data\\ZONAS_4.geojson")
else:
    print("   ⚠️  Revisar manualmente antes de reemplazar")

print()
