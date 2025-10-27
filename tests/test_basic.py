"""
Script de Testing para el Sistema de Ruteo.

Tests básicos para verificar funcionalidad.
"""

import pytest
from datetime import datetime, timedelta

from app.models import (
    Order, Vehicle, Coordinates, Address,
    VehicleType, OrderPriority, SystemConfig
)
from app.scoring import ScoringEngine
from app.routing import RouteCalculator, haversine_distance


class TestModels:
    """Tests para los modelos de datos"""
    
    def test_coordinates_validation(self):
        """Test validación de coordenadas"""
        # Coordenadas válidas
        coords = Coordinates(lat=-34.603722, lon=-58.381592)
        assert coords.lat == -34.603722
        assert coords.lon == -58.381592
        
        # Latitud fuera de rango
        with pytest.raises(ValueError):
            Coordinates(lat=100, lon=-58.381592)
    
    def test_vehicle_capacity(self):
        """Test capacidad de vehículos"""
        vehicle = Vehicle(
            id="MOV-001",
            vehicle_type=VehicleType.MOTO,
            current_location=Coordinates(lat=-34.603, lon=-58.381),
            max_capacity=6,
            current_load=4
        )
        
        assert vehicle.available_capacity == 2
        assert vehicle.is_available == True
        
        # Vehículo lleno
        vehicle.current_load = 6
        assert vehicle.available_capacity == 0
        assert vehicle.is_available == False
    
    def test_order_deadline(self):
        """Test validación de deadline"""
        now = datetime.now()
        
        # Deadline futuro (válido)
        order = Order(
            id="PED-001",
            deadline=now + timedelta(hours=2),
            delivery_location=Coordinates(lat=-34.603, lon=-58.381)
        )
        
        assert order.deadline > now


class TestRouting:
    """Tests para el sistema de rutas"""
    
    def test_haversine_distance(self):
        """Test cálculo de distancia haversine"""
        # Obelisco a Casa Rosada (≈1.5 km)
        obelisco = Coordinates(lat=-34.603722, lon=-58.381592)
        casa_rosada = Coordinates(lat=-34.608, lon=-58.373)
        
        distance = haversine_distance(obelisco, casa_rosada)
        
        # La distancia debe estar entre 1-2 km
        assert 1000 < distance < 2000
    
    def test_route_calculator_init(self):
        """Test inicialización del calculador de rutas"""
        calculator = RouteCalculator()
        
        assert calculator.network_type == "drive"
        assert calculator.default_speeds["motorway"] == 80


class TestScoring:
    """Tests para el sistema de scoring"""
    
    def setup_method(self):
        """Configuración para cada test"""
        self.config = SystemConfig()
        self.route_calc = RouteCalculator()
        self.scoring_engine = ScoringEngine(self.config, self.route_calc)
        
        self.order = Order(
            id="PED-001",
            deadline=datetime.now() + timedelta(hours=2),
            delivery_location=Coordinates(lat=-34.603, lon=-58.381),
            priority=OrderPriority.HIGH
        )
    
    def test_distance_score(self):
        """Test score de distancia"""
        vehicle = Vehicle(
            id="MOV-001",
            vehicle_type=VehicleType.MOTO,
            current_location=Coordinates(lat=-34.605, lon=-58.380),
            max_capacity=6,
            current_load=2
        )
        
        score, distance = self.scoring_engine.calculate_distance_score(
            vehicle, self.order
        )
        
        assert 0 <= score <= 1
        assert distance > 0
    
    def test_capacity_score(self):
        """Test score de capacidad"""
        # Vehículo con buena capacidad
        vehicle1 = Vehicle(
            id="MOV-001",
            vehicle_type=VehicleType.MOTO,
            current_location=Coordinates(lat=-34.603, lon=-58.381),
            max_capacity=6,
            current_load=2
        )
        
        score1, cap1 = self.scoring_engine.calculate_capacity_score(vehicle1)
        assert score1 > 0.5
        assert cap1 == 4
        
        # Vehículo sin capacidad
        vehicle2 = Vehicle(
            id="MOV-002",
            vehicle_type=VehicleType.MOTO,
            current_location=Coordinates(lat=-34.603, lon=-58.381),
            max_capacity=6,
            current_load=6
        )
        
        score2, cap2 = self.scoring_engine.calculate_capacity_score(vehicle2)
        assert score2 == 0
        assert cap2 == 0
    
    def test_ranking(self):
        """Test ranking de vehículos"""
        vehicles = [
            Vehicle(
                id="MOV-001",
                vehicle_type=VehicleType.MOTO,
                current_location=Coordinates(lat=-34.605, lon=-58.380),
                max_capacity=6,
                current_load=2,
                success_rate=0.95
            ),
            Vehicle(
                id="MOV-002",
                vehicle_type=VehicleType.AUTO,
                current_location=Coordinates(lat=-34.610, lon=-58.375),
                max_capacity=8,
                current_load=1,
                success_rate=0.88
            )
        ]
        
        ranked = self.scoring_engine.rank_vehicles(vehicles, self.order)
        
        assert len(ranked) == 2
        # El primer vehículo debe tener el mejor score
        assert ranked[0][1].total_score >= ranked[1][1].total_score


# ============================================================================
# EJECUTAR TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
