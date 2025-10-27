#!/usr/bin/env python3
"""
Generador de datos de prueba para el sistema de ruteo optimizado.
Crea un test con:
- 20 pedidos pendientes para asignar
- 12 vehículos (5 motos, 4 autos, 3 camionetas)
- 30 pedidos ya asignados distribuidos entre los 12 vehículos
"""

import json
import random
from datetime import datetime, timedelta

# Direcciones reales de Montevideo para hacer el test más realista
ADDRESSES_MVD = [
    ("18 de Julio 1234", -34.9034, -56.1883),
    ("Av. Italia 2545", -34.8892, -56.1546),
    ("Bvar. Artigas 1876", -34.8967, -56.1698),
    ("Colón 1523", -34.9012, -56.1734),
    ("Mercedes 1789", -34.9045, -56.1623),
    ("San José 2456", -34.8978, -56.1812),
    ("Av. 8 de Octubre 3123", -34.8856, -56.1589),
    ("Rivera 2876", -34.8923, -56.1645),
    ("Canelones 2234", -34.9067, -56.1778),
    ("Soriano 1654", -34.9001, -56.1867),
    ("Constituyente 1987", -34.8945, -56.1712),
    ("Comercio 1456", -34.8989, -56.1834),
    ("Yaguarón 1876", -34.9023, -56.1923),
    ("José Belloni 2345", -34.8912, -56.1567),
    ("Av. Brasil 2678", -34.8934, -56.1789),
    ("Av. Millán 1987", -34.9012, -56.1698),
    ("Rambla República de México 2456", -34.9078, -56.1534),
    ("Colonia 1234", -34.8956, -56.1812),
    ("Ejido 876", -34.8923, -56.1889),
    ("Bvar. España 2123", -34.9089, -56.1656),
    ("Paraguay 1654", -34.9034, -56.1745),
    ("Guayabo 1987", -34.8967, -56.1678),
    ("Galicia 2345", -34.8945, -56.1823),
    ("Arenal Grande 1765", -34.9001, -56.1756),
    ("Cuareim 2098", -34.8978, -56.1867),
    ("Jackson 1432", -34.9023, -56.1634),
    ("Paysandú 1876", -34.8912, -56.1789),
    ("Maldonado 2234", -34.8989, -56.1712),
    ("Andes 1567", -34.9056, -56.1845),
    ("Minas 2098", -34.8934, -56.1698),
]

# Productos con pesos realistas
PRODUCTS = [
    ("Notebook HP", 2.5),
    ("Monitor 24\"", 6.0),
    ("Teclado", 0.8),
    ("Mouse", 0.2),
    ("Impresora", 7.5),
    ("Router WiFi", 0.6),
    ("Disco SSD", 0.15),
    ("Webcam", 0.4),
    ("Auriculares", 0.3),
    ("Hub USB", 0.2),
    ("Cable HDMI", 0.1),
    ("Tablet", 0.5),
]

PRIORITIES = ["urgent", "high", "medium", "low"]
NAMES = ["Juan", "María", "Carlos", "Ana", "Pedro", "Lucía", "Diego", "Sofía", "Fernando", "Isabella", 
         "Roberto", "Carmen", "Gabriel", "Valentina", "Andrés", "Patricia", "Miguel", "Elena", "Jorge", "Laura"]
SURNAMES = ["García", "Rodríguez", "González", "Fernández", "López", "Martínez", "Sánchez", "Pérez", "Romero", 
            "Torres", "Flores", "Silva", "Morales", "Herrera", "Ramírez"]

def random_phone():
    """Genera un número de teléfono uruguayo aleatorio"""
    return f"+598 9{random.randint(1, 9)} {random.randint(100, 999)} {random.randint(100, 999)}"

def random_plate():
    """Genera una matrícula uruguaya aleatoria"""
    letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
    numbers = random.randint(1000, 9999)
    return f"S{letters[0]}{letters[1]}-{numbers}"

def generate_order_items():
    """Genera 1-3 items para un pedido con pesos realistas"""
    num_items = random.randint(1, 3)
    items = []
    total_weight = 0
    
    for _ in range(num_items):
        product, weight = random.choice(PRODUCTS)
        quantity = random.randint(1, 2)
        items.append({
            "name": product,
            "quantity": quantity,
            "weight_kg": weight
        })
        total_weight += weight * quantity
    
    return items, total_weight

