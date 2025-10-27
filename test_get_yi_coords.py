"""
Test para obtener las coordenadas EXACTAS de 18 de Julio y Yí
usando forward geocoding geométrico (no fallback).
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from dataclasses import dataclass
from typing import Optional
from geopy.geocoders import Nominatim
import requests
from shapely.geometry import LineString, Point
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")

@dataclass
class Coordinates:
    lat: float
    lon: float

@dataclass
class Address:
    street: str = ""
    corner_1: Optional[str] = None
    corner_2: Optional[str] = None
    city: str = "Montevideo"
    country: str = "Uruguay"

def get_street_geometry(street_name, timeout=10):
    """Obtener geometría de una calle desde Overpass."""
    overpass_url = "https://overpass-api.de/api/interpreter"
    bbox = "-34.95,-56.25,-34.75,-56.05"  # Montevideo
    
    query = f"""
    [out:json][timeout:{timeout}][bbox:{bbox}];
    way["highway"]["name"="{street_name}"];
    out geom;
    """
    
    response = requests.post(overpass_url, data={"data": query}, timeout=timeout+5)
    data = response.json()
    
    all_coords = []
    for element in data.get("elements", []):
        if element.get("type") == "way" and element.get("geometry"):
            coords = [(node["lon"], node["lat"]) for node in element["geometry"]]
            all_coords.extend(coords)
    
    if len(all_coords) >= 2:
        return LineString(all_coords)
    return None

def calculate_intersection(street1, street2):
    """Calcular intersección geométrica entre dos calles."""
    logger.info(f"📍 Calculando intersección: {street1} y {street2}")
    
    logger.info(f"   Descargando geometría de {street1}...")
    geom1 = get_street_geometry(street1, timeout=15)
    
    if not geom1:
        logger.error(f"   ❌ No se pudo obtener geometría de {street1}")
        return None
    
    logger.info(f"   Descargando geometría de {street2}...")
    geom2 = get_street_geometry(street2, timeout=15)
    
    if not geom2:
        logger.error(f"   ❌ No se pudo obtener geometría de {street2}")
        return None
    
    logger.info(f"   Calculando intersección geométrica...")
    intersection = geom1.intersection(geom2)
    
    if isinstance(intersection, Point):
        coords = Coordinates(lat=intersection.y, lon=intersection.x)
        logger.info(f"   ✅ Intersección encontrada: ({coords.lat:.6f}, {coords.lon:.6f})")
        return coords
    elif hasattr(intersection, 'geoms'):
        first_point = list(intersection.geoms)[0]
        coords = Coordinates(lat=first_point.y, lon=first_point.x)
        logger.info(f"   ✅ Intersección encontrada (primera): ({coords.lat:.6f}, {coords.lon:.6f})")
        return coords
    else:
        logger.error(f"   ❌ No hay intersección geométrica")
        return None

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 FORWARD GEOCODING: 18 de Julio y Yí")
    print("="*80 + "\n")
    
    # Intentar con variaciones del nombre
    variations = [
        ("Avenida 18 de Julio", "Yí"),
        ("18 de Julio", "Yí"),
        ("Avenida 18 de Julio", "Yi"),
        ("18 de Julio", "Yi"),
    ]
    
    for street1, street2 in variations:
        coords = calculate_intersection(street1, street2)
        if coords:
            print(f"\n✅ ÉXITO con: {street1} y {street2}")
            print(f"   Coordenadas: ({coords.lat:.6f}, {coords.lon:.6f})")
            break
        else:
            print(f"\n❌ Falló con: {street1} y {street2}")
    
    print("\n" + "="*80 + "\n")
