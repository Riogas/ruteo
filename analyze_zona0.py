import json
from shapely.geometry import shape
from shapely.validation import explain_validity

# Cargar ZONAS_F
with open('app/data/ZONAS_F.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Encontrar zona 0
zona0 = None
for feature in data['features']:
    if feature['properties']['Codigo'] == 0:
        zona0 = feature
        break

if not zona0:
    print("❌ No se encontró la zona 0")
    exit(1)

print("="*70)
print("📊 ANÁLISIS DE ZONA 0 (Zona de Flete)")
print("="*70)

# Información básica
print(f"\n🏷️  Código: {zona0['properties']['Codigo']}")
print(f"📏 Área: {zona0['properties'].get('Shape_Area', 0):,.0f} m²")
print(f"📐 Perímetro: {zona0['properties'].get('PERIMETER', 'N/A')}")

# Estructura de geometría
geom = zona0['geometry']
print(f"\n📐 Geometría:")
print(f"   - Tipo: {geom['type']}")
print(f"   - Número de polígonos: {len(geom['coordinates'])}")

# Analizar cada polígono
for i, polygon in enumerate(geom['coordinates'][:5]):  # Primeros 5 polígonos
    print(f"\n   Polígono {i+1}:")
    print(f"     - Anillos: {len(polygon)}")
    print(f"     - Puntos en anillo exterior: {len(polygon[0])}")
    
    if len(polygon) > 1:
        print(f"     - Anillos interiores (huecos): {len(polygon) - 1}")

if len(geom['coordinates']) > 5:
    print(f"\n   ... y {len(geom['coordinates']) - 5} polígonos más")

# Validar geometría con Shapely
print(f"\n🔍 Validación con Shapely:")
print("-"*70)

try:
    poly_shape = shape(geom)
    
    # Verificar si es válida
    is_valid = poly_shape.is_valid
    print(f"   ✓ ¿Es válida?: {'SÍ ✅' if is_valid else 'NO ❌'}")
    
    if not is_valid:
        reason = explain_validity(poly_shape)
        print(f"   ❌ Razón: {reason}")
    
    # Propiedades
    print(f"\n   📊 Propiedades:")
    print(f"     - Área calculada: {poly_shape.area:,.0f}")
    print(f"     - Es simple: {poly_shape.is_simple}")
    print(f"     - Está vacía: {poly_shape.is_empty}")
    print(f"     - Bounds: {poly_shape.bounds}")
    
    # Verificar si tiene auto-intersecciones
    if hasattr(poly_shape, 'exterior'):
        print(f"     - Exterior tiene {len(poly_shape.exterior.coords)} puntos")
    
except Exception as e:
    print(f"   ❌ Error al validar: {e}")

# Verificar algunos puntos de coordenadas
print(f"\n🌍 Muestra de coordenadas (primeros 3 puntos):")
print("-"*70)
first_ring = geom['coordinates'][0][0]
for i, coord in enumerate(first_ring[:3]):
    lon, lat = coord[0], coord[1]
    print(f"   {i+1}. Lon: {lon:.6f}, Lat: {lat:.6f}")

# Verificar orden de coordenadas (sentido horario vs antihorario)
print(f"\n🔄 Verificación de orientación:")
print("-"*70)

def is_clockwise(coords):
    """Verifica si las coordenadas van en sentido horario"""
    area = 0
    for i in range(len(coords) - 1):
        area += (coords[i+1][0] - coords[i][0]) * (coords[i+1][1] + coords[i][1])
    return area > 0

first_ring = geom['coordinates'][0][0]
cw = is_clockwise(first_ring)
print(f"   Anillo exterior: {'Sentido horario ⟳' if cw else 'Sentido antihorario ⟲'}")
print(f"   (GeoJSON exterior debe ser antihorario, interiores horarios)")

if cw:
    print(f"   ⚠️  PROBLEMA: El anillo exterior está en sentido horario!")
    print(f"   Esto puede causar problemas en algunas librerías de mapas.")

print("\n" + "="*70)
