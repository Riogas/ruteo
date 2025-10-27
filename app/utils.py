"""
Utilidades para conversión de coordenadas y funciones auxiliares.
"""

from typing import Tuple
from pyproj import Transformer, CRS
from loguru import logger


def lat_lon_to_utm(lat: float, lon: float) -> Tuple[float, float, str]:
    """
    Convierte coordenadas geográficas (latitud, longitud) a UTM (X, Y).
    
    Args:
        lat: Latitud en grados decimales
        lon: Longitud en grados decimales
        
    Returns:
        Tupla (utm_x, utm_y, zone) donde:
        - utm_x: Coordenada Este (m)
        - utm_y: Coordenada Norte (m)
        - zone: Zona UTM (ej: "21S" para Uruguay)
        
    Example:
        >>> utm_x, utm_y, zone = lat_lon_to_utm(-34.9033, -56.1882)
        >>> print(f"UTM: {utm_x:.2f}, {utm_y:.2f} - Zona: {zone}")
        UTM: 427633.84, 6138077.45 - Zona: 21S
    """
    try:
        # Calcular zona UTM automáticamente
        # Zona UTM = floor((lon + 180) / 6) + 1
        zone_number = int((lon + 180) / 6) + 1
        
        # Determinar hemisferio (N o S)
        hemisphere = 'north' if lat >= 0 else 'south'
        hemisphere_letter = 'N' if lat >= 0 else 'S'
        
        # Crear sistema de coordenadas UTM
        utm_crs = CRS(proj='utm', zone=zone_number, ellps='WGS84', south=(hemisphere == 'south'))
        wgs84_crs = CRS('EPSG:4326')  # WGS84 (lat/lon)
        
        # Crear transformador
        transformer = Transformer.from_crs(wgs84_crs, utm_crs, always_xy=True)
        
        # Convertir (lon, lat) -> (utm_x, utm_y)
        utm_x, utm_y = transformer.transform(lon, lat)
        
        # Formato de zona: "21S" para Uruguay
        zone_str = f"{zone_number}{hemisphere_letter}"
        
        logger.debug(f"Conversión UTM: ({lat}, {lon}) -> ({utm_x:.2f}, {utm_y:.2f}) Zona {zone_str}")
        
        return utm_x, utm_y, zone_str
        
    except Exception as e:
        logger.error(f"Error en conversión lat/lon a UTM: {e}")
        raise


def utm_to_lat_lon(utm_x: float, utm_y: float, zone_number: int, hemisphere: str = 'south') -> Tuple[float, float]:
    """
    Convierte coordenadas UTM (X, Y) a geográficas (latitud, longitud).
    
    Args:
        utm_x: Coordenada Este (m)
        utm_y: Coordenada Norte (m)
        zone_number: Número de zona UTM (ej: 21 para Uruguay)
        hemisphere: 'north' o 'south' (default: 'south' para Uruguay)
        
    Returns:
        Tupla (lat, lon) en grados decimales
        
    Example:
        >>> lat, lon = utm_to_lat_lon(427633.84, 6138077.45, 21, 'south')
        >>> print(f"Lat/Lon: {lat:.6f}, {lon:.6f}")
        Lat/Lon: -34.903300, -56.188200
    """
    try:
        # Crear sistema de coordenadas UTM
        utm_crs = CRS(proj='utm', zone=zone_number, ellps='WGS84', south=(hemisphere == 'south'))
        wgs84_crs = CRS('EPSG:4326')  # WGS84 (lat/lon)
        
        # Crear transformador
        transformer = Transformer.from_crs(utm_crs, wgs84_crs, always_xy=True)
        
        # Convertir (utm_x, utm_y) -> (lon, lat)
        lon, lat = transformer.transform(utm_x, utm_y)
        
        logger.debug(f"Conversión lat/lon: ({utm_x:.2f}, {utm_y:.2f}) -> ({lat}, {lon})")
        
        return lat, lon
        
    except Exception as e:
        logger.error(f"Error en conversión UTM a lat/lon: {e}")
        raise
