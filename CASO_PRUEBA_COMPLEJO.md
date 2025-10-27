# 🔥 CASO DE PRUEBA SUPER COMPLEJO

## 📋 Descripción del Escenario

Este JSON pone a prueba **TODAS** las capacidades avanzadas del sistema de ruteo.

---

## 🎯 El Pedido Nuevo (URGENTE)

**ORD-2025-URGENTE-001**
- 📍 Destino: `Av. Corrientes 3247, Buenos Aires`
- ⏰ Deadline: **18:30** (en 3 horas 30 minutos desde las 15:00)
- 🔴 Prioridad: **URGENTE**
- 📦 Productos: Notebook + Mouse (peso: 2.8kg)
- ⏱️ Duración estimada: **8 minutos** (requiere firma digital)

---

## 🚗 Los Vehículos Disponibles (5 opciones)

### 1. MOTO-001 (Carlos Martínez) ⭐ Top Performer
**Situación actual:**
- 📍 Ubicación: Av. Santa Fe 2100
- 📦 **2 pedidos pendientes** con deadlines APRETADOS:
  - ORD-100: Deadline **17:45** (2h 45min)
  - ORD-101: Deadline **18:15** (3h 15min)
- 🎯 Performance: **0.92** (Excelente - 487 entregas, 96% éxito)
- 📊 Capacidad: **2/6** (4 espacios libres)
- ⚖️ Peso: 8.5/30 kg

**Desafío:** 
- Tiene el mejor performance
- Está relativamente cerca
- PERO tiene 2 pedidos con deadlines apretados
- ¿Podrá cumplir con los 3 pedidos (los 2 actuales + el nuevo)?

**Predicción:**
- 🟡 **FACTIBILIDAD DUDOSA** - Los deadlines están muy ajustados
- El sistema tendrá que simular la ruta completa
- Si causa atrasos → RECHAZADO automáticamente

---

### 2. AUTO-002 (Ana Rodríguez) ⚠️ Sobrecargada
**Situación actual:**
- 📍 Ubicación: Av. 9 de Julio 1200
- 📦 **3 pedidos pendientes** (¡casi al límite!):
  - ORD-200: Deadline **17:30** 🔴 (MUY URGENTE - solo 2h 30min)
  - ORD-201: Deadline **18:00** 
  - ORD-202: Deadline **18:45**
- 🎯 Performance: **0.88** (Bueno - 312 entregas, 91% éxito)
- 📊 Capacidad: **3/8** (5 espacios libres)
- ⚖️ Peso: 45.2/150 kg

**Desafío:**
- Ya tiene 3 pedidos (carga alta)
- El primer pedido es MUY urgente (17:30)
- Agregar uno más podría causar un efecto dominó de atrasos

**Predicción:**
- 🔴 **ALTA PROBABILIDAD DE RECHAZO** 
- La interferencia será ALTA
- Riesgo de atrasar las 3 entregas actuales

---

### 3. MOTO-003 (Jorge Silva) 💚 Disponible pero Lejos
**Situación actual:**
- 📍 Ubicación: Av. Las Heras 3500 (más lejos)
- 📦 **1 pedido pendiente** (carga baja):
  - ORD-300: Deadline **19:00** (mucho margen)
- 🎯 Performance: **0.75** (Regular - 156 entregas, 82% éxito)
- 📊 Capacidad: **1/6** (5 espacios libres)
- ⚖️ Peso: 3.2/30 kg

**Desafío:**
- Está más LEJOS del punto de entrega
- Performance más bajo que otros
- Pero tiene MUCHO margen en su único pedido

**Predicción:**
- 🟢 **FACTIBLE** - Tiene capacidad y tiempo
- 🟡 **INTERFERENCIA BAJA** - Solo 1 pedido con deadline flexible
- ⚠️ **DISTANCIA PENALIZA** - Está lejos del nuevo pedido

---

### 4. CAMIONETA-004 (Patricia Morales) 🌟 La Experimentada
**Situación actual:**
- 📍 Ubicación: Av. San Juan 2500 (sur de la ciudad)
- 📦 **4 pedidos pendientes** (pero tiene capacidad):
  - ORD-400: Deadline **17:20** 🔴 (MUY APRETADO - 2h 20min)
  - ORD-401: Deadline **17:50**
  - ORD-402: Deadline **18:20**
  - ORD-403: Deadline **19:15**
- 🎯 Performance: **0.95** (EXCELENTE - 624 entregas, 97% éxito, solo 1.8min delay promedio)
- 📊 Capacidad: **4/10** (6 espacios libres)
- ⚖️ Peso: 125.8/500 kg

**Desafío:**
- Es la MEJOR conductora (0.95 performance)
- Pero ya tiene 4 pedidos con deadlines complicados
- Está en el SUR y el nuevo pedido está más al CENTRO/NORTE

