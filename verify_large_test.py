import json

data = json.load(open('test_batch_large.json', 'r', encoding='utf-8'))

print(f'📦 Pedidos pendientes: {len(data["orders"])}')
print(f'🚗 Vehículos: {len(data["vehicles"])}')

total_assigned = sum(len(v["current_orders"]) for v in data['vehicles'])
print(f'✅ Pedidos asignados: {total_assigned}')
print(f'⚡ Fast mode: {data["fast_mode"]}')
print(f'🎯 Max candidates: {data["max_candidates_per_order"]}')
print()

print('🏆 TOP 5 vehículos con más carga:')
sorted_vehicles = sorted(data['vehicles'], key=lambda v: v['current_load'], reverse=True)
for v in sorted_vehicles[:5]:
    print(f'  {v["id"]:15s} {v["vehicle_type"]:10s} carga={v["current_load"]}/{v["capacity"]} peso={v["current_weight_kg"]:.1f}/{v["max_weight_kg"]}kg perf={v["performance_score"]}')

print()
print('📊 Estadísticas de pedidos pendientes:')
priorities = {}
for order in data['orders']:
    p = order['priority']
    priorities[p] = priorities.get(p, 0) + 1

for priority in ['urgent', 'high', 'medium', 'low']:
    count = priorities.get(priority, 0)
    pct = count / len(data['orders']) * 100
    print(f'  {priority:8s}: {count:3d} ({pct:5.1f}%)')

print()
print(f'💾 Tamaño archivo: {len(json.dumps(data)) / 1024:.1f} KB')
print()
print('✅ El JSON está listo para prueba de estrés!')
print()
print('🔥 Para ejecutar el test:')
print('   Invoke-RestMethod -Uri "http://localhost:8080/api/v1/assign-orders-batch" `')
print('                     -Method POST `')
print('                     -ContentType "application/json" `')
print('                     -InFile "test_batch_large.json"')
