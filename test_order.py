import sys
sys.path.insert(0, 'app')

from zones import _load_zones_from_file

# Cargar zonas de flete
zones, prepared = _load_zones_from_file('ZONAS_F.geojson')

print("=== ZONAS DE FLETE (ordenadas por área) ===\n")
for i, zone in enumerate(zones[:5]):
    print(f"{i+1}. Zona {zone['codigo']}: {zone['area']:,.0f} m²")

print(f"\n... y {len(zones) - 5} más\n")
print(f"Última zona: Zona {zones[-1]['codigo']}: {zones[-1]['area']:,.0f} m²")
