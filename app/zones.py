"""
Servicio de detección de zonas usando geometría espacial (point-in-polygon).
Carga zonas desde GeoJSON y determina si un punto está dentro de alguna zona.

Soporta dos tipos de zonificación para Montevideo:
- Zonas de Flete (ZONAS_F): Zonas para cálculo de costos de flete
- Zonas Globales (ZONAS_4): Zonas administrativas/geográficas generales
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from shapely.geometry import Point, Polygon, shape, MultiPolygon
from shapely.prepared import prep

logger = logging.getLogger(__name__)

# Variables globales para almacenar las zonas cargadas
_zones_flete: List[Dict[str, Any]] = []
_prepared_polygons_flete: List[Tuple[Dict[str, Any], Any]] = []

_zones_global: List[Dict[str, Any]] = []
_prepared_polygons_global: List[Tuple[Dict[str, Any], Any]] = []

# Variables para zonas legacy (compatibilidad hacia atrás)
_zones_data: List[Dict[str, Any]] = []
_prepared_polygons: List[Tuple[Dict[str, Any], Any]] = []


def _load_zones_from_file(filename: str) -> Tuple[List[Dict[str, Any]], List[Tuple[Dict[str, Any], Any]]]:
    """
    Carga zonas desde un archivo GeoJSON específico.
    
    Args:
        filename: Nombre del archivo GeoJSON (ej: 'ZONAS_F.geojson')
    
    Returns:
        Tupla con (lista_zonas, lista_prepared_polygons)
    """
    zones_file = Path(__file__).parent / "data" / filename
    
    if not zones_file.exists():
        logger.warning(f"Archivo de zonas no encontrado: {zones_file}")
        return [], []
    
    try:
        with open(zones_file, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        zones_list = []
        prepared_list = []
        
        for feature in geojson_data.get('features', []):
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            # Convertir GeoJSON geometry a shapely Polygon/MultiPolygon
            polygon = shape(geometry)
            
            # Preparar el polígono para búsquedas rápidas
            prepared_polygon = prep(polygon)
            
            # Extraer información de la zona
            # ZONAS_4 usa 'Codigo', ZONAS_F puede usar otros campos
            zone_id = properties.get('Codigo') or properties.get('id') or properties.get('OBJECTID')
            zone_name = properties.get('name') or properties.get('nombre') or f"Zona {zone_id}"
            zone_area = properties.get('Shape_Area', 0)
            
            zone_info = {
                'id': str(zone_id),
                'codigo': zone_id,  # Campo específico de Montevideo
                'name': zone_name,
                'area': zone_area,  # Guardamos el área para ordenar
                'properties': properties,
                'geometry': geometry
            }
            
            zones_list.append(zone_info)
            prepared_list.append((zone_info, prepared_polygon))
        
        # CRÍTICO: Ordenar por área (menor a mayor) para que zonas específicas 
        # se verifiquen primero. Esto evita que zonas grandes "capturen" puntos 
        # que pertenecen a zonas más pequeñas y específicas
        prepared_list.sort(key=lambda x: x[0]['area'])
        zones_list.sort(key=lambda x: x['area'])
        
        logger.info(f"✅ Cargadas {len(zones_list)} zonas desde {zones_file.name} (ordenadas por área)")
        return zones_list, prepared_list
        
    except Exception as e:
        logger.error(f"❌ Error al cargar zonas desde {zones_file}: {e}")
        return [], []


def load_zones() -> None:
    """
    Carga todas las zonas desde los archivos GeoJSON al inicio de la aplicación.
    
    Carga dos tipos de zonas para Montevideo:
    1. ZONAS_F.geojson - Zonas de Flete
    2. ZONAS_4.geojson - Zonas Globales/Administrativas
    3. zonas.geojson - Zonas legacy (compatibilidad)
    
    Prepara los polígonos para búsqueda rápida usando shapely.prepared.
    """
    global _zones_flete, _prepared_polygons_flete
    global _zones_global, _prepared_polygons_global
    global _zones_data, _prepared_polygons
    
    logger.info("🗺️  Iniciando carga de zonas de Montevideo...")
    
    # 1. Cargar Zonas de Flete
    _zones_flete, _prepared_polygons_flete = _load_zones_from_file('ZONAS_F.geojson')
    if _zones_flete:
        logger.info(f"   📦 Zonas de Flete: {len(_zones_flete)} zonas cargadas")
        for zone in _zones_flete[:3]:  # Mostrar solo las primeras 3
            logger.info(f"      - Zona Flete: {zone['name']} (Código: {zone['codigo']})")
        if len(_zones_flete) > 3:
            logger.info(f"      ... y {len(_zones_flete) - 3} zonas más")
    
    # 2. Cargar Zonas Globales
    _zones_global, _prepared_polygons_global = _load_zones_from_file('ZONAS_4.geojson')
    if _zones_global:
        logger.info(f"   🌍 Zonas Globales: {len(_zones_global)} zonas cargadas")
        for zone in _zones_global[:3]:  # Mostrar solo las primeras 3
            logger.info(f"      - Zona Global: {zone['name']} (Código: {zone['codigo']})")
        if len(_zones_global) > 3:
            logger.info(f"      ... y {len(_zones_global) - 3} zonas más")
    
    # 3. Cargar zonas legacy para compatibilidad
    _zones_data, _prepared_polygons = _load_zones_from_file('zonas.geojson')
    if _zones_data:
        logger.info(f"   📍 Zonas Legacy: {len(_zones_data)} zonas cargadas")
    
    total_zones = len(_zones_flete) + len(_zones_global) + len(_zones_data)
    logger.info(f"✅ Total de zonas cargadas: {total_zones}")



def find_zone_by_coordinates(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Busca la zona que contiene las coordenadas dadas usando point-in-polygon.
    
    Args:
        lat: Latitud del punto
        lon: Longitud del punto
    
    Returns:
        Información de la zona si se encuentra, None si no está en ninguna zona
    """
    if not _prepared_polygons:
        logger.warning("⚠️  No hay zonas cargadas. Llama a load_zones() primero.")
        return None
    
    # Crear punto shapely (lon, lat - orden importante en shapely)
    point = Point(lon, lat)
    
    # Buscar en qué zona cae el punto
    for zone_info, prepared_polygon in _prepared_polygons:
        try:
            # Usar prepared polygon para búsqueda rápida
            if prepared_polygon.contains(point):
                logger.info(
                    f"✅ Coordenadas ({lat}, {lon}) encontradas en zona: "
                    f"{zone_info['name']} (ID: {zone_info['id']})"
                )
                return zone_info
        except Exception as e:
            logger.error(
                f"❌ Error al verificar punto en zona {zone_info['name']}: {e}"
            )
            continue
    
    logger.info(f"ℹ️  Coordenadas ({lat}, {lon}) no están en ninguna zona registrada")
    return None