**Predicción:**
- 🔴 **PROBABLE RECHAZO** - El primer deadline (17:20) es muy apretado
- Aunque tenga capacidad, agregar otro pedido es arriesgado
- Distancia al nuevo pedido es considerable

---

### 5. AUTO-005 (Miguel Herrera) 🆕 El Novato Sin Carga
**Situación actual:**
- 📍 Ubicación: Av. Cabildo 2800 (noroeste)
- 📦 **SIN pedidos pendientes** (¡totalmente libre!)
- 🎯 Performance: **0.68** (Bajo - solo 89 entregas, 79% éxito, 12.3min delay)
- 📊 Capacidad: **0/8** (8 espacios libres)
- ⚖️ Peso: 0/150 kg

**Desafío:**
- Es el ÚNICO sin carga
- Pero tiene el PEOR performance (nuevo/inexperto)
- Está relativamente lejos (Cabildo 2800)

**Predicción:**
- 🟢 **FACTIBLE** - Sin interferencia (no tiene otros pedidos)
- 🟡 **PERFORMANCE PENALIZA** - Es el menos confiable
- 🟡 **DISTANCIA MODERADA**

---

## 🤖 ¿Qué Debería Decidir el Sistema?

### Análisis Esperado:

#### Paso 1: Verificación de Capacidad
- ✅ Todos tienen capacidad disponible

#### Paso 2: Cálculo de Rutas Reales (OSMnx)
El sistema descargará el grafo de Buenos Aires y calculará:
- Tiempos reales con calles flechadas
- Distancias precisas por red vial
- Velocidad promedio según tipo de vía

#### Paso 3: Simulación de Factibilidad
Para **cada vehículo**, simulará:

**MOTO-001:**
```
15:00 - Posición actual (Av. Santa Fe 2100)
  ↓ [calcular ruta real]
15:XX - ORD-100 (Av. Córdoba 2500)
  ↓ [viaje + 5min servicio + 5min pedido]
15:XX - ORD-101 o ORD-NUEVO? (optimizar)
  ↓ [viaje + 5min servicio + ?min]
15:XX - Tercer pedido
  ↓
Verificar: ¿Todos llegan antes de deadline?
```

**AUTO-002:**
```
15:00 - Posición actual
  ↓
15:XX - ORD-200 (URGENTE 17:30) ← Este es crítico
  ↓
15:XX - ORD-201, ORD-202, ORD-NUEVO
  ↓
¿El primero llega a tiempo con el nuevo agregado?
```

#### Paso 4: Cálculo de Interferencia

**AUTO-005 (sin carga):**
```
Tiempo sin nuevo: 0 min
Tiempo con nuevo: 25 min (estimado)
Interferencia: 0% (¡perfecto!)
Score interferencia: 1.0
```

**MOTO-001 (2 pedidos):**
```
Tiempo sin nuevo: 45 min
Tiempo con nuevo: 68 min
Interferencia: +23 min (51%)
Score interferencia: 0.62
```

**CAMIONETA-004 (4 pedidos):**
```
Tiempo sin nuevo: 78 min
Tiempo con nuevo: 102 min
Interferencia: +24 min
Score interferencia: 0.60
```

#### Paso 5: Score Total

| Vehículo | Distancia | Capacidad | Urgencia | Compat. | Perf. | **Interf.** | **TOTAL** | Factible |
|----------|-----------|-----------|----------|---------|-------|-------------|-----------|----------|
| MOTO-001 | 0.85 | 0.67 | 0.70 | 0.80 | 0.92 | 0.62 | **0.75** | ✅/❌? |
| AUTO-002 | 0.75 | 0.63 | 0.60 | 0.70 | 0.88 | 0.35 | **0.63** | ❌ |
| MOTO-003 | 0.60 | 0.83 | 0.85 | 0.65 | 0.75 | 0.88 | **0.74** | ✅ |
| CAMIONETA-004 | 0.55 | 0.60 | 0.65 | 0.50 | 0.95 | 0.60 | **0.62** | ❌ |
| AUTO-005 | 0.65 | 1.00 | 0.90 | 0.50 | 0.68 | 1.00 | **0.78** | ✅ |

---

## 🎯 Predicción Final

### 🥇 Ganador Esperado: **AUTO-005 (Miguel Herrera)**

**Razones:**
1. ✅ **Interferencia = 0** (no tiene otros pedidos)
2. ✅ **Capacidad total disponible** (8 espacios libres)
3. ✅ **Sin riesgo de atrasos** (no tiene compromisos previos)
4. ⚠️ Performance bajo, pero compensado por otros factores

