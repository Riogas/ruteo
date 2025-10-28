import json

with open('app/data/ZONAS_F.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

for feat in data['features']:
    if feat['properties'].get('Codigo') == '0':
        geom_type = feat['geometry']['type']
        num_polys = len(feat['geometry']['coordinates'])
        
        print(f"Zona 0:")
        print(f"  Tipo: {geom_type}")
        print(f"  Número de polígonos: {num_polys}")
        
        if num_polys == 1:
            polygon = feat['geometry']['coordinates'][0]
            exterior_points = len(polygon[0])
            holes = len(polygon) - 1
            
            print(f"  ✅ Solo 1 polígono (basura eliminada)")
            print(f"  Puntos en anillo exterior: {exterior_points}")
            print(f"  Huecos interiores: {holes}")
        break
