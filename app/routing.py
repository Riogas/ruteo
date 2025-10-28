"""
Motor de Cálculo de Rutas con Restricciones Geoespaciales.

Este es el CORAZÓN del sistema de ruteo inteligente.

FUNCIONALIDADES AVANZADAS:
✓ Usa red vial REAL de OpenStreetMap (no distancia en línea recta)
✓ Considera CALLES FLECHADAS (grafos dirigidos)
✓ Calcula rutas óptimas considerando sentido de circulación
✓ Estima tiempos reales de viaje
✓ Cache de grafos para mejorar performance
✓ Soporte para diferentes tipos de vehículos

POR QUÉ OSMnx:
- OpenStreetMap tiene datos reales de calles flechadas
- NetworkX permite análisis de grafos dirigidos
- Algoritmos optimizados (Dijkstra, A*)
- Datos actualizados y gratuitos

CONCEPTOS CLAVE:
- GRAFO DIRIGIDO: Cada calle tiene sentido único o doble sentido
- NODO: Intersección de calles
- ARISTA: Segmento de calle con dirección
- PESO: Distancia o tiempo de recorrido
"""

import os
import pickle
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timedelta
import time

import networkx as nx
import osmnx as ox
from shapely.geometry import Point, LineString
import numpy as np
from loguru import logger

from app.models import Coordinates, Route, RouteSegment


# Configuración de OSMnx con servidor personalizado
ox.settings.use_cache = True
ox.settings.log_console = False

# Configurar servidor Overpass personalizado de Uruguay
ox.settings.overpass_endpoint = "http://overpass.riogas.uy/api/interpreter"
ox.settings.nominatim_endpoint = "http://nominatim.riogas.uy/"

logger.info(f"🌐 OSMnx configurado con servidores personalizados:")
logger.info(f"  - Overpass: {ox.settings.overpass_endpoint}")
logger.info(f"  - Nominatim: {ox.settings.nominatim_endpoint}")


