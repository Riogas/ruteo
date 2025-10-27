"""
Prueba simple del reverse geocoding con esquinas geométricas.

Usa coordenadas conocidas de Montevideo para validar que
el reverse geocoding detecta esquinas correctamente.
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
    city: str = ""
    state: str = ""
    country: str = ""
    postal_code: str = ""
    corner_1: Optional[str] = None
    corner_2: Optional[str] = None
    full_address: str = ""
    coordinates: Optional[Coordinates] = None

# Copiar las funciones del test anterior (versión simplificada del servicio)
class GeocodingServiceForTest:
    """Versión simplificada del servicio para testing"""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="ruteo_test/1.0", timeout=10)
        self.last_request_time = 0
        self.min_delay = 1.0
    
    def _respect_rate_limit(self):
        import time
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_delay:
            time.sleep(self.min_delay - time_since_last_request)
        self.last_request_time = time.time()
    
    def _get_nearby_streets_from_overpass(self, lat: float, lon: float, radius: float = 0.001, timeout: int = 10):
        try:
            overpass_url = "https://overpass-api.de/api/interpreter"
            south, north = lat - radius, lat + radius
            west, east = lon - radius, lon + radius
            
            query = f"""[out:json][timeout:{timeout}];(way["highway"]["name"]({south},{west},{north},{east}););out geom;"""
            
            response = requests.post(overpass_url, data={"data": query}, timeout=timeout + 5)
            if response.status_code != 200:
                return []
            
            data = response.json()
            if "remark" in data and "error" in data.get("remark", "").lower():
                return []
            
            streets = {}
            for element in data.get("elements", []):
                if element.get("type") == "way" and element.get("geometry"):
                    street_name = element.get("tags", {}).get("name", "")
                    if not street_name:
                        continue
                    coords = [(node["lon"], node["lat"]) for node in element["geometry"]]
                    if street_name in streets:
                        streets[street_name].extend(coords)
                    else:
                        streets[street_name] = coords
            
            result = []
            for name, coords in streets.items():
                if len(coords) >= 2:
                    result.append({"name": name, "geometry": LineString(coords)})
            
            return result
        except Exception as e:
            logger.warning(f"Error Overpass: {e}")
            return []
    
    def _find_nearest_intersection(self, coordinates: Coordinates, streets: list, prefer_street: Optional[str] = None):
        from itertools import combinations
        from math import sqrt
        
        preferred_intersections = []
        other_intersections = []
        
        for street1, street2 in combinations(streets, 2):
            try:
                geom1 = street1["geometry"]
                geom2 = street2["geometry"]
                intersection = geom1.intersection(geom2)
                
                if intersection.is_empty:
                    continue
                
                points = []
                if isinstance(intersection, Point):
                    points = [intersection]
                elif hasattr(intersection, 'geoms'):
                    points = [p for p in intersection.geoms if isinstance(p, Point)]
                
                for point in points:
                    dist = sqrt((point.y - coordinates.lat) ** 2 + (point.x - coordinates.lon) ** 2)
                    intersection_data = (street1["name"], street2["name"], dist, point)
                    
                    if prefer_street:
                        name1, name2 = street1["name"].lower(), street2["name"].lower()
                        prefer = prefer_street.lower()
                        is_preferred = (prefer in name1 or name1 in prefer or prefer in name2 or name2 in prefer)
                        
                        if is_preferred:
                            preferred_intersections.append(intersection_data)
                        else:
                            other_intersections.append(intersection_data)
                    else:
                        other_intersections.append(intersection_data)
            except:
                continue
        
        if preferred_intersections:
            best = min(preferred_intersections, key=lambda x: x[2])
            return (best[0], best[1], best[2])
        elif other_intersections:
            best = min(other_intersections, key=lambda x: x[2])
            return (best[0], best[1], best[2])
        return None
    
    def reverse_geocode(self, coordinates: Coordinates) -> Optional[Address]:
        try:
            self._respect_rate_limit()
            location = self.geocoder.reverse(f"{coordinates.lat}, {coordinates.lon}", exactly_one=True)
            
            if not location or not location.raw:
                return None
            
            raw = location.raw
            address_data = raw.get('address', {})
            street = address_data.get('road', '')
            house_number = address_data.get('house_number', '')
            
            street_with_number = f"{street} {house_number}" if (house_number and street) else street
            
            corner_1, corner_2 = None, None
            
            try:
                nearby_streets = self._get_nearby_streets_from_overpass(coordinates.lat, coordinates.lon, radius=0.001, timeout=8)
                
                if nearby_streets and len(nearby_streets) >= 2:
                    intersection = self._find_nearest_intersection(coordinates, nearby_streets, prefer_street=street)
                    if intersection:
                        corner_1, corner_2, distance = intersection
                        logger.info(f"✅ Esquinas: {corner_1} y {corner_2} (dist: {distance:.6f})")
            except Exception as e:
                logger.debug(f"Error geométrico: {e}")
            
            return Address(
                street=street_with_number,
                city=address_data.get('city') or address_data.get('town', ''),
                state=address_data.get('state', ''),
                country=address_data.get('country', ''),
                postal_code=address_data.get('postcode', ''),
                corner_1=corner_1,
                corner_2=corner_2,
                full_address=location.address,
                coordinates=coordinates
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 PRUEBA SIMPLE: Reverse Geocoding con Esquinas Geométricas")
    print("="*80 + "\n")
    
    service = GeocodingServiceForTest()
    
    # Coordenadas de la Plaza Independencia (esquina conocida)
    test_point = Coordinates(lat=-34.906067, lon=-56.193614)  # 18 de Julio y Río Negro
    
    print(f"📍 Coordenadas: ({test_point.lat:.6f}, {test_point.lon:.6f})")
    print(f"🔍 Haciendo reverse geocoding...\n")
    
    address = service.reverse_geocode(test_point)
    
    if address:
        print(f"✅ RESULTADO:")
        print(f"   Dirección completa: {address.full_address}")
        print(f"   Calle principal: {address.street}")
        print(f"   Esquina 1: {address.corner_1}")
        print(f"   Esquina 2: {address.corner_2}")
        print(f"   Ciudad: {address.city}, {address.country}")
        
        if address.corner_1 and address.corner_2:
            print(f"\n🎉 ÉXITO: Se detectaron las esquinas correctamente!")
        else:
            print(f"\n⚠️  Advertencia: No se detectaron ambas esquinas")
    else:
        print(f"❌ ERROR: No se pudo hacer reverse geocoding")
    
    print("\n" + "="*80 + "\n")
