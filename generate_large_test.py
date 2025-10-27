"""
Genera un JSON de prueba masivo para test de stress del sistema de ruteo:
- 100 vehículos
- 200-300 pedidos ya asignados (distribuidos)
- 100 pedidos pendientes para asignar
"""
import json
import random
from datetime import datetime, timedelta

# ============= CONFIGURACIÓN =============
NUM_VEHICLES = 100
NUM_PENDING_ORDERS = 100
NUM_ASSIGNED_ORDERS = 250  # distribuidos en los vehículos

# ============= DATOS REALISTAS =============
first_names = ['Carlos', 'Ana', 'Jorge', 'Patricia', 'Miguel', 'Lucía', 'Pedro', 'María', 'Diego', 'Sofía',
               'Fernando', 'Carmen', 'Roberto', 'Elena', 'Andrés', 'Valentina', 'Gabriel', 'Isabella', 'Mateo', 'Camila',
               'Santiago', 'Martina', 'Nicolás', 'Victoria', 'Lucas', 'Emilia', 'Sebastián', 'Renata', 'Joaquín', 'Catalina']

last_names = ['Martínez', 'Rodríguez', 'Silva', 'Morales', 'Herrera', 'García', 'López', 'Fernández', 'González', 'Pérez',
              'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Rivera', 'Gómez', 'Díaz', 'Cruz', 'Reyes', 'Ortiz',
              'Castro', 'Vargas', 'Mendoza', 'Rojas', 'Medina', 'Suárez', 'Acosta', 'Núñez', 'Vega', 'Cabrera']

streets = ['Mercedes', 'Constituyente', 'Colonia', 'Av. Italia', 'Bvar. Artigas', 'Rivera', 'Luis Alberto de Herrera',
           '18 de Julio', 'José Belloni', 'Av. Brasil', 'Bulevar España', 'Av. 8 de Octubre', 'Rambla República de México',
           'Av. Millán', 'Comercio', 'Ejido', 'Paraguay', 'Soriano', 'San José', 'Yaguarón', 'Bvar. Batlle y Ordóñez',
           'Av. Agraciada', 'Bvar. General Artigas', 'Av. Libertador', 'Jackson', 'Yi', 'Canelones', 'Gaboto', 
           'Guayabo', 'Durazno', 'Maldonado', 'Treinta y Tres', 'Florida', 'Cerrito', 'Río Negro', 'Paysandú']

products = [
    ('Laptop HP', 2.2, 5), ('Monitor Samsung 27"', 5.5, 6), ('Teclado mecánico', 1.0, 3),
    ('Mouse gaming', 0.3, 2), ('Impresora Epson', 8.5, 7), ('Cable HDMI', 0.2, 1),
    ('Router WiFi', 0.8, 4), ('Disco SSD 1TB', 0.15, 5), ('Webcam Logitech', 0.4, 3),
    ('Parlantes', 1.2, 4), ('Tablet Samsung', 0.5, 5), ('Auriculares', 0.3, 3),
    ('Cargador portátil', 0.4, 3), ('Hub USB', 0.2, 2), ('Micrófono', 0.6, 4),
    ('Silla gamer', 18.0, 10), ('Escritorio', 25.0, 15), ('Lámpara LED', 1.5, 4),
    ('Soporte monitor', 2.0, 5), ('Alfombrilla XXL', 0.8, 3), ('Teclado inalámbrico', 0.6, 3),
    ('Mouse pad', 0.4, 2), ('Adaptador USB-C', 0.1, 2), ('Base refrigerante laptop', 1.8, 5),
    ('Memoria USB 64GB', 0.05, 2), ('Disco externo 2TB', 0.3, 4), ('Switch ethernet', 0.5, 3),
    ('Cámara IP', 0.4, 4), ('Fuente alimentación', 1.2, 4), ('Gabinete PC', 6.5, 8)
]

vehicle_types_config = {
    'moto': {'capacity': 6, 'max_weight': 30, 'proportion': 0.40},  # 40%
    'auto': {'capacity': 8, 'max_weight': 150, 'proportion': 0.35},  # 35%
    'camioneta': {'capacity': 10, 'max_weight': 500, 'proportion': 0.25}  # 25%
}

# ============= FUNCIONES HELPER =============
def random_montevideo_location():
    """Genera coordenadas aleatorias en Montevideo"""
    lat = round(random.uniform(-34.92, -34.88), 6)
    lon = round(random.uniform(-56.22, -56.14), 6)
    street = random.choice(streets)
    number = random.randint(100, 5000)
    return {
        'lat': lat,
        'lon': lon,
        'address': f'{street} {number}, Montevideo'
    }

def random_items(max_items=3, max_weight=None):
    """Genera items aleatorios para un pedido"""
    num_items = random.randint(1, max_items)
    items = []
    total_weight = 0
    
    for _ in range(num_items):
        # Filtrar productos que no excedan peso máximo
        available_products = products if max_weight is None else [p for p in products if p[1] <= max_weight]
        if not available_products:
            break
            
        product = random.choice(available_products)
        quantity = random.randint(1, 2)
        items.append({
            'name': product[0],
            'quantity': quantity,
            'weight_kg': product[1]
        })
        total_weight += product[1] * quantity
        
        if max_weight and total_weight >= max_weight * 0.8:  # No exceder 80% del máximo
            break
    
    return items

