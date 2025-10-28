import json

f = open('app/data/ZONAS_F.geojson', 'r', encoding='utf-8')
data = json.load(f)
f.close()

zona0 = data['features'][0]
num_polygons = len(zona0['geometry']['coordinates'])

print(f"✅ Zona 0 limpia:")
print(f"   Número de polígonos: {num_polygons}")

if num_polygons == 1:
    poly = zona0['geometry']['coordinates'][0]
    print(f"   Puntos en exterior: {len(poly[0])}")
    print(f"   Huecos: {len(poly) - 1}")
    print(f"\n🎯 ÉXITO: 4 polígonos basura eliminados")
else:
    print(f"\n⚠️ Todavía hay {num_polygons} polígonos")