def generate_pending_orders(count=20):
    """Genera pedidos pendientes para asignar"""
    orders = []
    base_time = datetime.now()
    
    for i in range(count):
        address, lat, lon = random.choice(ADDRESSES_MVD)
        items, total_weight = generate_order_items()
        
        # Deadline entre 1-6 horas desde ahora
        deadline = base_time + timedelta(hours=random.randint(1, 6), minutes=random.randint(0, 45))
        
        order = {
            "id": f"ORD-PEND-{i+1:03d}",
            "customer_name": f"{random.choice(NAMES)} {random.choice(SURNAMES)}",
            "customer_phone": random_phone(),
            "delivery_address": f"{address}, Montevideo",
            "delivery_location": {
                "lat": lat + random.uniform(-0.003, 0.003),
                "lon": lon + random.uniform(-0.003, 0.003),
                "address": f"{address}, Montevideo"
            },
            "deadline": deadline.strftime("%Y-%m-%dT%H:%M:%S"),
            "priority": random.choice(PRIORITIES),
            "estimated_duration": random.randint(3, 8),
            "items": items
        }
        orders.append(order)
    
    return orders

def generate_vehicles_with_orders(num_vehicles=12, num_assigned_orders=30):
    """Genera vehículos con pedidos ya asignados"""
    vehicles = []
    
    # Distribución: 5 motos, 4 autos, 3 camionetas
    vehicle_configs = [
        ("moto", 6, 30.0, 5),      # 5 motos
        ("auto", 8, 150.0, 4),     # 4 autos
        ("camioneta", 10, 500.0, 3) # 3 camionetas
    ]
    
    vehicle_id = 1
    all_vehicles = []
    
    for vehicle_type, capacity, max_weight, count in vehicle_configs:
        for i in range(count):
            vehicle = {
                "id": f"{vehicle_type.upper()}-{vehicle_id:03d}",
                "driver_name": f"{random.choice(NAMES)} {random.choice(SURNAMES)}",
                "driver_phone": random_phone(),
                "vehicle_type": vehicle_type,
                "license_plate": random_plate(),
                "current_location": None,  # Se asignará después
                "current_orders": [],
                "capacity": capacity,
                "current_load": 0,
                "max_weight_kg": max_weight,
                "current_weight_kg": 0.0,
                "performance_score": round(random.uniform(0.70, 0.95), 2),
                "total_deliveries": random.randint(100, 600),
                "success_rate": round(random.uniform(0.85, 0.99), 2),
                "average_delay_minutes": round(random.uniform(3.0, 12.0), 1)
            }
            all_vehicles.append(vehicle)
            vehicle_id += 1
    
    # Distribuir los 30 pedidos asignados entre los 12 vehículos
    # Asegurar que ningún vehículo exceda su capacidad ni peso
    orders_per_vehicle = [0] * num_vehicles
    
    # Distribuir pedidos de forma realista (2-3 pedidos por vehículo en promedio)
    remaining_orders = num_assigned_orders
    for i in range(num_vehicles):
        if remaining_orders > 0:
            # Dar entre 1 y 4 pedidos por vehículo
            max_orders = min(all_vehicles[i]["capacity"] - 1, remaining_orders, 4)  # Dejar espacio
            num_orders = random.randint(1, max_orders) if max_orders > 0 else 0
            orders_per_vehicle[i] = num_orders
            remaining_orders -= num_orders
    
    # Distribuir pedidos restantes
    while remaining_orders > 0:
        vehicle_idx = random.randint(0, num_vehicles - 1)
        if orders_per_vehicle[vehicle_idx] < all_vehicles[vehicle_idx]["capacity"] - 1:
            orders_per_vehicle[vehicle_idx] += 1
            remaining_orders -= 1
    
    # Generar pedidos asignados para cada vehículo
    order_id = 1
    base_time = datetime.now()
    
    for vehicle_idx, vehicle in enumerate(all_vehicles):
        num_orders = orders_per_vehicle[vehicle_idx]
        total_weight = 0.0
        
        for _ in range(num_orders):
            address, lat, lon = random.choice(ADDRESSES_MVD)
            
            # Generar items que respeten el límite de peso
            max_order_weight = vehicle["max_weight_kg"] * 0.25  # Max 25% del peso total por pedido
            items = []
            order_weight = 0.0
            
            # Generar items cuidadosamente
            num_items = random.randint(1, 2)
            for _ in range(num_items):
                product, weight = random.choice(PRODUCTS)
                quantity = 1
                item_weight = weight * quantity
                
                # Solo agregar si no excede límites
                if total_weight + order_weight + item_weight <= vehicle["max_weight_kg"] * 0.85:  # Max 85% capacidad
                    items.append({
                        "name": product,
                        "quantity": quantity,
                        "weight_kg": weight
                    })
                    order_weight += item_weight
            
            if items:  # Solo agregar si tiene items
                deadline = base_time + timedelta(hours=random.randint(4, 10), minutes=random.randint(0, 45))
                assigned_at = base_time - timedelta(hours=random.randint(1, 4), minutes=random.randint(0, 55))
                
                order = {
                    "id": f"ORD-ASIG-{order_id:03d}",
                    "customer_name": f"{random.choice(NAMES)} {random.choice(SURNAMES)}",
                    "customer_phone": random_phone(),
                    "delivery_address": f"{address}, Montevideo",
                    "delivery_location": {
                        "lat": lat + random.uniform(-0.003, 0.003),
                        "lon": lon + random.uniform(-0.003, 0.003),
                        "address": f"{address}, Montevideo"
                    },
                    "deadline": deadline.strftime("%Y-%m-%dT%H:%M:%S"),
                    "priority": random.choice(PRIORITIES),
                    "estimated_duration": random.randint(3, 8),
                    "items": items,
                    "status": "assigned",
                    "assigned_at": assigned_at.strftime("%Y-%m-%dT%H:%M:%S")
                }
                
                vehicle["current_orders"].append(order)
                total_weight += order_weight
                order_id += 1
        
        # Actualizar peso y carga del vehículo
        vehicle["current_load"] = len(vehicle["current_orders"])
        vehicle["current_weight_kg"] = round(total_weight, 1)
        
        # Ubicación actual = última dirección de entrega o dirección aleatoria
        if vehicle["current_orders"]:
            last_order = vehicle["current_orders"][-1]
            vehicle["current_location"] = last_order["delivery_location"]
        else:
            address, lat, lon = random.choice(ADDRESSES_MVD)
            vehicle["current_location"] = {
                "lat": lat,
                "lon": lon,
                "address": f"{address}, Montevideo"
            }
    
    return all_vehicles

