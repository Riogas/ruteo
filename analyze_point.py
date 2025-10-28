"""
Verificar por qué 21 de setiembre 2570 da zona 9 en lugar de zona 0
"""

import json
from shapely.geometry import Point, shape

# Coordenadas de la dirección: 21 de setiembre 2570, Montevideo
# Según Nominatim: -34.9149255, -56.1601851
lat = -34.9149255
lon = -56.1601851

print("="*70)
print("🔬 ANÁLISIS DE DETECCIÓN DE ZONA")
print("="*70)
print(f"\n📍 Dirección: 21 de setiembre 2570, Montevideo")
print(f"   Latitud: {lat}")
print(f"   Longitud: {lon}")

point = Point(lon, lat)

# Cargar ZONAS_F
with open('app/data/ZONAS_F.geojson', 'r', encoding='utf-8') as f:
    zonas_f = json.load(f)

print(f"\n🗺️  Verificando en {len(zonas_f['features'])} zonas de flete:")
print("="*70)

# Ordenar por área (como en el código real)
features_sorted = sorted(
    zonas_f['features'],
    key=lambda f: f['properties'].get('Shape_Area', 0)
)

print("\n🔍 ORDEN DE BÚSQUEDA (por área, de menor a mayor):\n")

zonas_que_contienen = []

for i, feature in enumerate(features_sorted):
    codigo = feature['properties'].get('Codigo')
    nombre = feature['properties'].get('OBJECTID', '?')
    area = feature['properties'].get('Shape_Area', 0)
    geom = shape(feature['geometry'])
    
    contains = geom.contains(point)
    
    if contains:
        zonas_que_contienen.append({
            'orden': i+1,
            'codigo': codigo,
            'area': area,
            'nombre': nombre
        })
        status = "✅ CONTIENE EL PUNTO"
    else:
        status = "❌"
    
    print(f"{i+1:2}. Zona {codigo:2} - Área: {area:15,.0f} m² {status}")

print("\n" + "="*70)
print("📊 RESUMEN")
print("="*70)

if zonas_que_contienen:
    print(f"\n✅ El punto está contenido en {len(zonas_que_contienen)} zona(s):\n")
    for zona in zonas_que_contienen:
        print(f"   • Zona {zona['codigo']} (orden de búsqueda: {zona['orden']}, área: {zona['area']:,.0f} m²)")
    
    primera = zonas_que_contienen[0]
    print(f"\n🎯 ZONA RETORNADA (primera en el orden): Zona {primera['codigo']}")
    
    if primera['codigo'] != 0:
        # Verificar específicamente la zona 0
        print(f"\n⚠️  PROBLEMA: Debería retornar zona 0, pero retorna zona {primera['codigo']}")
        print("\n🔍 Analizando zona 0 específicamente:")
        
        zona_0 = next((f for f in zonas_f['features'] if f['properties'].get('Codigo') == 0), None)
        if zona_0:
            geom_0 = shape(zona_0['geometry'])
            
            print(f"\n   Zona 0:")
            print(f"   • Tipo: {zona_0['geometry']['type']}")
            print(f"   • Válida: {geom_0.is_valid}")
            print(f"   • Área Shapely: {geom_0.area}")
            print(f"   • Contiene punto: {geom_0.contains(point)}")
            
            # Verificar bounds
            minx, miny, maxx, maxy = geom_0.bounds
            print(f"\n   Bounds de zona 0:")
            print(f"   • Min Lon: {minx:.6f}, Max Lon: {maxx:.6f}")
            print(f"   • Min Lat: {miny:.6f}, Max Lat: {maxy:.6f}")
            
            # Verificar si el punto está dentro de los bounds
            en_bounds = minx <= lon <= maxx and miny <= lat <= maxy
            print(f"\n   Punto dentro de bounds: {en_bounds}")
            
            if en_bounds and not geom_0.contains(point):
                print("\n   ⚠️  El punto está dentro de los bounds pero NO dentro del polígono")
                print("   Esto significa que el punto cae en un hueco interior de la zona 0")
                
                # Verificar distancia al polígono
                distance = geom_0.distance(point)
                print(f"   Distancia al polígono más cercano: {distance:.6f}°")
                print(f"   Distancia aproximada: {distance * 111:.2f} km")
else:
    print("\n❌ El punto NO está en ninguna zona de flete")

print("\n" + "="*70)
