"""
Script para debugging: Analizar por qué el diccionario permite duplicados
"""
import requests
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from math import sqrt

# Coordenadas de prueba
lat = -34.90297260536874
lon = -56.17886058917217

# Obtener calles de Overpass
radius = 0.0009
bbox = f"{lat - radius},{lon - radius},{lat + radius},{lon + radius}"

query = f"""
[out:json];
(
  way["highway"]["name"]({bbox});
);
out geom;
"""

url = "https://overpass-api.de/api/interpreter"
response = requests.post(url, data={"data": query}, timeout=30)
data = response.json()

# Agrupar por nombre y combinar con unary_union
streets_segments = {}
for element in data.get("elements", []):
    street_name = element.get("tags", {}).get("name", "")
    if not street_name:
        continue
    
    coords = [(node["lon"], node["lat"]) for node in element.get("geometry", [])]
    
    if len(coords) >= 2:
        line = LineString(coords)
        if street_name in streets_segments:
            streets_segments[street_name].append(line)
        else:
            streets_segments[street_name] = [line]

# Combinar segmentos
streets = []
for name, segments in streets_segments.items():
    if len(segments) == 1:
        geometry = segments[0]
    else:
        geometry = unary_union(segments)
    streets.append({"name": name, "geometry": geometry})

print(f"📊 Calles encontradas: {len(streets)}")
for st in streets:
    print(f"   • {st['name']}: {type(st['geometry']).__name__}")

# Encontrar calle principal (18 de Julio)
main_street_geom = None
prefer_normalized = "18 de julio"

for street in streets:
    name_normalized = street["name"].lower()
    if prefer_normalized in name_normalized or name_normalized in prefer_normalized:
        main_street_geom = street["geometry"]
        print(f"\n✅ Calle principal: {street['name']}")
        break

if not main_street_geom:
    print("❌ No se encontró la calle principal")
    exit(1)

# Buscar intersecciones con diccionario
print(f"\n{'='*60}")
print("ANÁLISIS DE INTERSECCIONES CON DICCIONARIO")
print(f"{'='*60}\n")

cross_streets_dict = {}

for street in streets:
    street_normalized = street["name"].lower()
    if prefer_normalized in street_normalized or street_normalized in prefer_normalized:
        continue
    
    street_name = street["name"]
    
    try:
        intersection = main_street_geom.intersection(street["geometry"])
        
        if intersection.is_empty:
            continue
        
        # Obtener puntos
        points = []
        if isinstance(intersection, Point):
            points = [intersection]
        elif hasattr(intersection, 'geoms'):
            points = [p for p in intersection.geoms if isinstance(p, Point)]
        
        print(f"🔀 {street_name}:")
        print(f"   Tipo intersección: {type(intersection).__name__}")
        print(f"   Puntos de intersección: {len(points)}")
        
        # Procesar cada punto
        for i, point in enumerate(points):
            dist = sqrt((point.y - lat) ** 2 + (point.x - lon) ** 2)
            
            print(f"      Punto {i+1}: distancia {dist:.6f}")
            
            # ESTE ES EL CORAZÓN DEL PROBLEMA
            if street_name in cross_streets_dict:
                current_dist = cross_streets_dict[street_name]["distance"]
                print(f"         Ya existe '{street_name}' con dist {current_dist:.6f}")
                
                if dist < current_dist:
                    print(f"         ✅ ACTUALIZANDO '{street_name}' (más cercana)")
                    cross_streets_dict[street_name] = {
                        "name": street_name,
                        "distance": dist,
                        "point": point
                    }
                else:
                    print(f"         ⏭️  SALTANDO '{street_name}' (más lejos)")
            else:
                print(f"         ➕ AGREGANDO '{street_name}' (primera vez)")
                cross_streets_dict[street_name] = {
                    "name": street_name,
                    "distance": dist,
                    "point": point
                }
        
        print()
        
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        continue

# Resultado final
print(f"{'='*60}")
print("RESULTADO FINAL DEL DICCIONARIO")
print(f"{'='*60}\n")

print(f"Total de entradas en diccionario: {len(cross_streets_dict)}")
print(f"Nombres únicos: {list(cross_streets_dict.keys())}\n")

cross_streets = list(cross_streets_dict.values())
cross_streets.sort(key=lambda x: x["distance"])

print("Calles ordenadas por distancia:")
for i, cs in enumerate(cross_streets, 1):
    print(f"{i}. {cs['name']}: distancia {cs['distance']:.6f}")

if len(cross_streets) >= 2:
    print(f"\n✅ Esquinas: {cross_streets[0]['name']} y {cross_streets[1]['name']}")
else:
    print(f"\n❌ Solo se encontró {len(cross_streets)} calle(s)")
