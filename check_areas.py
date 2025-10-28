import json

# Cargar ZONAS_F
with open('app/data/ZONAS_F.geojson', 'r', encoding='utf-8') as f:
    zonas_f = json.load(f)

print("=== ZONAS DE FLETE ===")
for feature in zonas_f['features']:
    codigo = feature['properties']['Codigo']
    area = feature['properties'].get('Shape_Area', 0)
    print(f"Zona Flete {codigo}: Área = {area:,.0f} m²")

print("\n" + "="*50)

# Cargar ZONAS_4
with open('app/data/ZONAS_4.geojson', 'r', encoding='utf-8') as f:
    zonas_4 = json.load(f)

print("\n=== ZONAS GLOBALES (primeras 5) ===")
for feature in zonas_4['features'][:5]:
    codigo = feature['properties']['Codigo']
    area = feature['properties'].get('Shape_Area', 0)
    print(f"Zona Global {codigo}: Área = {area:,.0f} m²")
