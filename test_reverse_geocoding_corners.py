"""
Test de reverse geocoding con detección geométrica de esquinas.

Usa las coordenadas EXACTAS obtenidas en test_verify_intersections.py
para validar que el reverse geocoding devuelve las esquinas correctas.
"""

import sys
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Definir modelos directamente para evitar dependencias
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

# Importar librerías necesarias
from geopy.geocoders import Nominatim
import requests
from shapely.geometry import LineString, Point
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stderr, level="DEBUG")

class GeocodingServiceForTest:
    """Versión simplificada del servicio para testing"""
    
    def __init__(self):
        self.geocoder = Nominatim(
            user_agent="ruteo_test/1.0",
            timeout=10
        )
        self.last_request_time = 0
        self.min_delay = 1.0
    
    def _respect_rate_limit(self):
        import time
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_delay:
            time.sleep(self.min_delay - time_since_last_request)
        self.last_request_time = time.time()
    
    def _get_nearby_streets_from_overpass(self, lat: float, lon: float, radius: float = 0.0005, timeout: int = 10):
        """Obtiene todas las calles cercanas a un punto usando Overpass API."""
        try:
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            # Crear bounding box alrededor del punto
            south = lat - radius
            north = lat + radius
            west = lon - radius
            east = lon + radius
            
            query = f"""
            [out:json][timeout:{timeout}];
            (
              way["highway"]["name"]({south},{west},{north},{east});
            );
            out geom;
            """
            
            logger.debug(f"   🔍 Buscando calles cerca de ({lat:.6f}, {lon:.6f}) en radio {radius}")
            
            response = requests.post(
                overpass_url,
                data={"data": query},
                timeout=timeout + 5
            )
            
            if response.status_code != 200:
                logger.warning(f"   ⚠️  Overpass retornó código {response.status_code}")
                return []
            
            data = response.json()
            
            if "remark" in data and "error" in data.get("remark", "").lower():
                logger.warning(f"   ⚠️  Overpass error: {data.get('remark')}")
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
                    result.append({
                        "name": name,
                        "geometry": LineString(coords)
                    })
            
            logger.debug(f"   📍 Encontradas {len(result)} calles cerca del punto")
            return result
            
        except Exception as e:
            logger.warning(f"   ⚠️  Error obteniendo calles cercanas de Overpass: {e}")
            return []
    
    def _find_nearest_intersection(self, coordinates: Coordinates, streets: list, prefer_street: Optional[str] = None):
        """Encuentra la intersección más cercana al punto dado."""
        from itertools import combinations
        from math import sqrt
        
        best_intersection = None
        min_distance = float('inf')
        
        # Si hay una calle preferida, buscar intersecciones que la incluyan primero
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
                    dist = sqrt(
                        (point.y - coordinates.lat) ** 2 +
                        (point.x - coordinates.lon) ** 2
                    )
                    
                    intersection_data = (street1["name"], street2["name"], dist, point)
                    
                    # Clasificar según si incluye la calle preferida
                    if prefer_street:
                        name1_normalized = street1["name"].lower()
                        name2_normalized = street2["name"].lower()
                        prefer_normalized = prefer_street.lower()
                        
                        is_preferred = (
                            prefer_normalized in name1_normalized or 
                            name1_normalized in prefer_normalized or
                            prefer_normalized in name2_normalized or 
                            name2_normalized in prefer_normalized
                        )
                        
                        if is_preferred:
                            preferred_intersections.append(intersection_data)
                        else:
                            other_intersections.append(intersection_data)
                    else:
                        other_intersections.append(intersection_data)
                        
            except Exception as e:
                logger.debug(f"   ⚠️  Error calculando intersección: {e}")
                continue
        
        # Buscar la mejor intersección
        if preferred_intersections:
            best = min(preferred_intersections, key=lambda x: x[2])
            best_intersection = (best[0], best[1], best[2])
            logger.debug(f"   ✅ Intersección PREFERIDA más cercana: {best[0]} y {best[1]} (dist: {best[2]:.6f})")
        elif other_intersections:
            best = min(other_intersections, key=lambda x: x[2])
            best_intersection = (best[0], best[1], best[2])
            logger.debug(f"   ✅ Intersección más cercana: {best[0]} y {best[1]} (dist: {best[2]:.6f})")
        
        return best_intersection
    
    def reverse_geocode(self, coordinates: Coordinates) -> Optional[Address]:
        """Reverse geocoding con detección geométrica de esquinas."""
        try:
            logger.debug(f"🔄 Reverse geocoding: ({coordinates.lat}, {coordinates.lon})")
            
            self._respect_rate_limit()
            
            # Paso 1: Obtener dirección principal
            location = self.geocoder.reverse(
                f"{coordinates.lat}, {coordinates.lon}",
                exactly_one=True
            )
            
            if not location or not location.raw:
                logger.warning(f"✗ No se encontró dirección")
                return None
            
            raw = location.raw
            address_data = raw.get('address', {})
            
            street = address_data.get('road', '')
            house_number = address_data.get('house_number', '')
            
            if house_number and street:
                street_with_number = f"{street} {house_number}"
            else:
                street_with_number = street
            
            # Paso 2: Buscar esquinas GEOMÉTRICAS
            corner_1 = None
            corner_2 = None
            
            try:
                logger.debug(f"   🌐 Consultando Overpass para esquinas geométricas...")
                nearby_streets = self._get_nearby_streets_from_overpass(
                    coordinates.lat,
                    coordinates.lon,
                    radius=0.001,  # ~100 metros
                    timeout=8
                )
                
                if nearby_streets and len(nearby_streets) >= 2:
                    intersection = self._find_nearest_intersection(
                        coordinates, 
                        nearby_streets,
                        prefer_street=street  # Preferir la calle principal
                    )
                    
                    if intersection:
                        corner_1, corner_2, distance = intersection
                        logger.info(f"   📍 Esquinas GEOMÉTRICAS: {corner_1} y {corner_2} (dist: {distance:.6f})")
                    else:
                        logger.debug(f"   ⚠️  No se encontraron intersecciones geométricas")
                else:
                    logger.debug(f"   ⚠️  Pocas calles encontradas ({len(nearby_streets)})")
                
            except Exception as e:
                logger.debug(f"   ⚠️  Error en detección geométrica: {e}")
            
            # Paso 3: FALLBACK Nominatim
            if not corner_1 or not corner_2:
                try:
                    logger.debug(f"   🔄 Fallback: Buscando esquinas con Nominatim...")
                    nearby_streets = set()
                    
                    self._respect_rate_limit()
                    nearby_results = self.geocoder.reverse(
                        f"{coordinates.lat}, {coordinates.lon}",
                        exactly_one=False,
                        addressdetails=True
                    )
                    
                    if nearby_results and len(nearby_results) > 1:
                        for result in nearby_results[:5]:
                            if result.raw and 'address' in result.raw:
                                nearby_road = result.raw['address'].get('road', '')
                                if nearby_road and nearby_road != street:
                                    nearby_streets.add(nearby_road)
                                    if len(nearby_streets) >= 2:
                                        break
                    
                    if nearby_streets:
                        nearby_list = list(nearby_streets)
                        corner_1 = nearby_list[0] if len(nearby_list) > 0 else None
                        corner_2 = nearby_list[1] if len(nearby_list) > 1 else None
                        
                        if corner_1 or corner_2:
                            logger.info(f"   📍 Esquinas APROXIMADAS (Nominatim): {corner_1} y {corner_2}")
                    
                except Exception as e:
                    logger.debug(f"   ⚠️  Fallback también falló: {e}")
            
            address = Address(
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
            
            esquinas_info = ""
            if corner_1 and corner_2:
                esquinas_info = f" (entre {corner_1} y {corner_2})"
            elif corner_1:
                esquinas_info = f" (esquina {corner_1})"
            
            logger.info(f"✓ Reverse: {street_with_number}{esquinas_info}")
            
            return address
                
        except Exception as e:
            logger.error(f"❌ Error en reverse geocoding: {e}")
            return None

def test_reverse_corner_detection():
    """
    Test: Reverse geocoding debe detectar esquinas correctamente.
    
    Casos de prueba:
    1. (-34.905111, -56.186918) → Debe detectar "18 de Julio" y "Ejido"
    2. (-34.904269, -56.187903) → Debe detectar "18 de Julio" y "Yí"
    3. (-34.906067, -56.193614) → Debe detectar "18 de Julio" y "Río Negro"
    """
    
    service = GeocodingServiceForTest()
    
    test_cases = [
        {
            "name": "18 de Julio y Ejido",
            "coords": Coordinates(lat=-34.905111, lon=-56.186918),
            "expected_streets": {"18 de Julio", "Ejido"}
        },
        {
            "name": "18 de Julio y Yí",
            "coords": Coordinates(lat=-34.904269, lon=-56.187903),
            "expected_streets": {"18 de Julio", "Yí"}
        },
        {
            "name": "18 de Julio y Río Negro",
            "coords": Coordinates(lat=-34.906067, lon=-56.193614),
            "expected_streets": {"18 de Julio", "Río Negro"}
        }
    ]
    
    print("\n" + "="*80)
    print("🧪 TEST: Reverse Geocoding con Detección Geométrica de Esquinas")
    print("="*80 + "\n")
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}️⃣  TEST: {test['name']}")
        print(f"   Coordenadas: ({test['coords'].lat:.6f}, {test['coords'].lon:.6f})")
        
        # Reverse geocoding
        address = service.reverse_geocode(test['coords'])
        
        if not address:
            print(f"   ❌ ERROR: No se pudo hacer reverse geocoding")
            results.append(False)
            continue
        
        print(f"   📍 Dirección completa: {address.full_address}")
        print(f"   🛣️  Calle principal: {address.street}")
        
        # Verificar esquinas
        found_corners = set()
        if address.corner_1:
            found_corners.add(address.corner_1)
        if address.corner_2:
            found_corners.add(address.corner_2)
        
        print(f"   🔀 Esquinas detectadas: {address.corner_1} y {address.corner_2}")
        
        # Validar que las esquinas coincidan (puede ser en cualquier orden)
        if found_corners == test['expected_streets']:
            print(f"   ✅ CORRECTO: Esquinas coinciden exactamente")
            results.append(True)
        else:
            # Permitir nombres parciales (ej: "Avenida 18 de Julio" vs "18 de Julio")
            partial_match = all(
                any(expected in found or found in expected for found in found_corners)
                for expected in test['expected_streets']
            ) if found_corners and test['expected_streets'] else False
            
            if partial_match:
                print(f"   ⚠️  PARCIAL: Nombres similares pero no exactos")
                print(f"      Esperado: {test['expected_streets']}")
                print(f"      Obtenido: {found_corners}")
                results.append(True)
            else:
                print(f"   ❌ ERROR: Esquinas no coinciden")
                print(f"      Esperado: {test['expected_streets']}")
                print(f"      Obtenido: {found_corners}")
                results.append(False)
        
        print()
    
    # Resumen
    print("="*80)
    print("📊 RESUMEN")
    print("="*80)
    print(f"Total tests: {len(results)}")
    print(f"✅ Exitosos: {sum(results)}")
    print(f"❌ Fallidos: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 TODOS LOS TESTS PASARON!")
    else:
        print(f"\n⚠️  {len(results) - sum(results)} test(s) fallaron")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    test_reverse_corner_detection()
