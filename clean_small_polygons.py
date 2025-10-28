"""
Limpieza de polígonos pequeños/basura en ZONAS_F.geojson
Elimina polígonos menores a un umbral de área para cada zona.
"""

import json
from shapely.geometry import shape, mapping

def clean_small_polygons(input_file, output_file, min_area_km2=0.1):
    """
    Elimina polígonos muy pequeños (probablemente errores/basura)
    
    Args:
        min_area_km2: Área mínima en km² para conservar un polígono
                     (0.1 km² = 100,000 m² = 10 hectáreas)
    """
    print(f"📖 Leyendo {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Archivo cargado: {len(data['features'])} zonas\n")
    print(f"🧹 Limpiando polígonos menores a {min_area_km2} km²...")
    print("="*70)
    
    total_removed = 0
    
    for feature in data['features']:
        codigo = feature['properties'].get('Codigo', '?')
        geom = feature['geometry']
        
        if geom['type'] != 'MultiPolygon':
            continue
        
        original_count = len(geom['coordinates'])
        
        # Filtrar polígonos
        cleaned_polygons = []
        removed_polygons = []
        
        for i, polygon in enumerate(geom['coordinates']):
            # Crear geometría de este polígono individual
            from shapely.geometry import Polygon, MultiPolygon
            
            # polygon es [[exterior], [hole1], [hole2], ...]
            exterior = polygon[0]
            holes = polygon[1:] if len(polygon) > 1 else []
            
            poly = Polygon(exterior, holes)
            
            # Calcular área (en grados²)
            area_deg2 = abs(poly.area)
            
            # Convertir a km² aproximado (1° ≈ 111 km en el ecuador)
            # En Uruguay (lat ~-35°): 1° lon ≈ 91 km, 1° lat ≈ 111 km
            area_km2 = area_deg2 * 91 * 111
            
            if area_km2 >= min_area_km2:
                cleaned_polygons.append(polygon)
            else:
                removed_polygons.append({
                    'index': i,
                    'area_km2': area_km2,
                    'points': len(exterior)
                })
        
        # Actualizar geometría
        if len(cleaned_polygons) != original_count:
            feature['geometry']['coordinates'] = cleaned_polygons
            removed_count = original_count - len(cleaned_polygons)
            total_removed += removed_count
            
            print(f"\n📦 Zona {codigo}:")
            print(f"   Polígonos originales: {original_count}")
            print(f"   Polígonos conservados: {len(cleaned_polygons)}")
            print(f"   Polígonos eliminados: {removed_count}")
            
            for removed in removed_polygons:
                print(f"      ✗ Polígono {removed['index']+1}: {removed['area_km2']:.6f} km² ({removed['points']} puntos)")
    
    print("\n" + "="*70)
    print(f"💾 Guardando en {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=None)
    
    print(f"\n✅ ¡Completado!")
    print(f"   Total de polígonos pequeños eliminados: {total_removed}")
    
    return total_removed

if __name__ == "__main__":
    print("="*70)
    print("🧹 LIMPIADOR DE POLÍGONOS PEQUEÑOS/BASURA")
    print("="*70)
    print()
    
    # Limpiar ZONAS_F
    removed = clean_small_polygons(
        'app/data/ZONAS_F.geojson',
        'app/data/ZONAS_F_clean.geojson',
        min_area_km2=0.1  # Eliminar polígonos menores a 0.1 km²
    )
    
    print("\n" + "="*70)
    print("✅ PROCESO COMPLETADO")
    print("="*70)
    print(f"\n   Archivo limpio: app/data/ZONAS_F_clean.geojson")
    print(f"   Polígonos basura eliminados: {removed}")
    print()
    print("   Para aplicar los cambios:")
    print("   copy app\\data\\ZONAS_F.geojson app\\data\\ZONAS_F_before_clean.geojson")
    print("   copy app\\data\\ZONAS_F_clean.geojson app\\data\\ZONAS_F.geojson")
    print()
