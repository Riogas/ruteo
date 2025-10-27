"""
Debug: Ver qué calles está encontrando Overpass cerca del punto.
"""

import requests
from shapely.geometry import LineString, Point

lat = -34.90297260536874
lon = -56.17886058917217
radius = 0.001

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

print(f"\n🔍 Buscando calles cerca de ({lat:.6f}, {lon:.6f})")
print(f"   Radio: {radius} (~100 metros)")
print(f"   Bbox: {south:.6f}, {west:.6f}, {north:.6f}, {east:.6f}\n")

response = requests.post(overpass_url, data={"data": query}, timeout=15)
data = response.json()

streets = {}
for element in data.get("elements", []):
    if element.get("type") == "way" and element.get("geometry"):
        street_name = element.get("tags", {}).get("name", "")
        if not street_name:
            continue
        
        coords = [(node["lon"], node["lat"]) for node in element["geometry"]]
        
        if street_name in streets:
            streets[street_name]["count"] += 1
            streets[street_name]["total_coords"] += len(coords)
        else:
            streets[street_name] = {
                "count": 1,
                "total_coords": len(coords)
            }

print(f"📊 CALLES ENCONTRADAS ({len(streets)} únicas):")
print("="*60)
for name, info in sorted(streets.items()):
    print(f"  • {name}")
    print(f"      Segmentos (ways): {info['count']}")
    print(f"      Total coordenadas: {info['total_coords']}")
    print()
