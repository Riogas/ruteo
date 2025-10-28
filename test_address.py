"""
Probar geocodificación y detección de zona para dirección específica
"""

import requests
import json

# Dirección a probar
address = "21 de setiembre 2570, Montevideo, Uruguay"

# 1. Geocodificar la dirección
print("="*70)
print("🔍 GEOCODIFICACIÓN")
print("="*70)
print(f"Dirección: {address}\n")

geocode_url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
headers = {'User-Agent': 'RuteoApp/1.0'}

response = requests.get(geocode_url, headers=headers)
if response.status_code == 200:
    results = response.json()
    if results:
        result = results[0]
        lat = float(result['lat'])
        lon = float(result['lon'])
        print(f"✅ Coordenadas encontradas:")
        print(f"   Latitud: {lat}")
        print(f"   Longitud: {lon}")
        print(f"   Display Name: {result['display_name']}\n")
        
        # 2. Verificar zona con el endpoint local
        print("="*70)
        print("🗺️  DETECCIÓN DE ZONA")
        print("="*70)
        
        zones_url = f"http://localhost:8000/zones?lat={lat}&lon={lon}"
        zones_response = requests.get(zones_url)
        
        if zones_response.status_code == 200:
            zones_data = zones_response.json()
            print(f"\n📍 Zona detectada:")
            print(json.dumps(zones_data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error al consultar zonas: {zones_response.status_code}")
            print(zones_response.text)
            
        # 3. Verificar manualmente con shapely
        print("\n" + "="*70)
        print("🔬 VERIFICACIÓN MANUAL CON SHAPELY")
        print("="*70)
        
        from shapely.geometry import Point, shape
        
        point = Point(lon, lat)
        print(f"\nPunto: {point}")
        
        # Cargar ZONAS_F
        with open('app/data/ZONAS_F.geojson', 'r', encoding='utf-8') as f:
            zonas_f = json.load(f)
        
        print(f"\nVerificando en {len(zonas_f['features'])} zonas de flete:")
        
        # Ordenar por área (como en el código real)
        features_sorted = sorted(
            zonas_f['features'],
            key=lambda f: f['properties'].get('Shape_Area', 0)
        )
        
        for i, feature in enumerate(features_sorted):
            codigo = feature['properties'].get('Codigo')
            area = feature['properties'].get('Shape_Area', 0)
            geom = shape(feature['geometry'])
            
            contains = geom.contains(point)
            
            status = "✅ CONTIENE" if contains else "❌"
            print(f"{i+1}. Zona {codigo} (Área: {area:,.0f} m²) {status}")
            
            if contains:
                print(f"\n🎯 PRIMERA ZONA QUE CONTIENE EL PUNTO: Zona {codigo}")
                break
        
    else:
        print("❌ No se encontraron resultados para la dirección")
else:
    print(f"❌ Error en geocodificación: {response.status_code}")
