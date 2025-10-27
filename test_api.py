"""
Cliente de prueba para la API.

Permite probar la API de forma interactiva.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any


class RuteoAPIClient:
    """Cliente para interactuar con la API de ruteo"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica el estado de la API"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def assign_order(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Asigna un pedido a un vehículo"""
        response = self.session.post(
            f"{self.base_url}/api/v1/assign-order",
            json=request_data
        )
        response.raise_for_status()
        return response.json()
    
    def geocode(self, address: Dict[str, str]) -> Dict[str, float]:
        """Geocodifica una dirección"""
        response = self.session.post(
            f"{self.base_url}/api/v1/geocode",
            json=address
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema"""
        response = self.session.get(f"{self.base_url}/api/v1/stats")
        response.raise_for_status()
        return response.json()


def test_api():
    """Test completo de la API"""
    
    print("=" * 70)
    print("TEST DE API - Sistema de Ruteo Inteligente")
    print("=" * 70)
    
    # Crear cliente
    client = RuteoAPIClient()
    
    # 1. Health check
    print("\n1️⃣  Health Check...")
    try:
        health = client.health_check()
        print(f"✓ API Status: {health['status']}")
        print(f"  Version: {health['version']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Asegúrate de que la API esté corriendo: python app/main.py")
        return
    
    # 2. Geocodificación
    print("\n2️⃣  Geocodificación...")
    try:
        coords = client.geocode({
            "street": "Av. Corrientes 1234",
            "city": "Buenos Aires",
            "country": "Argentina"
        })
        print(f"✓ Coordenadas obtenidas:")
        print(f"  Lat: {coords['lat']}")
        print(f"  Lon: {coords['lon']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        # Usar coordenadas de ejemplo
        coords = {"lat": -34.603722, "lon": -58.381592}
    
    # 3. Asignación de pedido
    print("\n3️⃣  Asignación de pedido...")
    
    deadline = (datetime.now() + timedelta(hours=2)).isoformat()
    
    request_data = {
        "order": {
            "id": "PED-TEST-001",
            "customer_name": "Cliente Test",
            "address": {
                "street": "Av. Corrientes 1234",
                "city": "Buenos Aires",
                "country": "Argentina"
            },
            "delivery_location": coords,
            "deadline": deadline,
            "priority": "high",
            "estimated_duration": 10
        },
        "vehicles": [
            {
                "id": "MOV-001",
                "driver_name": "Carlos García",
                "vehicle_type": "moto",
                "current_location": coords,
                "max_capacity": 6,
                "current_load": 2,
                "current_orders": ["PED-010", "PED-011"],
                "status": "available",
                "success_rate": 0.95,
                "total_deliveries": 150
            },
            {
                "id": "MOV-002",
                "driver_name": "María López",
                "vehicle_type": "auto",
                "current_location": {
                    "lat": coords["lat"] + 0.01,
                    "lon": coords["lon"] - 0.01
                },
                "max_capacity": 8,
                "current_load": 1,
                "current_orders": ["PED-012"],
                "status": "available",
                "success_rate": 0.88,
                "total_deliveries": 80
            }
        ],
        "config": {
            "default_max_capacity": 6,
            "weight_distance": 0.30,
            "weight_capacity": 0.20,
            "weight_time_urgency": 0.25,
            "weight_route_compatibility": 0.15,
            "weight_vehicle_performance": 0.10
        }
    }
    
    try:
        result = client.assign_order(request_data)
        
        print(f"✓ Asignación exitosa!")
        print(f"  Pedido: {result['order_id']}")
        print(f"  Asignado a: {result['assigned_vehicle_id']}")
        print(f"  Confianza: {result['confidence_score']:.1%}")
        
        if result.get('score_details'):
            score = result['score_details']
            print(f"\n  📊 Desglose del score:")
            print(f"    - Distancia: {score['distance_score']:.3f}")
            print(f"    - Capacidad: {score['capacity_score']:.3f}")
            print(f"    - Urgencia: {score['time_urgency_score']:.3f}")
            print(f"    - Compatibilidad: {score['route_compatibility_score']:.3f}")
            print(f"    - Desempeño: {score['vehicle_performance_score']:.3f}")
            print(f"\n  🚗 Detalles:")
            print(f"    - Distancia al pedido: {score['distance_to_delivery_km']:.2f} km")
            print(f"    - Capacidad disponible: {score['available_capacity']} espacios")
            print(f"    - Llegará a tiempo: {'SÍ' if score['will_arrive_on_time'] else 'NO'}")
        
        if result.get('alternatives'):
            print(f"\n  🔄 Alternativas consideradas:")
            for alt in result['alternatives'][:3]:
                print(f"    - {alt['vehicle_id']}: score {alt['score']:.3f}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 4. Estadísticas
    print("\n4️⃣  Estadísticas del sistema...")
    try:
        stats = client.get_stats()
        print(f"✓ Estadísticas obtenidas:")
        print(f"  Cache de geocoding: {stats.get('geocoding', {}).get('cache_size', 0)} entradas")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✓ TEST COMPLETADO")
    print("=" * 70)


if __name__ == "__main__":
    test_api()
