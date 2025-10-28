"""
Script para corregir la orientación de polígonos en GeoJSON.
Asegura que los anillos exteriores vayan en sentido antihorario
y los anillos interiores en sentido horario (estándar RFC 7946).
"""

import json
from shapely.geometry import shape, mapping
from shapely.ops import orient

def fix_geojson_orientation(input_file, output_file):
    """
    Corrige la orientación de todos los polígonos en un GeoJSON
    """
    print(f"📖 Leyendo {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Archivo cargado: {len(data['features'])} zonas encontradas")
    print(f"\n🔧 Corrigiendo orientaciones...")
    print("-" * 70)
    
    fixed_count = 0
    
    for i, feature in enumerate(data['features']):
        codigo = feature['properties'].get('Codigo', '?')
        
        try:
            # Convertir a shapely geometry
            geom = shape(feature['geometry'])
            
            # Orientar correctamente (exterior antihorario, interior horario)
            # sign=1.0 significa: exterior antihorario (CCW)
            fixed_geom = orient(geom, sign=1.0)
            
            # Volver a convertir a GeoJSON
            feature['geometry'] = mapping(fixed_geom)
            
            fixed_count += 1
            print(f"   ✓ Zona {codigo} corregida")
            
        except Exception as e:
            print(f"   ✗ Error en zona {codigo}: {e}")
    
    print(f"\n💾 Guardando archivo corregido en {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=None)
    
    print(f"\n✅ ¡Completado!")
    print(f"   - Zonas procesadas: {len(data['features'])}")
    print(f"   - Zonas corregidas: {fixed_count}")
    print(f"   - Archivo guardado: {output_file}")
    
    return fixed_count

if __name__ == "__main__":
    print("="*70)
    print("🔧 CORRECTOR DE ORIENTACIÓN DE POLÍGONOS GEOJSON")
    print("="*70)
    print()
    
    # Corregir ZONAS_F
    print("📦 Procesando ZONAS_F.geojson (Zonas de Flete)...")
    print()
    
    fixed_f = fix_geojson_orientation(
        'app/data/ZONAS_F.geojson',
        'app/data/ZONAS_F_fixed.geojson'
    )
    
    print("\n" + "="*70)
    print("📍 Procesando ZONAS_4.geojson (Zonas Globales)...")
    print()
    
    fixed_4 = fix_geojson_orientation(
        'app/data/ZONAS_4.geojson',
        'app/data/ZONAS_4_fixed.geojson'
    )
    
    print("\n" + "="*70)
    print("✅ RESUMEN FINAL")
    print("="*70)
    print(f"   Zonas de Flete corregidas: {fixed_f}")
    print(f"   Zonas Globales corregidas: {fixed_4}")
    print()
    print("⚠️  IMPORTANTE:")
    print("   Los archivos corregidos tienen sufijo '_fixed.geojson'")
    print("   Revisa los archivos y si están bien, reemplaza los originales:")
    print()
    print("   1. Haz backup de los originales")
    print("   2. mv app/data/ZONAS_F_fixed.geojson app/data/ZONAS_F.geojson")
    print("   3. mv app/data/ZONAS_4_fixed.geojson app/data/ZONAS_4.geojson")
    print()