**Justificación del Sistema:**
```
✓ Ruta factible: Todos los deadlines se cumplen
✓ Baja interferencia: +0min (excelente)
⚠️ Distancia moderada: 8.5km
✓ Excelente capacidad: 8 espacios libres
✓ Llegará a tiempo
🌟 BUENA opción (score: 0.78)
```

### 🥈 Alternativa: **MOTO-003 (Jorge Silva)**

Si AUTO-005 está muy lejos o no es factible, MOTO-003 es la segunda opción:
- Solo 1 pedido con deadline flexible
- Baja interferencia
- Performance aceptable

### ❌ Rechazos Esperados:

**AUTO-002:** 
- ❌ Deadline 17:30 demasiado apretado
- ❌ Alta interferencia con 3 pedidos

**CAMIONETA-004:**
- ❌ Deadline 17:20 imposible de cumplir con el nuevo
- ❌ Distancia considerable

---

## 🧪 Cómo Probarlo

### Opción 1: Swagger UI (Recomendado)

1. Abre: http://localhost:8080/docs
2. Busca el endpoint: `POST /api/v1/assign-order`
3. Clic en "Try it out"
4. Pega el contenido de `test_complejo.json`
5. Clic en "Execute"
6. Analiza la respuesta

### Opción 2: cURL

```bash
curl -X POST "http://localhost:8080/api/v1/assign-order" \
  -H "Content-Type: application/json" \
  -d @test_complejo.json
```

### Opción 3: Python

```python
import requests
import json

with open('test_complejo.json', 'r') as f:
    payload = json.load(f)

response = requests.post(
    'http://localhost:8080/api/v1/assign-order',
    json=payload
)

result = response.json()

print("🎯 VEHÍCULO ASIGNADO:", result.get('assigned_vehicle_id'))
print("📊 SCORE TOTAL:", result.get('assignment_score', {}).get('total_score'))
print("\n📋 RANKING DE VEHÍCULOS:")
for vehicle_score in result.get('all_vehicle_scores', []):
    print(f"  {vehicle_score['vehicle_id']}: {vehicle_score['total_score']:.3f}")
```

---

## 📊 Qué Observar en la Respuesta

### 1. Vehículo Asignado
```json
{
  "assigned_vehicle_id": "AUTO-005",
  "confidence_score": 0.78
}
```

### 2. Scores Individuales
```json
{
  "assignment_score": {
    "total_score": 0.78,
    "distance_score": 0.65,
    "capacity_score": 1.00,
    "time_urgency_score": 0.90,
    "route_compatibility_score": 0.50,
    "vehicle_performance_score": 0.68,
    "interference_score": 1.00  ← ¡NUEVO!
  }
}
```

### 3. Vehículos Rechazados
```json
{
  "vehicle_id": "AUTO-002",
  "total_score": 0.0,
  "reasoning": [
    "❌ RECHAZADO: Agregar este pedido causaría atrasos en entregas existentes",
    "❌ Alta interferencia: +35.0min (problemático)"
  ]
}
```

### 4. Ruta Optimizada
```json
{
  "optimized_route": [
    {
      "order_id": "ORD-2025-URGENTE-001",
      "eta": "2025-10-24T18:15:00",
      "deadline": "2025-10-24T18:30:00",
      "on_time": true
    }
  ]
}
```

---

## 🎓 Lecciones de Este Caso

### 1. Performance NO es todo
- CAMIONETA-004 tiene el mejor performance (0.95)
- Pero NO será elegida porque tiene deadlines muy apretados

### 2. Capacidad disponible importa
- AUTO-005 gana porque está LIBRE
- Sin interferencia = score perfecto en ese criterio

### 3. Protección de compromisos
- El sistema RECHAZARÁ cualquier opción que ponga en riesgo entregas ya prometidas
- Esto es crítico para mantener SLAs

### 4. Optimización real
- No basta con estar cerca
- Hay que simular la ruta COMPLETA
- Considerar tiempos de servicio (5min) en cada stop

---

## 💡 Variantes para Probar

### Variante A: Deadline más ajustado
Cambia el deadline del nuevo pedido a `18:00` en vez de `18:30`
→ Verás cómo más vehículos son rechazados

### Variante B: Todos sin carga
Elimina los `current_orders` de todos los vehículos
→ Verás cómo el performance y distancia se vuelven más importantes

### Variante C: Todos sobrecargados
Agrega más pedidos pendientes a todos
→ Verás cómo el sistema podría rechazar TODOS si no es viable

---

## 🚀 ¡Pruébalo Ahora!

El archivo está listo en: `test_complejo.json`

**Comando rápido:**
```bash
curl -X POST http://localhost:8080/api/v1/assign-order \
  -H "Content-Type: application/json" \
  -d @test_complejo.json | python -m json.tool
```

¡Déjame saber qué resultado obtienes! 🎉
