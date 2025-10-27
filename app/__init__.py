"""
Sistema de Ruteo Inteligente

Paquete principal con todos los módulos del sistema.
"""

__version__ = "1.0.0"
__author__ = "Sistema de Ruteo Inteligente"

from app.models import (
    Order,
    Vehicle,
    Coordinates,
    Address,
    SystemConfig,
    AssignmentRequest,
    AssignmentResult
)

from app.geocoding import GeocodingService, get_geocoding_service
from app.routing import RouteCalculator, haversine_distance
from app.scoring import ScoringEngine
from app.optimizer import RouteOptimizer, ClusteringOptimizer

__all__ = [
    # Models
    "Order",
    "Vehicle",
    "Coordinates",
    "Address",
    "SystemConfig",
    "AssignmentRequest",
    "AssignmentResult",
    
    # Services
    "GeocodingService",
    "get_geocoding_service",
    "RouteCalculator",
    "haversine_distance",
    "ScoringEngine",
    "RouteOptimizer",
    "ClusteringOptimizer",
]