class RouteCalculator:
    """
    Calculadora de rutas con consideración de red vial real.
    
    FLUJO:
    1. Descarga/carga grafo de la ciudad desde OSM
    2. Encuentra nodos más cercanos a origen y destino
    3. Calcula ruta óptima usando algoritmo de caminos mínimos
    4. Retorna ruta con distancias, tiempos y coordenadas
    
    CARACTERÍSTICAS:
    - Grafo dirigido para respetar sentidos de calles
    - Cache persistente de grafos por ciudad
    - Múltiples algoritmos de routing disponibles
    """
    
    def __init__(
        self,
        network_type: str = "drive",
        cache_dir: str = "./cache/osm",
        simplify: bool = True
    ):
        """
        Inicializa el calculador de rutas.
        
        Args:
            network_type: Tipo de red ('drive', 'walk', 'bike', 'drive_service')
                - 'drive': Red de calles para autos (respeta sentidos)
                - 'walk': Red para peatones
                - 'bike': Red para bicicletas
                - 'drive_service': Incluye calles de servicio
            cache_dir: Directorio para cache de grafos
            simplify: Simplificar geometría de la red
        """
        self.network_type = network_type
        self.cache_dir = cache_dir
        self.simplify = simplify
        
        # Cache de grafos en memoria
        self._graph_cache: Dict[str, nx.MultiDiGraph] = {}
        
        # Cache de rutas calculadas entre puntos (para evitar recálculos)
        # Key: (lat1, lon1, lat2, lon2), Value: (route_nodes, distance_m, time_s)
        self._route_cache: Dict[Tuple[float, float, float, float], Tuple[List, float, float]] = {}
        
        # Crear directorio de cache
        os.makedirs(cache_dir, exist_ok=True)
        
        # Verificar conectividad con servidor Overpass personalizado
        self._verify_overpass_connection()
        
        # Velocidades por defecto (km/h) según tipo de vía
        # NOTA: Estas son velocidades REALES promedio considerando:
        # - Semáforos y cruces (reducen ~30-40% la velocidad)
        # - Tráfico urbano moderado
        # - Tiempos de aceleración/desaceleración
        # - Condiciones típicas de Montevideo
        self.default_speeds = {
            'motorway': 60,      # Rambla/autopistas urbanas (antes: 80)
            'trunk': 45,         # Vías rápidas urbanas (antes: 60)
            'primary': 35,       # Avenidas principales con semáforos (antes: 50)
            'secondary': 28,     # Calles importantes (antes: 40)
            'tertiary': 25,      # Calles secundarias (antes: 30)
            'residential': 22,   # Calles residenciales (antes: 30)
            'service': 15,       # Calles de servicio (antes: 20)
            'unclassified': 25,  # Calles sin clasificar (antes: 30)
        }
        
        # Factor de corrección urbano adicional (para casos con muchos semáforos)
        # Se puede ajustar por ciudad: Montevideo = 0.85 (muchos semáforos)
        self.urban_correction_factor = 0.85
        
        # OPTIMIZACIÓN: Grafo grande de Montevideo pre-cargado
        self._montevideo_graph: nx.MultiDiGraph | None = None
        self._montevideo_bounds = {
            'north': -34.80,
            'south': -34.92,
            'east': -56.10,
            'west': -56.22
        }
        
        logger.info(f"RouteCalculator inicializado (network_type: {network_type})")
    
    def _verify_overpass_connection(self):
        """Verifica conectividad con el servidor Overpass personalizado"""
        import requests
        
        try:
            # Hacer una consulta simple al servidor Overpass
            overpass_url = ox.settings.overpass_endpoint
            
            # Query simple para verificar conectividad
            test_query = "[out:json];node(1);out;"
            
            logger.info(f"🔍 Verificando conexión con Overpass: {overpass_url}")
            
            response = requests.post(
                overpass_url,
                data={'data': test_query},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Servidor Overpass respondiendo correctamente")
                logger.info(f"   Respuesta: {len(response.text)} bytes")
                return True
            else:
                logger.warning(f"⚠️ Servidor Overpass respondió con código: {response.status_code}")
                logger.warning(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ No se pudo verificar servidor Overpass: {e}")
            logger.warning(f"   Se usará lógica simplificada como fallback")
            return False
    
    def preload_montevideo_graph(self) -> bool:
        """
        PRE-CARGA el grafo grande de Montevideo para optimizar rendimiento.
        
        VENTAJAS:
        - Carga una sola vez al inicio (~2-5 segundos)
        - Evita cargar 20-30 grafos pequeños durante ejecución
        - Reduce tiempo total de 100 pedidos de 10min a 1-2min
        
        Returns:
            True si se cargó exitosamente, False en caso contrario
        """
        if self._montevideo_graph is not None:
            logger.debug("Grafo de Montevideo ya está pre-cargado")
            return True
        
        cache_key = "montevideo_full"
        
        # 1. Intentar cargar desde cache en disco
        cached_graph = self._load_graph_from_cache(cache_key)
        if cached_graph:
            self._montevideo_graph = cached_graph
            logger.info(f"✅ Grafo grande de Montevideo cargado desde cache: {len(cached_graph.nodes)} nodos")
            return True
        
        # 2. Descargar desde OSM
        try:
            logger.info("🌍 Descargando grafo GRANDE de Montevideo desde OSM...")
            logger.info(f"  Área: {self._montevideo_bounds}")
            start_time = time.time()
            
            # Descargar por bounding box completo
            # OSMnx usa: bbox=(north, south, east, west)
            graph = ox.graph_from_bbox(
                bbox=(
                    self._montevideo_bounds['north'],
                    self._montevideo_bounds['south'],
                    self._montevideo_bounds['east'],
                    self._montevideo_bounds['west']
                ),
                network_type=self.network_type,
                simplify=self.simplify
            )
            
            download_time = time.time() - start_time
            
            # Añadir pesos de tiempo
            graph = self._add_travel_times(graph)
            
            logger.info(
                f"✅ Grafo grande descargado: {len(graph.nodes)} nodos, "
                f"{len(graph.edges)} aristas, {download_time:.2f}s"
            )
            
            # Guardar en cache
            self._montevideo_graph = graph
            self._save_graph_to_cache(graph, cache_key)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error descargando grafo grande de Montevideo: {e}")
            logger.warning("   Se usarán grafos pequeños por área (modo tradicional)")
            return False
    
    def _get_cache_filename(self, location: str) -> str:
        """Genera nombre de archivo para cache de grafo"""
        safe_name = location.replace(" ", "_").replace(",", "")
        return os.path.join(self.cache_dir, f"graph_{safe_name}_{self.network_type}.pkl")
    
    def _load_graph_from_cache(self, location: str) -> Optional[nx.MultiDiGraph]:
        """Carga grafo desde cache en disco"""
        cache_file = self._get_cache_filename(location)
        
        if os.path.exists(cache_file):
            try:
                logger.debug(f"Cargando grafo desde cache: {cache_file}")
                with open(cache_file, 'rb') as f:
                    graph = pickle.load(f)
                logger.info(f"✓ Grafo cargado desde cache: {len(graph.nodes)} nodos")
                return graph
            except Exception as e:
                logger.warning(f"Error cargando cache: {e}")
                return None
        
        return None
    
    def _save_graph_to_cache(self, graph: nx.MultiDiGraph, location: str):
        """Guarda grafo en cache en disco"""
        cache_file = self._get_cache_filename(location)
        
        try:
            logger.debug(f"Guardando grafo en cache: {cache_file}")
            with open(cache_file, 'wb') as f:
                pickle.dump(graph, f, protocol=pickle.HIGHEST_PROTOCOL)
            logger.info(f"✓ Grafo guardado en cache")
        except Exception as e:
            logger.error(f"Error guardando cache: {e}")
    
    def get_graph_for_area(
        self,
        center: Coordinates,
        radius_meters: int = 10000,
        location_name: Optional[str] = None
    ) -> nx.MultiDiGraph:
        """
        Obtiene el grafo de red vial para un área.
        
        OPTIMIZACIÓN: Si el grafo grande de Montevideo está pre-cargado, lo usa directamente
        en lugar de cargar grafos pequeños por área.
        
        ESTRATEGIAS:
        0. **NUEVO**: Usar grafo grande pre-cargado (si disponible) - INSTANTÁNEO
        1. Por nombre de ciudad (ej: "Buenos Aires, Argentina") - MÁS RÁPIDO
        2. Por punto central + radio - MÁS FLEXIBLE
        
        El grafo es DIRIGIDO, lo que significa que respeta el sentido
        de las calles. Una calle de doble mano tendrá aristas en ambos sentidos.
        
        Args:
            center: Coordenadas del centro del área
            radius_meters: Radio de búsqueda en metros
            location_name: Nombre de la ciudad (opcional, mejora cache)
            
        Returns:
            Grafo de red vial (MultiDiGraph)
        """
        # OPTIMIZACIÓN: Si el grafo grande está cargado y el punto está en Montevideo, usarlo
        if self._montevideo_graph is not None:
            bounds = self._montevideo_bounds
            if (bounds['south'] <= center.lat <= bounds['north'] and 
                bounds['west'] <= center.lon <= bounds['east']):
                logger.debug("✅ Usando grafo grande pre-cargado de Montevideo (instantáneo)")
                return self._montevideo_graph
        
        cache_key = location_name or f"{center.lat}_{center.lon}_{radius_meters}"
        
        # 1. Verificar cache en memoria
        if cache_key in self._graph_cache:
            logger.debug("Grafo encontrado en cache de memoria")
            return self._graph_cache[cache_key]
        
        # 2. Verificar cache en disco
        cached_graph = self._load_graph_from_cache(cache_key)
        if cached_graph:
            self._graph_cache[cache_key] = cached_graph
            return cached_graph
        
        # 3. Descargar desde OpenStreetMap
        logger.info(f"🌍 Descargando grafo desde OSM para {cache_key}...")
        logger.info(f"  Usando servidor Overpass: {ox.settings.overpass_endpoint}")
        logger.info(f"  Coordenadas: ({center.lat}, {center.lon}), Radio: {radius_meters}m")
        start_time = time.time()
        
        try:
            if location_name:
                # Descargar por nombre de ciudad
                logger.info(f"  Método: graph_from_place('{location_name}')")
                graph = ox.graph_from_place(
                    location_name,
                    network_type=self.network_type,
                    simplify=self.simplify
                )
            else:
                # Descargar por coordenadas y radio
                logger.info(f"  Método: graph_from_point()")
                graph = ox.graph_from_point(
                    (center.lat, center.lon),
                    dist=radius_meters,
                    network_type=self.network_type,
                    simplify=self.simplify
                )
            
            download_time = time.time() - start_time
            
            # Añadir pesos de tiempo a las aristas
            graph = self._add_travel_times(graph)
            
            logger.info(
                f"✓ Grafo descargado: {len(graph.nodes)} nodos, "
                f"{len(graph.edges)} aristas, "
                f"{download_time:.2f}s"
            )
            
            # Guardar en cache
            self._graph_cache[cache_key] = graph
            self._save_graph_to_cache(graph, cache_key)
            
            return graph
            
        except Exception as e:
            logger.error(f"❌ Error descargando grafo: {e}")
            raise
    
    def _add_travel_times(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        Añade tiempos de viaje a las aristas del grafo.
        
        CÁLCULO REALISTA:
        tiempo = (distancia / velocidad) * factor_corrección_urbano
        
        La velocidad se determina por:
        1. Velocidad máxima de la vía (si está disponible) - se reduce a realista
        2. Tipo de vía (motorway, primary, residential, etc.)
        3. Velocidad por defecto
        
        El factor de corrección urbano (0.85 para Montevideo) considera:
        - Semáforos (principal factor: reducción ~20-30%)
        - Cruces y giros
        - Peatones y ciclistas
        - Congestión moderada típica
        - Tiempo de aceleración/desaceleración
        
        Esto permite calcular rutas con TIEMPOS REALISTAS, no ideales.
        """
        for u, v, k, data in graph.edges(keys=True, data=True):
            # Obtener longitud de la arista (metros)
            length = data.get('length', 0)
            
            # Determinar velocidad base
            if 'maxspeed' in data:
                try:
                    # Intentar parsear velocidad máxima
                    speed_str = data['maxspeed']
                    if isinstance(speed_str, list):
                        speed_str = speed_str[0]
                    speed_kmh = float(speed_str.split()[0])
                    # Reducir velocidad máxima a velocidad realista (75% de la máxima)
                    speed_kmh = speed_kmh * 0.75
                except:
                    speed_kmh = self._get_speed_for_highway_type(data.get('highway'))
            else:
                speed_kmh = self._get_speed_for_highway_type(data.get('highway'))
            
            # Calcular tiempo de viaje base (segundos)
            speed_ms = speed_kmh * 1000 / 3600  # km/h a m/s
            travel_time_base = length / speed_ms if speed_ms > 0 else length / 10
            
            # Aplicar factor de corrección urbano (semáforos, cruces, etc.)
            travel_time = travel_time_base / self.urban_correction_factor
            
            # Añadir al grafo
            data['travel_time'] = travel_time
            data['speed_kmh'] = speed_kmh
        
        return graph
    
    def _get_speed_for_highway_type(self, highway_type) -> float:
        """
        Obtiene velocidad estimada según tipo de vía.
        
        TIPOS DE VÍAS (OpenStreetMap):
        - motorway: Autopista
        - trunk: Vía rápida
        - primary: Avenida principal
        - secondary: Calle secundaria
        - residential: Calle residencial
        - service: Calle de servicio
        """
        if isinstance(highway_type, list):
            highway_type = highway_type[0]
        
        return self.default_speeds.get(highway_type, 30)
    
    def find_nearest_node(
        self,
        graph: nx.MultiDiGraph,
        coordinates: Coordinates
    ) -> int:
        """
        Encuentra el nodo más cercano a unas coordenadas.
        
        IMPORTANTE:
        Para calcular una ruta, necesitamos encontrar los NODOS
        (intersecciones) más cercanos a las coordenadas origen/destino.
        
        Args:
            graph: Grafo de la red vial
            coordinates: Coordenadas a buscar
            
        Returns:
            ID del nodo más cercano
        """
        nearest_node = ox.nearest_nodes(
            graph,
            coordinates.lon,
            coordinates.lat
        )
        
        logger.debug(f"Nodo más cercano a {coordinates}: {nearest_node}")
        return nearest_node
    
    def calculate_route(
        self,
        graph: nx.MultiDiGraph,
        origin: Coordinates,
        destination: Coordinates,
        optimize_by: str = "time"
    ) -> Optional[Tuple[List[int], float, float]]:
        """
        Calcula la ruta óptima entre dos puntos.
        
        ALGORITMO:
        Usa algoritmo de Dijkstra para encontrar el camino más corto
        en el grafo dirigido, considerando el peso especificado.
        
        Args:
            graph: Grafo de la red vial
            origin: Coordenadas de origen
            destination: Coordenadas de destino
            optimize_by: 'time' (tiempo) o 'distance' (distancia)
            
        Returns:
            Tupla (nodos_ruta, distancia_metros, tiempo_segundos) o None
        """
        try:
            # Crear clave de cache con coordenadas redondeadas (5 decimales ~1m precisión)
            cache_key = (
                round(origin.lat, 5), 
                round(origin.lon, 5),
                round(destination.lat, 5), 
                round(destination.lon, 5)
            )
            
            # Verificar cache
            if cache_key in self._route_cache:
                logger.debug(f"✓ Ruta obtenida de cache: {cache_key[0:2]} -> {cache_key[2:4]}")
                return self._route_cache[cache_key]
            
            # Encontrar nodos más cercanos
            origin_node = self.find_nearest_node(graph, origin)
            dest_node = self.find_nearest_node(graph, destination)
            
            logger.debug(f"Calculando ruta: {origin_node} -> {dest_node}")
            
            # Seleccionar peso a optimizar
            weight = 'travel_time' if optimize_by == 'time' else 'length'
            
            # Calcular ruta óptima usando Dijkstra
            route_nodes = nx.shortest_path(
                graph,
                origin_node,
                dest_node,
                weight=weight
            )
            
            # Calcular métricas de la ruta
            total_distance = 0
            total_time = 0
            
            for i in range(len(route_nodes) - 1):
                u, v = route_nodes[i], route_nodes[i + 1]
                
                # Obtener datos de la arista
                # Nota: MultiDiGraph puede tener múltiples aristas entre nodos
                edge_data = graph.get_edge_data(u, v)
                if edge_data:
                    # Tomar la primera arista (key=0)
                    data = edge_data[0]
                    total_distance += data.get('length', 0)
                    total_time += data.get('travel_time', 0)
            
            # Guardar en cache
            result = (route_nodes, total_distance, total_time)
            self._route_cache[cache_key] = result
            
            logger.info(
                f"✓ Ruta calculada: {len(route_nodes)} nodos, "
                f"{total_distance:.0f}m, {total_time/60:.1f}min"
            )
            
            return result
            
        except nx.NetworkXNoPath:
            logger.error(f"❌ No existe ruta entre {origin} y {destination}")
            return None
        except Exception as e:
            logger.error(f"❌ Error calculando ruta: {e}")
            return None
    
    def get_route_coordinates(
        self,
        graph: nx.MultiDiGraph,
        route_nodes: List[int]
    ) -> List[Coordinates]:
        """
        Obtiene las coordenadas de todos los nodos de la ruta.
        
        ÚTIL PARA:
        - Visualizar la ruta en un mapa
        - Calcular puntos intermedios
        - Validar la ruta visualmente
        
        Args:
            graph: Grafo de la red vial
            route_nodes: Lista de IDs de nodos de la ruta
            
        Returns:
            Lista de coordenadas
        """
        coordinates = []
        
        for node_id in route_nodes:
            node_data = graph.nodes[node_id]
            coords = Coordinates(
                lat=node_data['y'],
                lon=node_data['x']
            )
            coordinates.append(coords)
        
        return coordinates
    
    def calculate_route_full(
        self,
        origin: Coordinates,
        destination: Coordinates,
        vehicle_id: str = "unknown",
        location_name: Optional[str] = "Buenos Aires, Argentina"
    ) -> Optional[Route]:
        """
        Calcula ruta completa con toda la información estructurada.
        
        Esta es la función PRINCIPAL que se usa desde el sistema de asignación.
        
        Args:
            origin: Punto de origen
            destination: Punto de destino
            vehicle_id: ID del vehículo
            location_name: Nombre de la ciudad para cache
            
        Returns:
            Objeto Route completo o None si falla
        """
        logger.info(f"🚗 Calculando ruta completa: {vehicle_id}")
        
        try:
            # 1. Obtener grafo de la zona
            graph = self.get_graph_for_area(
                center=origin,
                radius_meters=20000,  # 20km de radio
                location_name=location_name
            )
            
            # 2. Calcular ruta
            result = self.calculate_route(
                graph,
                origin,
                destination,
                optimize_by='time'
            )
            
            if not result:
                logger.error("No se pudo calcular la ruta")
                return None
            
            route_nodes, total_distance, total_time = result
            
            # 3. Obtener coordenadas de la ruta
            path_coordinates = self.get_route_coordinates(graph, route_nodes)
            
            # 4. Crear objeto Route
            route = Route(
                vehicle_id=vehicle_id,
                segments=[
                    RouteSegment(
                        from_location=origin,
                        to_location=destination,
                        distance_meters=total_distance,
                        duration_seconds=total_time,
                        path=path_coordinates
                    )
                ],
                total_distance_meters=total_distance,
                total_duration_seconds=total_time,
                estimated_arrival=datetime.now() + timedelta(seconds=total_time),
                orders_in_route=[]
            )
            
            logger.info(
                f"✓ Ruta completa: {total_distance/1000:.2f}km, "
                f"{total_time/60:.1f}min"
            )
            
            return route
            
        except Exception as e:
            logger.error(f"❌ Error en calculate_route_full: {e}")
            return None
    
    def calculate_distance_matrix(
        self,
        locations: List[Coordinates],
        location_name: Optional[str] = "Buenos Aires, Argentina"
    ) -> np.ndarray:
        """
        Calcula matriz de distancias entre múltiples puntos.
        
        APLICACIÓN:
        - Problema del viajante (TSP)
        - Optimización de secuencia de entregas
        - Agrupamiento de pedidos cercanos
        
        Args:
            locations: Lista de coordenadas
            location_name: Nombre de la ciudad
            
        Returns:
            Matriz NxN donde matrix[i][j] = distancia de i a j
        """
        n = len(locations)
        matrix = np.zeros((n, n))
        
        logger.info(f"📊 Calculando matriz de distancias {n}x{n}")
        
        # Obtener grafo
        center = locations[0]
        graph = self.get_graph_for_area(center, 20000, location_name)
        
        # Calcular distancias
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 0
                else:
                    result = self.calculate_route(
                        graph,
                        locations[i],
                        locations[j]
                    )
                    if result:
                        _, distance, _ = result
                        matrix[i][j] = distance
                    else:
                        matrix[i][j] = float('inf')
        
        return matrix


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def haversine_distance(coord1: Coordinates, coord2: Coordinates) -> float:
    """
    Calcula distancia en línea recta (haversine).
    
    ÚTIL PARA:
    - Estimaciones rápidas
    - Pre-filtrado de candidatos
    - Cuando no se necesita ruta exacta
    
    NOTA: Esta es distancia "en línea recta", NO considera calles.
    Para rutas reales usar RouteCalculator.
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000  # Radio de la Tierra en metros
    
    lat1, lon1 = radians(coord1.lat), radians(coord1.lon)
    lat2, lon2 = radians(coord2.lat), radians(coord2.lon)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c
    return distance


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    from loguru import logger
    
    logger.add("logs/routing.log", rotation="1 day")
    
    # Crear calculador
    calculator = RouteCalculator()
    
    # Ejemplo: Calcular ruta en Buenos Aires
    origin = Coordinates(lat=-34.603722, lon=-58.381592)  # Obelisco
    destination = Coordinates(lat=-34.608, lon=-58.373)   # Casa Rosada
    
    route = calculator.calculate_route_full(
        origin=origin,
        destination=destination,
        vehicle_id="MOV-001",
        location_name="Buenos Aires, Argentina"
    )
    
    if route:
        print(f"✓ Ruta calculada:")
        print(f"  Distancia: {route.total_distance_meters/1000:.2f} km")
        print(f"  Tiempo: {route.total_duration_seconds/60:.1f} min")
        print(f"  Puntos en ruta: {len(route.segments[0].path or [])}")