def generate_test_data():
    """Genera el dataset completo de prueba"""
    print("🔧 Generando datos de prueba...")
    print("   - 20 pedidos pendientes")
    print("   - 12 vehículos (5 motos, 4 autos, 3 camionetas)")
    print("   - 30 pedidos asignados")
    print()
    
    pending_orders = generate_pending_orders(20)
    vehicles = generate_vehicles_with_orders(12, 30)
    
    # Verificar distribución
    total_assigned = sum(len(v["current_orders"]) for v in vehicles)
    print(f"✅ Generados {len(pending_orders)} pedidos pendientes")
    print(f"✅ Generados {len(vehicles)} vehículos con {total_assigned} pedidos asignados")
    print()
    
    # Mostrar distribución de carga
    print("📊 Distribución de carga por vehículo:")
    for v in vehicles:
        load_pct = (v["current_load"] / v["capacity"]) * 100
        weight_pct = (v["current_weight_kg"] / v["max_weight_kg"]) * 100
        status = "⚠️ LLENO" if v["current_load"] >= v["capacity"] else "✓"
        weight_status = "⚠️ SOBREPESO" if v["current_weight_kg"] > v["max_weight_kg"] else "✓"
        print(f"   {v['id']:15} {v['current_load']}/{v['capacity']} pedidos ({load_pct:5.1f}%) {status}  |  "
              f"{v['current_weight_kg']:6.1f}/{v['max_weight_kg']:6.1f}kg ({weight_pct:5.1f}%) {weight_status}")
    
    data = {
        "orders": pending_orders,
        "vehicles": vehicles,
        "config": {
            "default_max_capacity": 6,
            "weight_distance": 0.25,
            "weight_capacity": 0.2,
            "weight_time_urgency": 0.25,
            "weight_route_compatibility": 0.1,
            "weight_vehicle_performance": 0.05,
            "weight_interference": 0.15,
            "max_route_time_minutes": 180,
            "service_time_per_delivery_minutes": 5,
            "average_speed_kmh": 25,
            "consider_traffic": True,
            "optimize_route_order": True
        },
        "fast_mode": True,
        "max_candidates_per_order": 3
    }
    
    return data

def main():
    print("=" * 70)
    print("  GENERADOR DE TEST - 20 PEDIDOS × 12 VEHÍCULOS")
    print("=" * 70)
    print()
    
    data = generate_test_data()
    
    output_file = "test_batch_20.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    file_size = len(json.dumps(data, indent=2)) / 1024
    print()
    print(f"✅ Archivo generado: {output_file}")
    print(f"📦 Tamaño: {file_size:.1f} KB")
    print()
    print("🚀 Listo para probar con:")
    print(f"   Invoke-RestMethod -Uri 'http://localhost:8080/api/v1/assign-orders-batch' \\")
    print(f"     -Method POST -ContentType 'application/json' \\")
    print(f"     -InFile '{output_file}'")
    print()

if __name__ == "__main__":
    main()
