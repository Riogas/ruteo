import sys
sys.path.insert(0, 'app')

from zones import load_zones, _prepared_polygons_flete, _zones_flete

# Cargar zonas
print("Cargando zonas...")
load_zones()

print("\n=== ZONAS DE FLETE CARGADAS ===\n")
print(f"Total: {len(_zones_flete)} zonas")
print(f"Total prepared: {len(_prepared_polygons_flete)} zonas\n")

print("Primeras 5 zonas en _zones_flete:")
for i, zone in enumerate(_zones_flete[:5]):
    print(f"  {i+1}. Zona {zone['codigo']}: {zone['area']:,.0f} m²")

print("\nPrimeras 5 zonas en _prepared_polygons_flete:")
for i, (zone_info, poly) in enumerate(_prepared_polygons_flete[:5]):
    print(f"  {i+1}. Zona {zone_info['codigo']}: {zone_info['area']:,.0f} m²")
