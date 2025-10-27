"""
Script de ejemplo de uso del Sistema de Ruteo Inteligente.

Demuestra cómo usar la API para asignar pedidos a vehículos.

EJECUCIÓN:
    python example_usage.py
"""

from datetime import datetime, timedelta
from app.models import (
    Order, Vehicle, Address, Coordinates,
    VehicleType, OrderPriority, SystemConfig,
    AssignmentRequest
)
from app.geocoding import get_geocoding_service
from app.routing import RouteCalculator
from app.scoring import ScoringEngine
from loguru import logger


def main():
    """Ejemplo completo de uso del sistema"""
    
    logger.info("=" * 70)
    logger.info("EJEMPLO DE USO: Sistema de Ruteo Inteligente")
    logger.info("=" * 70)
    
    # ========================================================================
    # 1. CREAR CONFIGURACIÓN
    # ========================================================================
    
    logger.info("\n📋 1. Configurando sistema...")
    
    config = SystemConfig(
        default_max_capacity=6,
        weight_distance=0.30,
        weight_capacity=0.20,
        weight_time_urgency=0.25,
        weight_route_compatibility=0.15,
        weight_vehicle_performance=0.10
    )
    
    logger.info("✓ Configuración creada")
    logger.info(f"  - Capacidad por defecto: {config.default_max_capacity}")
    logger.info(f"  - Peso distancia: {config.weight_distance}")
    logger.info(f"  - Peso capacidad: {config.weight_capacity}")
    
    # ========================================================================
    # 2. CREAR PEDIDO
    # ========================================================================
    
    logger.info("\n📦 2. Creando pedido...")
    
    order = Order(
        id="PED-001",
        customer_name="Juan Pérez",
        customer_phone="+54 11 1234-5678",
        address=Address(
            street="Av. Corrientes 1234",
            city="Buenos Aires",
            state="CABA",
            country="Argentina"
        ),
        deadline=datetime.now() + timedelta(hours=2),
        priority=OrderPriority.HIGH,
        weight_kg=2.5,
        estimated_duration=10  # 10 minutos de entrega
    )
    
    logger.info("✓ Pedido creado")
    logger.info(f"  - ID: {order.id}")
    logger.info(f"  - Cliente: {order.customer_name}")
    logger.info(f"  - Dirección: {order.address.street}, {order.address.city}")
    logger.info(f"  - Deadline: {order.deadline.strftime('%Y-%m-%d %H:%M')}")
    logger.info(f"  - Prioridad: {order.priority.value}")
    
    # ========================================================================
    # 3. GEOCODIFICAR DIRECCIÓN
    # ========================================================================
    
    logger.info("\n🔍 3. Geocodificando dirección...")
    
    geocoding_service = get_geocoding_service()
    coords = geocoding_service.geocode(order.address)
    
    if coords:
        order.delivery_location = coords
        logger.info("✓ Dirección geocodificada")
        logger.info(f"  - Latitud: {coords.lat}")
        logger.info(f"  - Longitud: {coords.lon}")
    else:
        logger.error("✗ No se pudo geocodificar la dirección")
        # Usar coordenadas de ejemplo
        order.delivery_location = Coordinates(lat=-34.603722, lon=-58.381592)
        logger.info("  - Usando coordenadas de ejemplo (Obelisco, Buenos Aires)")
    
    # ========================================================================
    # 4. CREAR VEHÍCULOS DISPONIBLES
    # ========================================================================
    
    logger.info("\n🚗 4. Creando flota de vehículos...")
    
    vehicles = [
        Vehicle(
            id="MOV-001",
            driver_name="Carlos García",
            driver_phone="+54 11 2222-3333",
            vehicle_type=VehicleType.MOTO,
            license_plate="ABC123",
            current_location=Coordinates(lat=-34.605, lon=-58.380),
            max_capacity=6,
            current_load=2,
            current_orders=["PED-010", "PED-011"],
            success_rate=0.95,
            total_deliveries=150
        ),
        Vehicle(
            id="MOV-002",
            driver_name="María López",
            driver_phone="+54 11 3333-4444",
            vehicle_type=VehicleType.AUTO,
            license_plate="XYZ789",
            current_location=Coordinates(lat=-34.610, lon=-58.375),
            max_capacity=8,
            current_load=1,
            current_orders=["PED-012"],
            success_rate=0.88,
            total_deliveries=80
        ),
        Vehicle(
            id="MOV-003",
            driver_name="Pedro Martínez",
            driver_phone="+54 11 4444-5555",
            vehicle_type=VehicleType.MOTO,
            license_plate="DEF456",
            current_location=Coordinates(lat=-34.600, lon=-58.385),
            max_capacity=6,
            current_load=5,
            current_orders=["PED-013", "PED-014", "PED-015", "PED-016", "PED-017"],
            success_rate=0.92,
            total_deliveries=200
        )
    ]
    
    logger.info(f"✓ Flota creada: {len(vehicles)} vehículos")
    for v in vehicles:
        logger.info(
            f"  - {v.id}: {v.driver_name} ({v.vehicle_type.value}) - "
            f"Carga: {v.current_load}/{v.max_capacity}"
        )
    
    # ========================================================================
    # 5. EVALUAR Y ASIGNAR
    # ========================================================================
    
    logger.info("\n🎯 5. Evaluando vehículos y asignando pedido...")
    
    route_calculator = RouteCalculator()
    scoring_engine = ScoringEngine(config, route_calculator)
    
    # Rankear todos los vehículos
    ranked_vehicles = scoring_engine.rank_vehicles(vehicles, order)
    
    logger.info(f"✓ Evaluación completada. Rankings:")
    for i, (vehicle, score) in enumerate(ranked_vehicles, 1):
        logger.info(
            f"  {i}. {vehicle.id}: Score {score.total_score:.3f} "
            f"(dist={score.distance_to_delivery_km:.1f}km, "
            f"cap={score.available_capacity}, "
            f"on_time={score.will_arrive_on_time})"
        )
    
    # Encontrar mejor vehículo
    result = scoring_engine.find_best_vehicle(vehicles, order)
    
    if result:
        best_vehicle, best_score = result
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 ASIGNACIÓN EXITOSA")
        logger.info("=" * 70)
        logger.info(f"Pedido: {order.id}")
        logger.info(f"Asignado a: {best_vehicle.id} ({best_vehicle.driver_name})")
        logger.info(f"Confianza: {best_score.total_score:.1%}")
        logger.info(f"Distancia: {best_score.distance_to_delivery_km:.2f} km")
        logger.info(f"Llegará a tiempo: {'SÍ' if best_score.will_arrive_on_time else 'NO'}")
        logger.info(f"Tiempo estimado: {best_score.estimated_arrival_time.strftime('%H:%M')}")
        
        logger.info("\n📊 Desglose del score:")
        logger.info(f"  - Distancia: {best_score.distance_score:.3f}")
        logger.info(f"  - Capacidad: {best_score.capacity_score:.3f}")
        logger.info(f"  - Urgencia temporal: {best_score.time_urgency_score:.3f}")
        logger.info(f"  - Compatibilidad de ruta: {best_score.route_compatibility_score:.3f}")
        logger.info(f"  - Desempeño: {best_score.vehicle_performance_score:.3f}")
        
        logger.info("\n💡 Razones de la decisión:")
        for reason in best_score.reasoning:
            logger.info(f"  {reason}")
        
    else:
        logger.error("\n❌ NO SE PUDO ASIGNAR EL PEDIDO")
        logger.error("No hay vehículos disponibles o adecuados")
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ EJEMPLO COMPLETADO")
    logger.info("=" * 70)


if __name__ == "__main__":
    # Configurar logger
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>",
        level="INFO"
    )
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n👋 Programa interrumpido por el usuario")
    except Exception as e:
        logger.error(f"\n\n❌ Error: {e}", exc_info=True)
