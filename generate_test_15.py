"""
Genera JSON de prueba: 15 pedidos pendientes + 6 vehículos con 3-4 pedidos asignados
"""
import json
import random

# Datos realistas
nombres = ['Carlos', 'Ana', 'Jorge', 'Patricia', 'Miguel', 'Lucía', 'Pedro', 'María', 'Diego', 'Sofía',
           'Fernando', 'Carmen', 'Roberto', 'Elena', 'Andrés', 'Valentina', 'Gabriel', 'Isabella']
apellidos = ['Martínez', 'Rodríguez', 'Silva', 'Morales', 'Herrera', 'García', 'López', 'Fernández', 
             'González', 'Pérez', 'Sánchez', 'Ramírez', 'Torres', 'Flores']

# Calles reales de Montevideo
calles = [
    'Mercedes', 'Constituyente', 'Colonia', 'Av. Italia', 'Bvar. Artigas', 'Rivera',
    'Luis Alberto de Herrera', '18 de Julio', 'José Belloni', 'Av. Brasil', 'Bulevar España',
    'Av. 8 de Octubre', 'Rambla República de México', 'Av. Millán', 'Comercio', 'Ejido',
    'Paraguay', 'Soriano', 'San José', 'Yaguarón', 'Canelones', 'Cerrito', 'Colón'
]

# Productos con pesos realistas
productos = [
    ('Notebook HP', 2.5), ('Monitor 24"', 6.0), ('Teclado', 0.8), ('Mouse', 0.2),
    ('Impresora', 7.5), ('Router WiFi', 0.6), ('Tablet', 0.5), ('Auriculares', 0.3),
    ('Webcam', 0.4), ('Hub USB', 0.2), ('Disco SSD', 0.15), ('Cable HDMI', 0.1)
]

def random_location():
    """Coordenadas aleatorias en Montevideo"""
    lat = round(random.uniform(-34.91, -34.89), 6)
    lon = round(random.uniform(-56.20, -56.15), 6)
    calle = random.choice(calles)
    num = random.randint(100, 4000)
    return {'lat': lat, 'lon': lon, 'address': f'{calle} {num}, Montevideo'}

def random_items():
    """Items aleatorios para pedido"""
    num_items = random.randint(1, 3)
    items = []
    for _ in range(num_items):
        prod = random.choice(productos)
        items.append({
            'name': prod[0],
            'quantity': random.randint(1, 2),
            'weight_kg': prod[1]
        })
    return items

def create_order(order_id, is_assigned=False):
    """Crea un pedido"""
    loc = random_location()
    hora = random.randint(16, 19)
    minuto = random.choice([0, 15, 30, 45])
    priority = random.choice(['urgent', 'high', 'medium', 'low'])
    
    order = {
        'id': order_id,
        'customer_name': f"{random.choice(nombres)} {random.choice(apellidos)}",
        'customer_phone': f"+598 9{random.randint(1,9)} {random.randint(100,999)} {random.randint(100,999)}",
        'delivery_address': loc['address'],
        'delivery_location': loc,
        'deadline': f'2025-10-24T{hora:02d}:{minuto:02d}:00',
        'priority': priority,
        'estimated_duration': random.randint(3, 8),
        'items': random_items()
    }
    
    if is_assigned:
        order['status'] = 'assigned'
        order['assigned_at'] = f'2025-10-24T{random.randint(9,13):02d}:{random.randint(0,59):02d}:00'
    
    return order

# Generar 15 pedidos PENDIENTES
print('Generando 15 pedidos pendientes...')
pending_orders = []
for i in range(1, 16):
    pending_orders.append(create_order(f'ORD-PEND-{i:03d}'))

# Generar 6 vehículos con 3-4 pedidos cada uno
print('Generando 6 vehículos con pedidos asignados...')
vehicles = []
vehicle_configs = [
    ('MOTO-001', 'moto', 6, 30, 3),
    ('AUTO-002', 'auto', 8, 150, 4),
    ('MOTO-003', 'moto', 6, 30, 3),
    ('CAMIONETA-004', 'camioneta', 10, 500, 4),
    ('AUTO-005', 'auto', 8, 150, 3),
    ('MOTO-006', 'moto', 6, 30, 4)
]

assigned_order_counter = 1
for vid, vtype, capacity, max_weight, num_orders in vehicle_configs:
    # Crear pedidos asignados a este vehículo
    vehicle_orders = []
    for _ in range(num_orders):
        vehicle_orders.append(create_order(f'ORD-ASIG-{assigned_order_counter:03d}', is_assigned=True))
        assigned_order_counter += 1
    
    # Calcular peso y carga actual
    current_load = len(vehicle_orders)
    current_weight = sum(sum(item['weight_kg'] * item['quantity'] for item in order['items']) 
                        for order in vehicle_orders)
    
    vehicle = {
        'id': vid,
        'driver_name': f"{random.choice(nombres)} {random.choice(apellidos)}",
        'driver_phone': f"+598 9{random.randint(1,9)} {random.randint(100,999)} {random.randint(100,999)}",
        'vehicle_type': vtype,
        'license_plate': f"S{random.choice('ABCDEFGH')}{random.choice('ABCDEFGH')}-{random.randint(1000,9999)}",
        'current_location': random_location(),
        'current_orders': vehicle_orders,
        'capacity': capacity,
        'current_load': current_load,
        'max_weight_kg': max_weight,
        'current_weight_kg': round(current_weight, 2),
        'performance_score': round(random.uniform(0.70, 0.96), 2),
        'total_deliveries': random.randint(100, 600),
        'success_rate': round(random.uniform(0.85, 0.98), 2),
        'average_delay_minutes': round(random.uniform(2.0, 10.0), 1)
    }
    vehicles.append(vehicle)

# Construir JSON final
data = {
    'orders': pending_orders,
    'vehicles': vehicles,
    'config': {
        'default_max_capacity': 6,
        'weight_distance': 0.25,
        'weight_capacity': 0.20,
        'weight_time_urgency': 0.25,
        'weight_route_compatibility': 0.10,
        'weight_vehicle_performance': 0.05,
        'weight_interference': 0.15,
        'max_route_time_minutes': 180,
        'service_time_per_delivery_minutes': 5,
        'average_speed_kmh': 25,
        'consider_traffic': True,
        'optimize_route_order': True
    },
    'fast_mode': True,
    'max_candidates_per_order': 3
}

# Guardar
output_file = 'test_batch_15.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'\n✅ JSON generado: {output_file}')
print(f'\n📊 RESUMEN:')
print(f'   📦 Pedidos pendientes: {len(pending_orders)}')
print(f'   🚗 Vehículos: {len(vehicles)}')
print(f'   ✅ Pedidos ya asignados: {assigned_order_counter - 1}')
print(f'   📈 Total pedidos en sistema: {len(pending_orders) + assigned_order_counter - 1}')
print(f'\n🚗 Detalle de vehículos:')
for v in vehicles:
    print(f'   {v["id"]:15s} {v["vehicle_type"]:10s} '
          f'carga={v["current_load"]}/{v["capacity"]} '
          f'peso={v["current_weight_kg"]:.1f}/{v["max_weight_kg"]}kg')
print(f'\n🔥 Para probar:')
print(f'   Invoke-RestMethod -Uri "http://localhost:8080/api/v1/assign-orders-batch" \\')
print(f'                     -Method POST -ContentType "application/json" \\')
print(f'                     -InFile "{output_file}"')