def find_zones_by_coordinates(lat: float, lon: float) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Busca AMBAS zonas (flete y global) que contienen las coordenadas dadas.
    
    Permite conocer tanto la zona de flete como la zona global/administrativa
    para un punto en Montevideo.
    
    Args:
        lat: Latitud del punto
        lon: Longitud del punto
    
    Returns:
        Diccionario con {
            'flete': {...} or None,
            'global': {...} or None
        }
    """
    result = {
        'flete': None,
        'global': None
    }
    
    # Crear punto shapely (lon, lat - orden importante en shapely)
    point = Point(lon, lat)
    
    # 1. Buscar en zonas de flete
    # Las zonas están ordenadas por área (menor a mayor), así que
    # la primera zona que contenga el punto será la más específica
    for zone_info, prepared_polygon in _prepared_polygons_flete:
        try:
            if prepared_polygon.contains(point):
                logger.info(
                    f"✅ Coordenadas ({lat}, {lon}) en Zona Flete: "
                    f"{zone_info['name']} (Código: {zone_info['codigo']}, Área: {zone_info['area']:,.0f} m²)"
                )
                result['flete'] = zone_info
                break  # Tomamos la primera (más pequeña) que contiene el punto
        except Exception as e:
            logger.error(f"❌ Error al verificar punto en zona flete {zone_info['name']}: {e}")
            continue
    
    # 2. Buscar en zonas globales
    # Mismo principio: la primera zona (más pequeña) que contiene el punto
    for zone_info, prepared_polygon in _prepared_polygons_global:
        try:
            if prepared_polygon.contains(point):
                logger.info(
                    f"✅ Coordenadas ({lat}, {lon}) en Zona Global: "
                    f"{zone_info['name']} (Código: {zone_info['codigo']}, Área: {zone_info['area']:,.0f} m²)"
                )
                result['global'] = zone_info
                break  # Tomamos la primera (más pequeña) que contiene el punto
        except Exception as e:
            logger.error(f"❌ Error al verificar punto en zona global {zone_info['name']}: {e}")
            continue
    
    if not result['flete'] and not result['global']:
        logger.info(f"ℹ️  Coordenadas ({lat}, {lon}) no están en ninguna zona de Montevideo")
    
    return result


def get_all_zones() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de todas las zonas cargadas (legacy).
    
    Returns:
        Lista de información de todas las zonas legacy
    """
    return _zones_data.copy()


def get_flete_zones() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de todas las zonas de flete.
    
    Returns:
        Lista de información de todas las zonas de flete
    """
    return _zones_flete.copy()


def get_global_zones() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de todas las zonas globales.
    
    Returns:
        Lista de información de todas las zonas globales
    """
    return _zones_global.copy()


def get_zone_by_id(zone_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene información de una zona específica por su ID.
    
    Args:
        zone_id: ID de la zona
    
    Returns:
        Información de la zona si se encuentra, None si no existe
    """
    for zone in _zones_data:
        if zone['id'] == zone_id:
            return zone
    return None


def get_zone_by_name(zone_name: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene información de una zona específica por su nombre.
    
    Args:
        zone_name: Nombre de la zona (búsqueda case-insensitive)
    
    Returns:
        Información de la zona si se encuentra, None si no existe
    """
    zone_name_lower = zone_name.lower()
    for zone in _zones_data:
        if zone['name'].lower() == zone_name_lower:
            return zone
    return None
