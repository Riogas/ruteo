"""
Servicio de Geocodificación.

Convierte direcciones de texto a coordenadas geográficas (lat, lon).

CARACTERÍSTICAS:
- Soporte múltiples proveedores (Nominatim, Google Maps, OpenCage)
- Cache de resultados para evitar llamadas repetidas
- Fallback automático si un proveedor falla
- Rate limiting para respetar límites de API
- Validación y normalización de direcciones

PROVEEDORES:
1. Nominatim (OpenStreetMap) - GRATIS, sin API key, rate limit bajo
2. Google Maps - PAGO, muy preciso, requiere API key
3. OpenCage - FREEMIUM, buen balance, requiere API key

POR QUÉ ES IMPORTANTE:
El sistema necesita coordenadas exactas para calcular rutas reales.
La geocodificación es el primer paso crítico para todo el flujo.
"""

import os
import time
from typing import Optional, Dict, Tuple, List
from functools import lru_cache
import json
import requests

from geopy.geocoders import Nominatim, GoogleV3, OpenCage
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable
from loguru import logger
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

from app.models import Address, Coordinates
from app.utils import lat_lon_to_utm


class GeocodingService:
    """
    Servicio de geocodificación con soporte multi-proveedor.
    
    FLUJO:
    1. Verifica cache local
    2. Intenta geocodificar con proveedor primario
    3. Si falla, intenta con proveedores de respaldo
    4. Guarda resultado en cache
    5. Retorna coordenadas
    """
    
    def __init__(
        self,
        primary_provider: str = "nominatim",
        cache_enabled: bool = True,
        user_agent: str = "ruteo-inteligente-v1"
    ):
        """
        Inicializa el servicio de geocodificación.
        
        Args:
            primary_provider: Proveedor preferido ('nominatim', 'google', 'opencage')
            cache_enabled: Activar cache de resultados
            user_agent: User agent para las solicitudes
        """
        self.primary_provider = primary_provider
        self.cache_enabled = cache_enabled
        self.user_agent = user_agent
        
        # Inicializar geocodificadores
        self.geocoders = self._initialize_geocoders()
        
        # Cache en memoria (en producción usar Redis)
        self._cache: Dict[str, Coordinates] = {}
        
        # Rate limiting (tiempo mínimo entre requests)
        self._last_request_time = 0
        self._min_request_interval = 1.0  # Nominatim requiere 1 segundo entre requests
        
        logger.info(f"GeocodingService inicializado con proveedor primario: {primary_provider}")
    
    def _initialize_geocoders(self) -> Dict[str, any]:
        """
        Inicializa los geocodificadores disponibles.
        
        ORDEN DE PREFERENCIA:
        1. Nominatim - Gratis, pero lento y limitado
        2. Google Maps - Preciso pero requiere API key de pago
        3. OpenCage - Balance entre precisión y costo
        """
        geocoders = {}
        
        # Nominatim (OpenStreetMap) - Servidor personalizado de Uruguay
        try:
            # Usar HTTP explícitamente para evitar problemas de SSL
            geocoders['nominatim'] = Nominatim(
                user_agent=self.user_agent,
                timeout=10,
                domain="nominatim.riogas.uy",
                scheme="http"  # ⭐ Forzar HTTP en lugar de HTTPS
            )
            logger.info(f"✓ Nominatim geocoder inicializado con servidor: http://nominatim.riogas.uy/")
        except Exception as e:
            logger.warning(f"✗ No se pudo inicializar Nominatim: {e}")
        
        # Google Maps - Requiere API key
        google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if google_api_key and google_api_key != 'your_google_maps_key_here':
            try:
                geocoders['google'] = GoogleV3(
                    api_key=google_api_key,
                    timeout=10
                )
                logger.info("✓ Google Maps geocoder inicializado")
            except Exception as e:
                logger.warning(f"✗ No se pudo inicializar Google Maps: {e}")
        
        # OpenCage - Requiere API key
        opencage_api_key = os.getenv('OPENCAGE_API_KEY')
        if opencage_api_key and opencage_api_key != 'your_opencage_key_here':
            try:
                geocoders['opencage'] = OpenCage(
                    api_key=opencage_api_key,
                    timeout=10
                )
                logger.info("✓ OpenCage geocoder inicializado")
            except Exception as e:
                logger.warning(f"✗ No se pudo inicializar OpenCage: {e}")
        
        if not geocoders:
            logger.error("⚠️  ADVERTENCIA: No hay geocodificadores disponibles!")
        
        return geocoders
    
    def _get_cache_key(self, address: str) -> str:
        """Genera una clave de cache normalizada para una dirección"""
        # Normalizar: minúsculas, sin espacios extra, sin puntuación especial
        normalized = address.lower().strip()
        normalized = ' '.join(normalized.split())  # Normalizar espacios
        return normalized
    
    def _check_cache(self, address: str) -> Optional[Coordinates]:
        """Verifica si la dirección está en cache"""
        if not self.cache_enabled:
            return None
        
        cache_key = self._get_cache_key(address)
        return self._cache.get(cache_key)
    
    def _save_to_cache(self, address: str, coordinates: Coordinates):
        """Guarda coordenadas en cache"""
        if not self.cache_enabled:
            return
        
        cache_key = self._get_cache_key(address)
        self._cache[cache_key] = coordinates
        logger.debug(f"Cache guardado para: {address}")
    
    def _respect_rate_limit(self):
        """Respeta el rate limit entre requests"""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        
        if time_since_last_request < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: esperando {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _enrich_with_utm(self, coords: Coordinates) -> Coordinates:
        """
        Enriquece un objeto Coordinates con coordenadas UTM.
        
        Args:
            coords: Coordenadas con lat/lon
            
        Returns:
            Coordenadas enriquecidas con utm_x, utm_y, utm_zone
        """
        try:
            utm_x, utm_y, utm_zone = lat_lon_to_utm(coords.lat, coords.lon)
            coords.utm_x = utm_x
            coords.utm_y = utm_y
            coords.utm_zone = utm_zone
            return coords
        except Exception as e:
            logger.warning(f"No se pudo calcular coordenadas UTM: {e}")
            return coords
    
    def _geocode_with_provider(
        self,
        address: str,
        provider_name: str
    ) -> Optional[Coordinates]:
        """
        Geocodifica usando un proveedor específico.
        
        Args:
            address: Dirección a geocodificar
            provider_name: Nombre del proveedor
            
        Returns:
            Coordenadas o None si falla
        """
        geocoder = self.geocoders.get(provider_name)
        if not geocoder:
            logger.warning(f"Proveedor {provider_name} no disponible")
            return None
        
        try:
            logger.debug(f"Geocodificando con {provider_name}: {address}")
            
            # Respetar rate limit
            self._respect_rate_limit()
            
            # Realizar geocodificación
            location = geocoder.geocode(address)
            
            if location:
                coords = Coordinates(
                    lat=location.latitude,
                    lon=location.longitude
                )
                # Enriquecer con coordenadas UTM
                coords = self._enrich_with_utm(coords)
                logger.info(f"✓ Geocodificado con {provider_name}: {address} -> {coords}")
                return coords
            else:
                logger.warning(f"✗ {provider_name} no encontró resultados para: {address}")
                return None
                
        except GeocoderTimedOut:
            logger.error(f"⏱️  Timeout con {provider_name} para: {address}")
            return None
        except (GeocoderServiceError, GeocoderUnavailable) as e:
            logger.error(f"❌ Error de servicio con {provider_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado con {provider_name}: {e}")
            return None
    
    def _get_street_geometry_from_overpass(self, street_name: str, city: str, country: str, timeout: int = 10) -> Optional[LineString]:
        """
        Obtiene la geometría completa de una calle desde Overpass API.
        
        OPTIMIZACIÓN: Usa bounding box de Montevideo en lugar de búsqueda por área
        para evitar timeouts.
        
        Args:
            street_name: Nombre de la calle
            city: Ciudad
            country: País
            timeout: Timeout en segundos para la consulta
            
        Returns:
            LineString con la geometría de la calle o None si falla
        """
        try:
            # URL de Overpass API
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            # Bounding box de Montevideo (sur, oeste, norte, este)
            # Esto es MUCHO más rápido que buscar por área
            bbox = "-34.95,-56.25,-34.75,-56.05"  # Montevideo aproximado
            
            # Query optimizada con bounding box
            query = f"""
            [out:json][timeout:{timeout}][bbox:{bbox}];
            way["highway"]["name"="{street_name}"];
            out geom;
            """
            
            logger.debug(f"🌐 Overpass: {street_name} en bbox {bbox}")
            
            response = requests.post(overpass_url, data={"data": query}, timeout=timeout + 5)
            
            if response.status_code != 200:
                logger.warning(f"⚠️ Overpass status {response.status_code}")
                return None
            
            data = response.json()
            
            # Verificar si hubo error de runtime
            if 'remark' in data and 'error' in data['remark'].lower():
                logger.warning(f"⚠️ Overpass error: {data['remark']}")
                return None
            
            if not data.get("elements"):
                logger.warning(f"⚠️ Overpass: sin resultados para {street_name}")
                return None
            
            # Extraer coordenadas de todos los ways encontrados
            all_coords = []
            for element in data["elements"]:
                if element.get("type") == "way" and element.get("geometry"):
                    coords = [(node["lon"], node["lat"]) for node in element["geometry"]]
                    all_coords.extend(coords)
            
            if not all_coords:
                logger.warning(f"⚠️ Sin coordenadas en respuesta Overpass")
                return None
            
            # Construir LineString
            line = LineString(all_coords)
            logger.info(f"✓ Geometría: {street_name} ({len(all_coords)} puntos, {len(data['elements'])} ways)")
            
            return line
            
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ Overpass timeout >{timeout}s: {street_name}")
            return None
        except Exception as e:
            logger.error(f"❌ Error Overpass: {e}")
            return None
    
    def _calculate_intersection(self, street1: str, street2: str, city: str, country: str) -> Optional[Coordinates]:
        """
        Calcula la intersección GEOMÉTRICA REAL entre dos calles.
        
        ESTRATEGIA MEJORADA (PRO):
        1. Obtiene geometrías completas (LineStrings) de ambas calles desde Overpass API
        2. Calcula la intersección geométrica real entre las dos líneas
        3. Retorna el punto exacto donde se cruzan
        
        FALLBACK INMEDIATO:
        Si alguna geometría falla o timeout, usa método rápido sin esperar
        
        Args:
            street1: Primera calle
            street2: Segunda calle
            city: Ciudad
            country: País
            
        Returns:
            Coordenadas de la intersección exacta o None si falla
        """
        try:
            logger.info(f"🔍 Intersección GEOMÉTRICA: {street1} ∩ {street2}")
            
            # PASO 1: Obtener geometrías con timeout 8s cada una
            geom1 = self._get_street_geometry_from_overpass(street1, city, country, timeout=8)
            
            # Si la primera falla, hacer fallback inmediato (no esperar la segunda)
            if not geom1:
                logger.warning(f"⚠️ {street1} no disponible en Overpass, fallback inmediato")
                return self._calculate_intersection_fallback(street1, street2, city, country)
            
            geom2 = self._get_street_geometry_from_overpass(street2, city, country, timeout=8)
            
            if not geom2:
                logger.warning(f"⚠️ {street2} no disponible en Overpass, fallback")
                return self._calculate_intersection_fallback(street1, street2, city, country)
            
            # PASO 2: Calcular intersección geométrica
            intersection = geom1.intersection(geom2)
            
            # Verificar que la intersección sea un punto
            if isinstance(intersection, Point):
                coords = Coordinates(lat=intersection.y, lon=intersection.x)
                coords = self._enrich_with_utm(coords)
                logger.info(f"✅ Intersección EXACTA: {coords}")
                return coords
            elif not intersection.is_empty:
                # Si es una colección de puntos, tomar el primero
                if hasattr(intersection, 'geoms'):
                    first_point = list(intersection.geoms)[0]
                    if isinstance(first_point, Point):
                        coords = Coordinates(lat=first_point.y, lon=first_point.x)
                        coords = self._enrich_with_utm(coords)
                        logger.info(f"✅ Intersección EXACTA (múltiple, 1ro): {coords}")
                        return coords
            else:
                logger.warning(f"⚠️ Sin cruce geométrico")
                return self._calculate_intersection_fallback(street1, street2, city, country)
            
        except Exception as e:
            logger.error(f"❌ Error intersección: {e}")
            return self._calculate_intersection_fallback(street1, street2, city, country)
        
        return None
    
    def _calculate_intersection_fallback(self, street1: str, street2: str, city: str, country: str) -> Optional[Coordinates]:
        """
        Método fallback para calcular intersección (punto medio entre cercanos).
        
        Usado cuando Overpass falla o timeout.
        """
        try:
            logger.warning(f"⚠️ Fallback RÁPIDO: {street1} ∩ {street2}")
            
            geocoder = self.geocoders.get(self.primary_provider)
            if not geocoder:
                return None
            
            self._respect_rate_limit()
            loc1 = geocoder.geocode(f"{street1}, {city}, {country}", exactly_one=False, limit=5)
            
            self._respect_rate_limit()
            loc2 = geocoder.geocode(f"{street2}, {city}, {country}", exactly_one=False, limit=5)
            
            if not loc1 or not loc2:
                return None
            
            # Encontrar puntos más cercanos
            min_distance = float('inf')
            best_point = None
            
            for l1 in loc1:
                for l2 in loc2:
                    dist = ((l1.latitude - l2.latitude)**2 + (l1.longitude - l2.longitude)**2)**0.5
                    if dist < min_distance:
                        min_distance = dist
                        best_point = Coordinates(
                            lat=(l1.latitude + l2.latitude) / 2,
                            lon=(l1.longitude + l2.longitude) / 2
                        )
            
            if best_point:
                # Enriquecer con coordenadas UTM
                best_point = self._enrich_with_utm(best_point)
                logger.info(f"✓ Intersección APROXIMADA: {street1} ∩ {street2}")
                return best_point
                
        except Exception as e:
            logger.error(f"❌ Error fallback: {e}")
        
        return None
    
    def geocode(self, address: Address) -> Optional[Coordinates]:
        """
        Geocodifica una dirección estructurada.
        
        ESTRATEGIA MEJORADA:
        1. Calle + Número de puerta → Geocodifica "Calle Número"
        2. Calle + Esquinas (sin número) → Calcula intersección "Calle con Esquina1"
        3. Solo Esquinas → Calcula intersección "Esquina1 con Esquina2"
        
        Args:
            address: Dirección estructurada (puede incluir esquinas)
            
        Returns:
            Coordenadas geocodificadas o None si falla
        """
        # Si ya tiene coordenadas, usarlas
        if address.coordinates:
            logger.debug("Dirección ya tiene coordenadas, usando las existentes")
            return address.coordinates
        
        # CASO 1: Dirección completa proporcionada
        if address.full_address:
            cache_key = address.full_address
            cached = self._check_cache(cache_key)
            if cached:
                return cached
            
            coords = self._geocode_with_provider(address.full_address, self.primary_provider)
            if coords:
                self._save_to_cache(cache_key, coords)
                return coords
        
        # CASO 2: Calle principal + Número de puerta (más específico)
        # Ejemplo: street="18 de Julio" + number="1234" → "18 de Julio 1234"
        if address.street:
            # Construir la dirección completa con el número si existe
            if address.number:
                street_with_number = f"{address.street} {address.number}"
                cache_key = f"{street_with_number}, {address.city}, {address.country}"
                cached = self._check_cache(cache_key)
                if cached:
                    return cached
                
                logger.info(f"🔍 Geocodificando calle con número: {street_with_number}")
                coords = self._geocode_with_provider(cache_key, self.primary_provider)
                if coords:
                    self._save_to_cache(cache_key, coords)
                    return coords
            
            # CASO 3: Calle + Esquina(s) (sin número de puerta)
            # Calcular intersección aproximada
            elif address.corner_1:
                logger.info(f"🔍 Calculando intersección: {address.street} y {address.corner_1}")
                coords = self._calculate_intersection(
                    address.street, 
                    address.corner_1,
                    address.city,
                    address.country
                )
                if coords:
                    return coords
                
                # Fallback: Geocodificar solo la calle principal
                logger.warning(f"⚠️ No se pudo calcular intersección, usando solo calle principal")
                cache_key = f"{address.street}, {address.city}, {address.country}"
                coords = self._geocode_with_provider(cache_key, self.primary_provider)
                if coords:
                    return coords
            
            # CASO 4: Solo calle (sin número ni esquinas)
            else:
                cache_key = f"{address.street}, {address.city}, {address.country}"
                cached = self._check_cache(cache_key)
                if cached:
                    return cached
                
                logger.info(f"🔍 Geocodificando solo calle: {address.street}")
                coords = self._geocode_with_provider(cache_key, self.primary_provider)
                if coords:
                    self._save_to_cache(cache_key, coords)
                    return coords
        
        # CASO 5: Solo esquinas (sin calle principal)
        # Calcular intersección entre las dos esquinas
        elif address.corner_1 and address.corner_2:
            logger.info(f"🔍 Calculando intersección de esquinas: {address.corner_1} y {address.corner_2}")
            coords = self._calculate_intersection(
                address.corner_1,
                address.corner_2,
                address.city,
                address.country
            )
            if coords:
                return coords
        
        # CASO 6: Solo una esquina (sin calle principal ni segunda esquina)
        elif address.corner_1:
            cache_key = f"{address.corner_1}, {address.city}, {address.country}"
            cached = self._check_cache(cache_key)
            if cached:
                return cached
            
            logger.info(f"🔍 Geocodificando esquina única: {address.corner_1}")
            coords = self._geocode_with_provider(cache_key, self.primary_provider)
            if coords:
                self._save_to_cache(cache_key, coords)
                return coords
        
        # Si llegamos aquí, no se pudo geocodificar
        logger.error(f"❌ No se pudo geocodificar la dirección proporcionada")
        return None
    
    def _get_nearby_streets_from_overpass(self, lat: float, lon: float, radius: float = 0.0005, timeout: int = 10):
        """
        Obtiene todas las calles cercanas a un punto usando Overpass API.
        
        Args:
            lat: Latitud del punto
            lon: Longitud del punto
            radius: Radio de búsqueda en grados (~0.0005 = 50 metros)
            timeout: Timeout de la consulta en segundos
            
        Returns:
            Lista de diccionarios con {name: str, geometry: LineString}
        """
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
            
            # Verificar si hay error
            if "remark" in data and "error" in data.get("remark", "").lower():
                logger.warning(f"   ⚠️  Overpass error: {data.get('remark')}")
                return []
            
            # Agrupar segmentos por nombre de calle
            streets_segments = {}  # {name: [LineString1, LineString2, ...]}
            
            for element in data.get("elements", []):
                if element.get("type") == "way" and element.get("geometry"):
                    street_name = element.get("tags", {}).get("name", "")
                    if not street_name:
                        continue
                    
                    coords = [(node["lon"], node["lat"]) for node in element["geometry"]]
                    
                    if len(coords) >= 2:
                        line = LineString(coords)
                        
                        if street_name in streets_segments:
                            streets_segments[street_name].append(line)
                        else:
                            streets_segments[street_name] = [line]
            
            # Combinar segmentos de la misma calle usando unary_union
            result = []
            for name, segments in streets_segments.items():
                if len(segments) == 1:
                    # Solo un segmento, usar directamente
                    result.append({
                        "name": name,
                        "geometry": segments[0]
                    })
                else:
                    # Múltiples segmentos, combinar con unary_union
                    combined = unary_union(segments)
                    result.append({
                        "name": name,
                        "geometry": combined
                    })
            
            logger.debug(f"   📍 Encontradas {len(result)} calles cerca del punto")
            return result
            
        except Exception as e:
            logger.warning(f"   ⚠️  Error obteniendo calles cercanas de Overpass: {e}")
            return []
    
    def _find_nearest_intersection(self, coordinates: Coordinates, streets: list, prefer_street: Optional[str] = None):
        """
        Encuentra la intersección más cercana al punto dado.
        
        NUEVO: Si se proporciona prefer_street (calle principal), busca las DOS calles
        transversales más cercanas que intersectan con ella (una a cada lado).
        
        Args:
            coordinates: Punto de referencia
            streets: Lista de diccionarios {name, geometry}
            prefer_street: Nombre de calle principal (para encontrar transversales)
            
        Returns:
            Tupla (corner_1, corner_2, distance) o None si no hay intersección
        """
        from itertools import combinations
        from math import sqrt
        
        # CASO 1: Si hay calle preferida, buscar calles TRANSVERSALES
        if prefer_street:
            # Encontrar la geometría de la calle principal
            main_street_geom = None
            main_street_name = None
            
            prefer_normalized = prefer_street.lower()
            
            for street in streets:
                name_normalized = street["name"].lower()
                # Verificar si es la calle principal
                if prefer_normalized in name_normalized or name_normalized in prefer_normalized:
                    main_street_geom = street["geometry"]
                    main_street_name = street["name"]
                    break
            
            if main_street_geom:
                # Buscar todas las calles que intersectan con la principal
                # Usar diccionario para agrupar por nombre (evitar duplicados)
                cross_streets_dict = {}
                
                for street in streets:
                    # Saltar si es la misma calle principal
                    street_normalized = street["name"].lower()
                    if prefer_normalized in street_normalized or street_normalized in prefer_normalized:
                        continue
                    
                    street_name = street["name"]
                    
                    try:
                        intersection = main_street_geom.intersection(street["geometry"])
                        
                        if intersection.is_empty:
                            continue
                        
                        # Obtener puntos de intersección
                        points = []
                        if isinstance(intersection, Point):
                            points = [intersection]
                        elif hasattr(intersection, 'geoms'):
                            points = [p for p in intersection.geoms if isinstance(p, Point)]
                        
                        # Para cada calle, guardar SOLO la intersección más cercana
                        for point in points:
                            dist = sqrt(
                                (point.y - coordinates.lat) ** 2 +
                                (point.x - coordinates.lon) ** 2
                            )
                            
                            # Si esta calle ya existe, quedarse con la intersección más cercana
                            if street_name in cross_streets_dict:
                                if dist < cross_streets_dict[street_name]["distance"]:
                                    cross_streets_dict[street_name] = {
                                        "name": street_name,
                                        "distance": dist,
                                        "point": point
                                    }
                            else:
                                cross_streets_dict[street_name] = {
                                    "name": street_name,
                                    "distance": dist,
                                    "point": point
                                }
                    except Exception as e:
                        logger.debug(f"   ⚠️  Error calculando intersección con {street['name']}: {e}")
                        continue
                
                # Convertir diccionario a lista y ordenar por distancia
                cross_streets = list(cross_streets_dict.values())
                cross_streets.sort(key=lambda x: x["distance"])
                
                # Tomar las 2 calles DIFERENTES más cercanas
                if len(cross_streets) >= 2:
                    corner_1 = cross_streets[0]["name"]
                    corner_2 = cross_streets[1]["name"]
                    avg_dist = (cross_streets[0]["distance"] + cross_streets[1]["distance"]) / 2
                    
                    logger.debug(f"   ✅ Esquinas transversales: {corner_1} (dist: {cross_streets[0]['distance']:.6f}) y {corner_2} (dist: {cross_streets[1]['distance']:.6f})")
                    
                    return (corner_1, corner_2, avg_dist)
                elif len(cross_streets) == 1:
                    # Solo hay una calle transversal cercana
                    logger.debug(f"   ⚠️  Solo se encontró una esquina transversal: {cross_streets[0]['name']}")
                    return (cross_streets[0]["name"], None, cross_streets[0]["distance"])
        
        # CASO 2: Sin calle preferida - buscar cualquier intersección cercana
        best_intersection = None
        min_distance = float('inf')
        
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
                    
                    if dist < min_distance:
                        min_distance = dist
                        best_intersection = (street1["name"], street2["name"], dist)
                        
            except Exception as e:
                logger.debug(f"   ⚠️  Error calculando intersección: {e}")
                continue
        
        if best_intersection:
            logger.debug(f"   ✅ Intersección más cercana: {best_intersection[0]} y {best_intersection[1]} (dist: {best_intersection[2]:.6f})")
        
        return best_intersection
    
    def reverse_geocode(self, coordinates: Coordinates) -> Optional[Address]:
        """
        Geocodificación inversa: convierte coordenadas en dirección.
        
        **PROCESO MEJORADO (con Overpass + Shapely):**
        1. Consulta Nominatim con las coordenadas (obtiene dirección principal)
        2. Consulta Overpass para calles cercanas al punto (radio ~50m)
        3. Descarga geometrías completas de esas calles
        4. Calcula intersecciones geométricas entre pares de calles
        5. Encuentra la intersección MÁS CERCANA al punto dado
        6. Retorna Address completo con esquinas geométricamente correctas
        
        **VENTAJAS vs enfoque anterior:**
        - Esquinas REALES (calles que se intersectan geométricamente)
        - Mayor precisión (usa cálculo geométrico, no búsqueda textual)
        - Consistencia con forward geocoding (mismo algoritmo)
        
        **FALLBACK:**
        - Si Overpass falla/timeout, usa enfoque Nominatim simple
        
        Args:
            coordinates: Coordenadas a convertir
            
        Returns:
            Dirección estructurada con esquinas o None si falla
        """
        geocoder = self.geocoders.get(self.primary_provider)
        if not geocoder:
            logger.error("No hay geocodificador disponible para reverse geocoding")
            return None
        
        try:
            logger.debug(f"🔄 Reverse geocoding: ({coordinates.lat}, {coordinates.lon})")
            
            self._respect_rate_limit()
            
            # Paso 1: Obtener dirección principal (Nominatim)
            location = geocoder.reverse(
                f"{coordinates.lat}, {coordinates.lon}",
                exactly_one=True
            )
            
            if not location or not location.raw:
                logger.warning(f"✗ No se encontró dirección para: {coordinates}")
                return None
            
            raw = location.raw
            address_data = raw.get('address', {})
            
            # Extraer calle y número de puerta separados
            street = address_data.get('road', '')
            house_number = address_data.get('house_number', '')
            
            # Construir street_with_number solo para logging/full_address
            if house_number and street:
                street_with_number = f"{street} {house_number}"
            else:
                street_with_number = street
            
            # Paso 2: Buscar esquinas GEOMÉTRICAS usando Overpass + Shapely
            corner_1 = None
            corner_2 = None
            
            try:
                # Obtener calles cercanas de Overpass (radio ~100 metros para mejor cobertura)
                logger.debug(f"   🌐 Consultando Overpass para esquinas geométricas...")
                nearby_streets = self._get_nearby_streets_from_overpass(
                    coordinates.lat,
                    coordinates.lon,
                    radius=0.001,  # ~100 metros (aumentado de 50m)
                    timeout=8
                )
                
                if nearby_streets and len(nearby_streets) >= 2:
                    # Encontrar la intersección más cercana, PREFIRIENDO la calle principal
                    intersection = self._find_nearest_intersection(
                        coordinates, 
                        nearby_streets,
                        prefer_street=street  # Usar la calle principal de Nominatim como preferencia
                    )
                    
                    if intersection:
                        corner_1, corner_2, distance = intersection
                        logger.info(f"   📍 Esquinas GEOMÉTRICAS encontradas: {corner_1} y {corner_2} (dist: {distance:.6f})")
                    else:
                        logger.debug(f"   ⚠️  No se encontraron intersecciones geométricas, usando fallback Nominatim")
                else:
                    logger.debug(f"   ⚠️  Pocas calles encontradas ({len(nearby_streets)}), usando fallback Nominatim")
                
            except Exception as e:
                logger.debug(f"   ⚠️  Error en detección geométrica de esquinas: {e}")
            
            # Paso 3: FALLBACK - Si no se encontraron esquinas geométricas, usar enfoque Nominatim
            if not corner_1 or not corner_2:
                try:
                    logger.debug(f"   🔄 Fallback: Buscando esquinas con Nominatim...")
                    nearby_streets = set()
                    
                    self._respect_rate_limit()
                    nearby_results = geocoder.reverse(
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
                        # SOLO sobrescribir las esquinas que estén vacías
                        if not corner_1:
                            corner_1 = nearby_list[0] if len(nearby_list) > 0 else None
                        if not corner_2:
                            corner_2 = nearby_list[1] if len(nearby_list) > 1 else nearby_list[0] if len(nearby_list) > 0 else None
                        
                        if corner_1 or corner_2:
                            logger.info(f"   📍 Esquinas APROXIMADAS (Nominatim): {corner_1} y {corner_2}")
                    
                except Exception as e:
                    logger.debug(f"   ⚠️  Fallback Nominatim también falló: {e}")
            
            # Construir Address con todos los datos (número separado)
            address = Address(
                street=street,  # Sin número
                number=house_number if house_number else None,  # Número separado
                city=address_data.get('city') or address_data.get('town', ''),
                state=address_data.get('state', ''),
                country=address_data.get('country', ''),
                postal_code=address_data.get('postcode', ''),
                corner_1=corner_1,
                corner_2=corner_2,
                full_address=location.address,
                coordinates=coordinates
            )
            
            # Log mejorado con esquinas
            esquinas_info = ""
            if corner_1 and corner_2:
                esquinas_info = f" (entre {corner_1} y {corner_2})"
            elif corner_1:
                esquinas_info = f" (esquina {corner_1})"
            
            logger.info(f"✓ Reverse geocoding: ({coordinates.lat:.6f}, {coordinates.lon:.6f}) -> {street_with_number}{esquinas_info}")
            
            return address
                
        except Exception as e:
            logger.error(f"❌ Error en reverse geocoding: {e}")
            return None
    
    def batch_geocode(self, addresses: list[Address]) -> Dict[str, Optional[Coordinates]]:
        """
        Geocodifica múltiples direcciones en batch.
        
        OPTIMIZACIONES:
        - Procesa todas las direcciones de una vez
        - Aprovecha cache para evitar requests duplicados
        - Útil para inicializar sistema con direcciones históricas
        
        Args:
            addresses: Lista de direcciones a geocodificar
            
        Returns:
            Diccionario {address_str: Coordinates}
        """
        results = {}
        
        logger.info(f"📦 Batch geocoding de {len(addresses)} direcciones")
        
        for i, address in enumerate(addresses, 1):
            logger.debug(f"Procesando {i}/{len(addresses)}")
            coords = self.geocode(address)
            
            address_str = address.full_address or f"{address.street}, {address.city}"
            results[address_str] = coords
        
        success_count = sum(1 for c in results.values() if c is not None)
        logger.info(f"✓ Batch geocoding completado: {success_count}/{len(addresses)} exitosos")
        
        return results
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas del cache"""
        return {
            "cache_size": len(self._cache),
            "cache_enabled": self.cache_enabled
        }
    
    def get_streets_by_location(self, departamento: str, localidad: Optional[str] = None, timeout: int = 60) -> List[str]:
        """
        Obtiene listado de calles de un departamento/localidad en Uruguay usando Overpass API.
        
        Args:
            departamento: Departamento de Uruguay (ej: Montevideo, Canelones)
            localidad: Localidad específica (opcional)
            timeout: Timeout de la consulta en segundos
            
        Returns:
            Lista de nombres de calles únicas (ordenadas alfabéticamente)
        """
        try:
            # Determinar URL de Overpass (usar servidor personalizado si está disponible)
            overpass_url = os.getenv('OVERPASS_URL', 'https://overpass-api.de/api/interpreter')
            
            logger.info(f"🔍 Buscando calles en {departamento}" + 
                       (f", {localidad}" if localidad else "") + ", Uruguay")
            
            # Paso 1: Primero geocodificar la localidad para obtener bounding box
            if localidad:
                search_query = f"{localidad}, {departamento}, Uruguay"
            else:
                search_query = f"{departamento}, Uruguay"
            
            logger.debug(f"   Geocodificando área: {search_query}")
            
            # Usar nominatim para obtener el bounding box del área
            geocoder = self.geocoders.get(self.primary_provider)
            if not geocoder:
                logger.error("No hay geocodificador disponible")
                return []
            
            self._respect_rate_limit()
            location = geocoder.geocode(search_query, exactly_one=True)
            
            if not location or not location.raw or 'boundingbox' not in location.raw:
                logger.error(f"No se pudo geocodificar el área: {search_query}")
                return []
            
            # Obtener bounding box [south, north, west, east]
            bbox = location.raw['boundingbox']
            south, north, west, east = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
            
            logger.debug(f"   Bounding box: S={south}, N={north}, W={west}, E={east}")
            
            # Query de Overpass usando bounding box
            query = f"""
            [out:json][timeout:{timeout}][bbox:{south},{west},{north},{east}];
            (
              way["highway"]["name"];
            );
            out tags;
            """
            
            logger.debug(f"   Consultando Overpass API...")
            
            response = requests.post(
                overpass_url,
                data=query,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=timeout
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Error en Overpass: HTTP {response.status_code}")
                return []
            
            data = response.json()
            elements = data.get('elements', [])
            
            logger.debug(f"   Overpass retornó {len(elements)} elementos")
            
            # Extraer nombres únicos de calles
            street_names = set()
            for element in elements:
                tags = element.get('tags', {})
                name = tags.get('name', '').strip()
                
                if name:
                    street_names.add(name)
            
            # Convertir a lista ordenada
            streets_list = sorted(list(street_names))
            
            logger.info(f"✅ Encontradas {len(streets_list)} calles únicas en {departamento}" + 
                       (f", {localidad}" if localidad else ""))
            
            return streets_list
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout al consultar Overpass (>{timeout}s)")
            return []
        except Exception as e:
            logger.error(f"❌ Error obteniendo calles: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

@lru_cache(maxsize=1)
def get_geocoding_service() -> GeocodingService:
    """
    Singleton del servicio de geocodificación.
    
    Usa LRU cache para mantener una única instancia del servicio
    durante toda la ejecución de la aplicación.
    """
    return GeocodingService(
        primary_provider=os.getenv('GEOCODING_PROVIDER', 'nominatim'),
        cache_enabled=True
    )


def quick_geocode(address_str: str) -> Optional[Tuple[float, float]]:
    """
    Función de utilidad para geocodificar rápidamente una dirección string.
    
    Args:
        address_str: Dirección como string
        
    Returns:
        Tupla (lat, lon) o None
    """
    service = get_geocoding_service()
    
    address = Address(
        street="",
        city="",
        full_address=address_str
    )
    
    coords = service.geocode(address)
    if coords:
        return (coords.lat, coords.lon)
    return None


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Configurar logging
    logger.add("logs/geocoding.log", rotation="1 day")
    
    # Crear servicio
    service = GeocodingService()
    
    # Ejemplo 1: Geocodificar dirección estructurada
    address = Address(
        street="Av. Corrientes",
        number="1234",
        city="Buenos Aires",
        country="Argentina"
    )
    
    coords = service.geocode(address)
    if coords:
        print(f"✓ Coordenadas: {coords.lat}, {coords.lon}")
    else:
        print("✗ No se pudo geocodificar")
    
    # Ejemplo 2: Reverse geocoding
    if coords:
        reverse_address = service.reverse_geocode(coords)
        if reverse_address:
            print(f"✓ Dirección: {reverse_address.full_address}")
    
    # Ejemplo 3: Batch geocoding
    addresses = [
        Address(street="Av. 9 de Julio", number="1000", city="Buenos Aires", country="Argentina"),
        Address(street="Calle Florida", number="500", city="Buenos Aires", country="Argentina"),
    ]
    
    results = service.batch_geocode(addresses)
    print(f"\n✓ Batch: {len(results)} direcciones procesadas")
    
    # Estadísticas
    stats = service.get_cache_stats()
    print(f"\n📊 Cache: {stats['cache_size']} entradas")
