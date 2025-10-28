import json
from shapely.geometry import shape

# Cargar ZONAS_F
with open('app/data/ZONAS_F.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Encontrar zona 0
zona0 = None
for feature in data['features']:
    if feature['properties']['Codigo'] == 0:
        zona0 = feature
        break

print("="*70)
print("🗺️  ANÁLISIS DETALLADO DE ZONA 0")
print("="*70)

geom = zona0['geometry']
print(f"\nZona 0 tiene {len(geom['coordinates'])} polígonos:\n")

for i, polygon in enumerate(geom['coordinates']):
    print(f"📐 Polígono {i+1}:")
    print(f"   - Anillos: {len(polygon)}")
    
    # Analizar el anillo exterior
    exterior = polygon[0]
    print(f"   - Puntos en anillo exterior: {len(exterior)}")
    
    # Calcular bounds
    lons = [coord[0] for coord in exterior]
    lats = [coord[1] for coord in exterior]
    
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    
    print(f"   - Bounds:")
    print(f"     Lon: {min_lon:.6f} a {max_lon:.6f}")
    print(f"     Lat: {min_lat:.6f} a {max_lat:.6f}")
    
    # Calcular área aproximada
    width = max_lon - min_lon
    height = max_lat - min_lat
    
    print(f"   - Dimensiones:")
    print(f"     Ancho: {width:.6f}° ({width * 111:.2f} km aprox)")
    print(f"     Alto: {height:.6f}° ({height * 111:.2f} km aprox)")
    
    # Muestra primeros 3 puntos
    print(f"   - Primeros 3 puntos:")
    for j, coord in enumerate(exterior[:3]):
        print(f"     {j+1}. Lon: {coord[0]:.6f}, Lat: {coord[1]:.6f}")
    
    print()

# Bounds generales de toda la zona
poly_shape = shape(geom)
bounds = poly_shape.bounds
print("="*70)
print("📊 BOUNDS TOTALES DE ZONA 0:")
print("="*70)
print(f"   Min Lon: {bounds[0]:.6f}")
print(f"   Min Lat: {bounds[1]:.6f}")
print(f"   Max Lon: {bounds[2]:.6f}")
print(f"   Max Lat: {bounds[3]:.6f}")
print(f"\n   Ancho total: {(bounds[2] - bounds[0]):.6f}° ({(bounds[2] - bounds[0]) * 111:.2f} km)")
print(f"   Alto total: {(bounds[3] - bounds[1]):.6f}° ({(bounds[3] - bounds[1]) * 111:.2f} km)")

print("\n" + "="*70)
print("💡 REFERENCIA MONTEVIDEO:")
print("="*70)
print("   Centro: -34.9011, -56.1645")
print("   Bounds aproximados:")
print("     Lon: -56.43 a -55.95 (48 km)")
print("     Lat: -34.95 a -34.73 (24 km)")
print("\n")
