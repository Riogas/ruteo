#!/usr/bin/env python3
"""
Cliente de prueba para el Sistema de Ruteo
Ejecutar: python cliente_simple.py
"""
import requests
import json
from datetime import datetime, timedelta

# Configuración
API_URL = "http://localhost:8080"

def print_separator(title=""):
    """Imprimir separador bonito"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"{'='*60}\n")

def test_1_health_check():
    """Test 1: Verificar que el servidor está funcionando"""
    print_separator("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        result = response.json()
        
        print("✅ Servidor está funcionando!")
        print(f"   Status: {result['status']}")
        print(f"   Versión: {result['version']}")
        print("\n   Servicios:")
        for service, status in result['services'].items():
            print(f"     - {service}: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Error al conectar con el servidor: {e}")
        print(f"   Verifica que el servidor esté corriendo en {API_URL}")
        return False

def test_2_geocoding():
    """Test 2: Probar geocodificación de direcciones"""
    print_separator("TEST 2: Geocodificación")
    
    direcciones = [
        "Obelisco, Buenos Aires, Argentina",
        "Av. Corrientes 1000, Buenos Aires",
        "Av. 9 de Julio, Buenos Aires"
    ]
    
    results = []
    
    for direccion in direcciones:
        try:
            print(f"Geocodificando: {direccion}")
            
            payload = {"address": direccion}
            response = requests.post(
                f"{API_URL}/api/v1/geocode",
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"  ✅ {result['normalized_address']}")
            print(f"     Coordenadas: ({result['coordinates']['lat']:.6f}, {result['coordinates']['lon']:.6f})")
            print(f"     Proveedor: {result['provider']}")
            print(f"     Confianza: {result.get('confidence', 'N/A')}\n")
            
            results.append(result['coordinates'])
            
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
            results.append(None)
    
    return results

def test_3_simple_assignment():
    """Test 3: Asignación simple con un solo vehículo"""
    print_separator("TEST 3: Asignación Simple (1 vehículo vacío)")
    
    # Deadline: 3 horas desde ahora
    deadline = (datetime.now() + timedelta(hours=3)).isoformat()
    
    payload = {
        "order": {
            "id": "TEST-001",
            "customer_name": "Juan Pérez",
            "delivery_address": "Av. Corrientes 1234, Buenos Aires, Argentina",
            "deadline": deadline
        },
        "available_vehicles": [
            {
                "id": "VH-001",
                "driver_name": "Carlos",
                "current_location": {
                    "lat": -34.603722,
                    "lon": -58.381592
                },
                "current_orders": [],
                "capacity": 8,
                "performance_score": 4.5
            }
        ]
    }
    
    try:
        print("Enviando orden...")
        response = requests.post(
            f"{API_URL}/api/v1/assign-order",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        print("✅ Orden asignada exitosamente!\n")
        
        # Información del vehículo asignado
        vehicle = result['assigned_vehicle']
        print(f"Vehículo asignado: {vehicle['driver_name']} ({vehicle['id']})")
        
        # Scores
        score = result['scores'][0]
        print(f"\nScores:")
        print(f"  Total: {score['total_score']:.2f}/100")
        print(f"  - Distancia: {score['distance_score']:.1f}")
        print(f"  - Capacidad: {score['capacity_score']:.1f}")
        print(f"  - Urgencia: {score['time_urgency_score']:.1f}")
        print(f"  - Compatibilidad: {score['route_compatibility_score']:.1f}")
        print(f"  - Performance: {score['performance_score']:.1f}")
        
        # Detalles de ruta
        print(f"\nDetalles de la ruta:")
        print(f"  Distancia: {score['distance_km']:.2f} km")
        print(f"  Tiempo estimado: {score['estimated_time_minutes']} minutos")
        print(f"  Cumple deadline: {'✅ Sí' if score['can_meet_deadline'] else '❌ No'}")
        
        # Geocodificación
        geocode = result['geocoding_result']
        print(f"\nDirección geocodificada:")
        print(f"  Original: {geocode['original_address']}")
        print(f"  Normalizada: {geocode['normalized_address']}")
        print(f"  Coordenadas: ({geocode['coordinates']['lat']:.6f}, {geocode['coordinates']['lon']:.6f})")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_4_multiple_vehicles():
    """Test 4: Asignación con múltiples vehículos"""
    print_separator("TEST 4: Asignación con Múltiples Vehículos")
    
    deadline = (datetime.now() + timedelta(hours=2)).isoformat()
    
    payload = {
        "order": {
            "id": "TEST-002",
            "customer_name": "María González",
            "delivery_address": "Av. Santa Fe 2500, Buenos Aires",
            "deadline": deadline
        },
        "available_vehicles": [
            {
                "id": "VH-001",
                "driver_name": "Carlos",
                "current_location": {
                    "lat": -34.603722,
                    "lon": -58.381592
                },
                "current_orders": [],
                "capacity": 8,
                "performance_score": 4.5
            },
            {
                "id": "VH-002",
                "driver_name": "Ana",
                "current_location": {
                    "lat": -34.595000,
                    "lon": -58.373000
                },
                "current_orders": [],
                "capacity": 6,
                "performance_score": 4.8
            },
            {
                "id": "VH-003",
                "driver_name": "Jorge",
                "current_location": {
                    "lat": -34.615000,
                    "lon": -58.445000
                },
                "current_orders": [],
                "capacity": 10,
                "performance_score": 4.2
            }
        ]
    }
    
    try:
        print("Evaluando 3 vehículos disponibles...")
        response = requests.post(
            f"{API_URL}/api/v1/assign-order",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        print("✅ Evaluación completa!\n")
        
        # Mostrar todos los scores
        print("Rankings de vehículos:")
        scores = sorted(result['scores'], key=lambda x: x['total_score'], reverse=True)
        
        for i, score in enumerate(scores, 1):
            print(f"\n{i}. {score['vehicle_id']} - Score: {score['total_score']:.2f}/100")
            print(f"   Distancia: {score['distance_km']:.2f} km")
            print(f"   Tiempo: {score['estimated_time_minutes']} min")
            print(f"   Deadline: {'✅' if score['can_meet_deadline'] else '❌'}")
        
        # Ganador
        winner = result['assigned_vehicle']
        print(f"\n🏆 GANADOR: {winner['driver_name']} ({winner['id']})")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_5_vehicle_with_orders():
    """Test 5: Asignación a vehículo que ya tiene órdenes"""
    print_separator("TEST 5: Vehículo con Órdenes Existentes")
    
    deadline = (datetime.now() + timedelta(hours=4)).isoformat()
    existing_deadline = (datetime.now() + timedelta(hours=2)).isoformat()
    
    payload = {
        "order": {
            "id": "TEST-003",
            "customer_name": "Roberto López",
            "delivery_address": "Av. Cabildo 1500, Buenos Aires",
            "deadline": deadline
        },
        "available_vehicles": [
            {
                "id": "VH-BUSY",
                "driver_name": "Andrés",
                "current_location": {
                    "lat": -34.560000,
                    "lon": -58.450000
                },
                "current_orders": [
                    {
                        "id": "ORD-100",
                        "customer_name": "Cliente A",
                        "delivery_address": {
                            "lat": -34.565000,
                            "lon": -58.455000
                        },
                        "deadline": existing_deadline
                    }
                ],
                "capacity": 8,
                "performance_score": 4.7
            }
        ]
    }
    
    try:
        print("Asignando a vehículo con órdenes existentes...")
        print(f"  Vehículo tiene: 1 orden previa")
        print(f"  Capacidad: 8")
        print(f"  Disponible: 7 espacios\n")
        
        response = requests.post(
            f"{API_URL}/api/v1/assign-order",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        print("✅ Orden asignada!\n")
        
        # Ruta optimizada
        route = result.get('optimized_route')
        if route:
            print(f"Ruta optimizada:")
            print(f"  Total: {route['total_distance_km']:.2f} km en {route['total_time_minutes']} min")
            print(f"\n  Secuencia de entregas:")
            for i, waypoint in enumerate(route['waypoints'], 1):
                print(f"    {i}. {waypoint['order_id']} - {waypoint['type']}")
                print(f"       ETA: {waypoint['arrival_time']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("  🚚 CLIENTE DE PRUEBA - SISTEMA DE RUTEO")
    print("="*60)
    
    # Test 1: Health Check
    if not test_1_health_check():
        print("\n❌ El servidor no está disponible. Tests cancelados.")
        return
    
    # Test 2: Geocoding
    test_2_geocoding()
    
    # Test 3: Asignación simple
    test_3_simple_assignment()
    
    # Test 4: Múltiples vehículos
    test_4_multiple_vehicles()
    
    # Test 5: Vehículo con órdenes
    test_5_vehicle_with_orders()
    
    # Resumen final
    print_separator("TESTS COMPLETADOS")
    print("✅ Todos los tests ejecutados")
    print("\nPara más detalles:")
    print(f"  - Documentación interactiva: {API_URL}/docs")
    print(f"  - Guía de uso: USO_ENDPOINTS.md")
    print(f"  - Arquitectura: ARCHITECTURE.md")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
