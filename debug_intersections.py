"""
Debug detallado: Ver cómo se calculan las intersecciones.
"""

import requests
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from math import sqrt

lat = -34.90297260536874
lon = -56.17886058917217
radius = 0.001
coordinates_point = (lat, lon)

overpass_url = "https://overpass-api.de/api/interpreter"
south, north = lat - radius, lat + radius
west, east = lon - radius, lon + radius

query = f"""
[out:json][timeout:10];
(
  way["highway"]["name"]({south},{west},{north},{east});
);
out geom;
"""

print(f"\n🔍 Analizando intersecciones cerca de ({lat:.6f}, {lon:.6f})\n")

response = requests.post(overpass_url, data={"data": query}, timeout=15)
data = response.json()

# Agrupar segmentos por nombre
streets_segments = {}
for element in data.get("elements", []):
    if element.get("type") == "way" and element.get("geometry"):
        street_name = element.get("tags", {}).get("name", "")
        if not street_name:
            continue
        
        coords = [(node["lon"], node["lat"]) for node in element["geometry"]]
        
        if len(coords) >= 2:
            line = LineString(coords)
            if street_name in streets_segments:
                streets_segments[street_name].append(line)
            else:
                streets_segments[street_name] = [line]

# Combinar geometrías
streets = []
for name, segments in streets_segments.items():
    if len(segments) == 1:
        geom = segments[0]
    else:
        geom = unary_union(segments)
    
    streets.append({"name": name, "geometry": geom})

print(f"📊 Calles encontradas: {len(streets)}")
for street in streets:
    print(f"  • {street['name']}: {type(street['geometry']).__name__}")

# Buscar calle principal
main_street = None
main_street_name = None
for street in streets:
    if "18 de julio" in street["name"].lower():
        main_street = street["geometry"]
        main_street_name = street["name"]
        break

print(f"\n🛣️  Calle principal: {main_street_name}")
print(f"   Tipo: {type(main_street).__name__}\n")

# Buscar intersecciones con calles transversales
cross_streets_dict = {}

for street in streets:
    if "18 de julio" in street["name"].lower():
        continue
    
    street_name = street["name"]
    
    try:
        intersection = main_street.intersection(street["geometry"])
        
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
        
        # Calcular distancias
        for i, point in enumerate(points, 1):
            dist = sqrt((point.y - lat) ** 2 + (point.x - lon) ** 2)
            print(f"     Punto {i}: ({point.y:.6f}, {point.x:.6f}) - Distancia: {dist:.6f}")
            
            # Guardar solo la más cercana para esta calle
            if street_name in cross_streets_dict:
                if dist < cross_streets_dict[street_name]["distance"]:
                    cross_streets_dict[street_name] = {"name": street_name, "distance": dist, "point": point}
            else:
                cross_streets_dict[street_name] = {"name": street_name, "distance": dist, "point": point}
        
        print()
    except Exception as e:
        print(f"❌ Error con {street_name}: {e}\n")

# Resultado final
cross_streets = list(cross_streets_dict.values())
cross_streets.sort(key=lambda x: x["distance"])

print(f"\n📍 RESULTADO FINAL (calles transversales únicas):")
print("="*60)
for i, street in enumerate(cross_streets[:3], 1):
    print(f"{i}. {street['name']}: distancia {street['distance']:.6f}")

if len(cross_streets) >= 2:
    print(f"\n✅ Esquinas: {cross_streets[0]['name']} y {cross_streets[1]['name']}")
