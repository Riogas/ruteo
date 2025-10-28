"""
Servicio de detección de zonas usando geometría espacial (point-in-polygon).
Carga zonas desde GeoJSON y determina si un punto está dentro de alguna zona.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from shapely.geometry import Point, Polygon, shape
from shapely.prepared import prep

logger = logging.getLogger(__name__)

# Variable global para almacenar las zonas cargadas
_zones_data: List[Dict[str, Any]] = []
_prepared_polygons: List[Tuple[Dict[str, Any], Any]] = []


def load_zones() -> None:
    """
    Carga las zonas desde el archivo GeoJSON al inicio de la aplicación.
    Prepara los polígonos para búsqueda rápida usando shapely.prepared.
    """
    global _zones_data, _prepared_polygons
    
    zones_file = Path(__file__).parent / "data" / "zonas.geojson"
    
    if not zones_file.exists():
        logger.warning(f"Archivo de zonas no encontrado: {zones_file}")
        return
    
    try:
        with open(zones_file, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        _zones_data = []
        _prepared_polygons = []
        
        for feature in geojson_data.get('features', []):
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            # Convertir GeoJSON geometry a shapely Polygon
            polygon = shape(geometry)
            
            # Preparar el polígono para búsquedas rápidas
            prepared_polygon = prep(polygon)
            
            zone_info = {
                'id': properties.get('id'),
                'name': properties.get('name'),
                'properties': properties,
                'geometry': geometry
            }
            
            _zones_data.append(zone_info)
            _prepared_polygons.append((zone_info, prepared_polygon))
        
        logger.info(f"✅ Cargadas {len(_zones_data)} zonas desde {zones_file}")
        for zone in _zones_data:
            logger.info(f"   - Zona: {zone['name']} (ID: {zone['id']})")
    
    except Exception as e:
        logger.error(f"❌ Error al cargar zonas desde {zones_file}: {e}")


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


def get_all_zones() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de todas las zonas cargadas.
    
    Returns:
        Lista de información de todas las zonas
    """
    return _zones_data.copy()


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
