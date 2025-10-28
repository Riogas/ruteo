"""
Middleware personalizado para la API de Ruteo
"""

from .logging import DetailedRequestLogger, EndpointLogger

__all__ = ["DetailedRequestLogger", "EndpointLogger"]