def random_deadline(base_hour=17):
    """Genera deadline aleatorio"""
    hour = random.randint(base_hour, 20)
    minute = random.choice([0, 15, 30, 45])
    return f'2025-10-24T{hour:02d}:{minute:02d}:00'

def random_priority():
    """Genera prioridad aleatoria con distribución realista"""
    return random.choices(['urgent', 'high', 'medium', 'low'], weights=[0.15, 0.30, 0.40, 0.15])[0]

def random_name():
    """Genera nombre completo aleatorio"""
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def random_phone():
    """Genera teléfono uruguayo aleatorio"""
    prefix = random.choice(['91', '92', '93', '94', '95', '96', '97', '98', '99'])
    num1 = random.randint(100, 999)
    num2 = random.randint(100, 999)
    return f"+598 {prefix} {num1} {num2}"

def random_license_plate():
    """Genera matrícula uruguaya aleatoria"""
    letter1 = random.choice('SABCDEFGHIJKLMNOPQRSTUVWXYZ')
    letter2 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    letter3 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    num = random.randint(1000, 9999)
    return f"{letter1}{letter2}{letter3}-{num}"

def create_order(order_id, is_assigned=False):
    """Crea un pedido completo"""
    priority = random_priority()
    location = random_montevideo_location()
    items = random_items(max_items=3)
    
    order = {
        'id': order_id,
        'customer_name': random_name(),
        'customer_phone': random_phone(),
        'delivery_address': location['address'],
        'delivery_location': location,
        'deadline': random_deadline(),
        'priority': priority,
        'estimated_duration': random.randint(3, 10),
        'items': items
    }
    
    # Si es asignado, agregar campos adicionales para tracking
    if is_assigned:
        order['status'] = 'assigned'
        order['assigned_at'] = f'2025-10-24T{random.randint(8, 14):02d}:{random.randint(0, 59):02d}:00'
    
    return order

def create_vehicle(vehicle_id, vehicle_type, assigned_orders=[]):
    """Crea un vehículo completo con sus pedidos asignados"""
    config = vehicle_types_config[vehicle_type]
    
    # Calcular carga actual
    current_load = len(assigned_orders)
    current_weight = sum(sum(item['weight_kg'] * item['quantity'] for item in order['items']) for order in assigned_orders)
    
    # Performance score: mejor para vehículos con más entregas
    total_deliveries = random.randint(50, 800)
    success_rate = round(random.uniform(0.75, 0.98), 2)
    performance_score = round((success_rate + random.uniform(-0.1, 0.1)) * random.uniform(0.85, 1.0), 2)
    performance_score = max(0.60, min(0.99, performance_score))  # Clamp entre 0.60 y 0.99
    
    average_delay = round(random.uniform(1.0, 15.0), 1)
    
    return {
        'id': vehicle_id,
        'driver_name': random_name(),
        'driver_phone': random_phone(),
        'vehicle_type': vehicle_type,
        'license_plate': random_license_plate(),
        'current_location': random_montevideo_location(),
        'current_orders': assigned_orders,
        'capacity': config['capacity'],
        'current_load': current_load,
        'max_weight_kg': config['max_weight'],
        'current_weight_kg': round(current_weight, 2),
        'performance_score': performance_score,
        'total_deliveries': total_deliveries,
        'success_rate': success_rate,
        'average_delay_minutes': average_delay
    }

# ============= GENERACIÓN PRINCIPAL =============
print('🚀 Generando JSON de prueba masivo...')
print(f'   📦 {NUM_PENDING_ORDERS} pedidos pendientes')
print(f'   ✅ {NUM_ASSIGNED_ORDERS} pedidos ya asignados')
print(f'   🚗 {NUM_VEHICLES} vehículos')
print()

# 1. Generar pedidos PENDIENTES (sin asignar)
print('Parte 1/4: Generando pedidos pendientes...')
pending_orders = []
for i in range(1, NUM_PENDING_ORDERS + 1):
    order_id = f'ORD-PEND-{i:03d}'
    pending_orders.append(create_order(order_id, is_assigned=False))

print(f'   ✓ {len(pending_orders)} pedidos pendientes creados')

# 2. Generar pedidos ASIGNADOS
print('Parte 2/4: Generando pedidos asignados...')
assigned_orders_pool = []
for i in range(1, NUM_ASSIGNED_ORDERS + 1):
    order_id = f'ORD-ASIG-{i:03d}'
    assigned_orders_pool.append(create_order(order_id, is_assigned=True))

print(f'   ✓ {len(assigned_orders_pool)} pedidos asignados creados')

# 3. Distribuir tipos de vehículos
print('Parte 3/4: Generando vehículos...')
vehicle_types = []
for vtype, config in vehicle_types_config.items():
    count = int(NUM_VEHICLES * config['proportion'])
    vehicle_types.extend([vtype] * count)

# Ajustar si no suma exactamente NUM_VEHICLES
while len(vehicle_types) < NUM_VEHICLES:
    vehicle_types.append(random.choice(['moto', 'auto', 'camioneta']))

random.shuffle(vehicle_types)

# 4. Crear vehículos y distribuir pedidos asignados
vehicles = []
orders_distribution = []  # Para distribuir los pedidos asignados

# Distribuir pedidos: algunos vehículos con muchos, otros con pocos
for i in range(NUM_VEHICLES):
    # Distribución realista: 
    # - 20% vacíos (0 pedidos)
    # - 30% con 1-2 pedidos
    # - 30% con 3-4 pedidos
    # - 15% con 5-6 pedidos
    # - 5% con 7-9 pedidos
    rand = random.random()
    if rand < 0.20:
        num_orders = 0
    elif rand < 0.50:
        num_orders = random.randint(1, 2)
    elif rand < 0.80:
        num_orders = random.randint(3, 4)
    elif rand < 0.95:
        num_orders = random.randint(5, 6)
    else:
        num_orders = random.randint(7, 9)
    
    orders_distribution.append(num_orders)

# Ajustar para que sume exactamente NUM_ASSIGNED_ORDERS
total_assigned = sum(orders_distribution)
diff = NUM_ASSIGNED_ORDERS - total_assigned
if diff > 0:
    # Agregar pedidos a vehículos aleatorios
    for _ in range(diff):
        idx = random.randint(0, NUM_VEHICLES - 1)
        orders_distribution[idx] += 1
elif diff < 0:
    # Quitar pedidos de vehículos con más carga
    for _ in range(abs(diff)):
        idx = orders_distribution.index(max(orders_distribution))
        if orders_distribution[idx] > 0:
            orders_distribution[idx] -= 1

# Crear vehículos con pedidos asignados
assigned_orders_index = 0
for i in range(NUM_VEHICLES):
    vehicle_type = vehicle_types[i]
    vehicle_id = f'{vehicle_type.upper()}-{i+1:03d}'
    
    # Asignar pedidos a este vehículo
    num_orders_for_vehicle = orders_distribution[i]
    vehicle_orders = []
    
    for _ in range(num_orders_for_vehicle):
        if assigned_orders_index < len(assigned_orders_pool):
            vehicle_orders.append(assigned_orders_pool[assigned_orders_index])
            assigned_orders_index += 1
    
    vehicle = create_vehicle(vehicle_id, vehicle_type, vehicle_orders)
    vehicles.append(vehicle)
    
    if (i + 1) % 20 == 0:
        print(f'   ... {i+1}/{NUM_VEHICLES} vehículos creados')

print(f'   ✓ {len(vehicles)} vehículos creados')
print(f'   ✓ {assigned_orders_index} pedidos asignados distribuidos')

# 5. Construir estructura final
print('Parte 4/4: Ensamblando JSON final...')
data = {
    'orders': pending_orders,  # Solo los pendientes
    'vehicles': vehicles,  # Con sus pedidos asignados incluidos
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

# 6. Guardar JSON
output_file = 'test_batch_large.json'
print(f'Guardando en {output_file}...')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print()
print('✅ JSON generado exitosamente!')
print()
print('📊 RESUMEN:')
print(f'   📦 Pedidos pendientes: {len(pending_orders)}')
print(f'   🚗 Vehículos: {len(vehicles)}')
print(f'   ✅ Pedidos ya asignados: {assigned_orders_index}')
print()
print('📁 Tipos de vehículos:')
type_counts = {}
for v in vehicles:
    vtype = v['vehicle_type']
    type_counts[vtype] = type_counts.get(vtype, 0) + 1
print(f'   🏍️  Motos: {type_counts.get("moto", 0)}')
print(f'   🚗 Autos: {type_counts.get("auto", 0)}')
print(f'   🚚 Camionetas: {type_counts.get("camioneta", 0)}')
print()
print('📊 Distribución de carga:')
empty = sum(1 for v in vehicles if v['current_load'] == 0)
light = sum(1 for v in vehicles if 1 <= v['current_load'] <= 2)
medium = sum(1 for v in vehicles if 3 <= v['current_load'] <= 4)
heavy = sum(1 for v in vehicles if 5 <= v['current_load'] <= 6)
very_heavy = sum(1 for v in vehicles if v['current_load'] >= 7)
print(f'   ⚪ Vacíos (0): {empty}')
print(f'   🟢 Ligeros (1-2): {light}')
print(f'   🟡 Medios (3-4): {medium}')
print(f'   🟠 Pesados (5-6): {heavy}')
print(f'   🔴 Muy pesados (7+): {very_heavy}')
print()
print(f'💾 Tamaño del archivo: ~{len(json.dumps(data)) / 1024:.1f} KB')
print()
print('🚀 Listo para probar con:')
print(f'   Invoke-RestMethod -Uri "http://localhost:8080/api/v1/assign-orders-batch" -Method POST -ContentType "application/json" -InFile "{output_file}"')
