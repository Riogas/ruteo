# 🎯 CÓMO CALCULAR EL PERFORMANCE SCORE

## ¿Qué es el Performance Score?

Es un número entre **0.0 y 1.0** que representa la calidad histórica del conductor:
- **0.0** = Muy mal desempeño
- **0.5** = Desempeño promedio
- **1.0** = Desempeño excelente

---

## 📊 Ejemplo Práctico de Cálculo

### Conductor: Carlos Rodriguez (VH-001)

#### Datos del último mes:

1. **Entregas a tiempo**: 85 de 100 entregas = 85%
2. **Satisfacción del cliente**: 4.3 de 5 estrellas = 86%
3. **Eficiencia de ruta**: 90% (comparado con ruta óptima)
4. **Calidad de comunicación**: 4.5 de 5 = 90%
5. **Precisión de pedidos**: 95% sin errores
6. **Mantenimiento del vehículo**: 88% (inspecciones pasadas)

#### Cálculo:

```python
performance_score = (
    0.85 * 0.25 +  # Entregas a tiempo (25%)
    0.86 * 0.20 +  # Satisfacción (20%)
    0.90 * 0.20 +  # Eficiencia (20%)
    0.90 * 0.15 +  # Comunicación (15%)
    0.95 * 0.10 +  # Precisión (10%)
    0.88 * 0.10    # Mantenimiento (10%)
)
= 0.2125 + 0.172 + 0.18 + 0.135 + 0.095 + 0.088
= 0.88
```

**Resultado: 0.88** (Conductor excelente)

---

## 🔢 Ejemplos de Diferentes Niveles

### Conductor Excelente (0.90+)
```json
{
  "id": "VH-001",
  "driver_name": "Ana Martínez",
  "performance_score": 0.92,
  "metrics": {
    "on_time_delivery": "95%",
    "customer_rating": "4.8/5",
    "route_efficiency": "93%"
  }
}
```

### Conductor Bueno (0.75-0.89)
```json
{
  "id": "VH-002",
  "driver_name": "Carlos Rodriguez",
  "performance_score": 0.82,
  "metrics": {
    "on_time_delivery": "87%",
    "customer_rating": "4.2/5",
    "route_efficiency": "85%"
  }
}
```

### Conductor Promedio (0.60-0.74)
```json
{
  "id": "VH-003",
  "driver_name": "Jorge López",
  "performance_score": 0.68,
  "metrics": {
    "on_time_delivery": "75%",
    "customer_rating": "3.8/5",
    "route_efficiency": "70%"
  }
}
```

### Conductor Nuevo (Sin historial)
```json
{
  "id": "VH-004",
  "driver_name": "María Fernández",
  "performance_score": 0.70,
  "note": "Valor por defecto para conductores nuevos"
}
```

---

## 💡 Casos de Uso Reales

### Caso 1: Sin Sistema de Métricas
Si **NO** tienes un sistema de métricas, usa estos valores:

```python
# Conductor nuevo o sin historial
performance_score = 0.70

# Conductor conocido como "bueno"
performance_score = 0.80

# Conductor conocido como "excelente"
performance_score = 0.90

# Conductor con problemas de desempeño
performance_score = 0.60
```

### Caso 2: Con Sistema de Entregas Previas
Si tienes una base de datos de entregas:

```python
def calcular_performance_score(driver_id):
    # Consultar últimas 100 entregas del conductor
    entregas = db.query(f"SELECT * FROM entregas WHERE driver_id = {driver_id} LIMIT 100")
    
    # Calcular tasa de entregas a tiempo
    entregas_a_tiempo = sum(1 for e in entregas if e.entregado_antes_de_deadline)
    tasa_puntualidad = entregas_a_tiempo / len(entregas)
    
    # Calcular satisfacción promedio
    ratings = [e.customer_rating for e in entregas if e.customer_rating]
    satisfaccion_promedio = sum(ratings) / len(ratings) / 5.0  # Normalizar a 0-1
    
    # Calcular score final (ponderado)
    performance_score = (tasa_puntualidad * 0.6) + (satisfaccion_promedio * 0.4)
    
    return round(performance_score, 2)
```

### Caso 3: Con Sistema de Calificaciones
Si tienes calificaciones de clientes:

```python
def performance_desde_calificaciones(driver_id):
    # Obtener calificaciones del último mes
    calificaciones = db.query(f"""
        SELECT AVG(rating) as promedio 
        FROM customer_ratings 
        WHERE driver_id = {driver_id}
        AND created_at >= NOW() - INTERVAL 30 DAYS
    """)
    
    # Convertir escala 1-5 a 0-1
    promedio = calificaciones[0]['promedio']
    performance_score = (promedio - 1) / 4  # Normalizar de 1-5 a 0-1
    
    return round(performance_score, 2)
```

---

## 🚀 Integración con el Sistema de Ruteo

### Ejemplo Completo con Cálculo Dinámico

```python
import requests
from datetime import datetime

# 1. Obtener conductores de tu base de datos
conductores = obtener_conductores_disponibles()

# 2. Calcular performance_score para cada uno
vehicles = []
for conductor in conductores:
    # Calcular o recuperar el score
    perf_score = calcular_performance_score(conductor.id)
    
    vehicles.append({
        "id": conductor.vehicle_id,
        "driver_name": conductor.nombre,
        "current_location": {
            "lat": conductor.ultima_lat,
            "lon": conductor.ultima_lon
        },
        "current_orders": obtener_ordenes_activas(conductor.id),
        "capacity": conductor.capacidad_vehiculo,
        "performance_score": perf_score  # ← AQUÍ VA EL SCORE CALCULADO
    })

# 3. Enviar al sistema de ruteo
response = requests.post("http://localhost:8080/assign", json={
    "order": {
        "id": "ORD-2025-001",
        "customer_name": "Cliente Test",
        "delivery_address": "Av. Corrientes 1234, Buenos Aires",
        "deadline": "2025-01-25T18:00:00"
    },
    "available_vehicles": vehicles
})

print(response.json())
```

---

## 📈 Impacto en la Asignación

El `performance_score` representa el **10%** del score total:

```
Score Total = 
    Distancia (30%) +
    Capacidad (20%) +
    Urgencia (25%) +
    Compatibilidad (15%) +
    Performance (10%)  ← AQUÍ
```

### Ejemplo de Impacto:

```
Conductor A: performance_score = 0.95 → contribuye 9.5 puntos
Conductor B: performance_score = 0.65 → contribuye 6.5 puntos

Diferencia: 3 puntos de 100 en el score final
```

Esto significa que **SI** dos conductores están muy cerca en otros factores (distancia, capacidad, urgencia), el que tenga mejor `performance_score` será elegido.

---

## ✅ Valores Recomendados por Situación

| Situación | Performance Score | Justificación |
|-----------|-------------------|---------------|
| Conductor nuevo sin historial | 0.70 | Valor neutro para empezar |
| Conductor con 1-2 meses | Calcular con fórmula | Usar datos reales disponibles |
| Conductor experimentado (>6 meses) | Calcular con fórmula | Suficientes datos para análisis |
| Conductor con problemas recurrentes | 0.50-0.65 | Penalizar en asignación |
| Conductor estrella | 0.90-1.00 | Priorizar para entregas críticas |
| Sin sistema de métricas | 0.70 para todos | Igualdad hasta implementar métricas |

---

## 🔄 Actualización Periódica

### Script de Actualización Mensual

```python
def actualizar_performance_scores():
    """Ejecutar este script cada mes para actualizar scores"""
    
    conductores = db.query("SELECT * FROM drivers WHERE active = true")
    
    for conductor in conductores:
        # Calcular nuevo score basado en últimos 30 días
        nuevo_score = calcular_performance_score(conductor.id)
        
        # Actualizar en base de datos
        db.execute(f"""
            UPDATE drivers 
            SET performance_score = {nuevo_score},
                score_updated_at = NOW()
            WHERE id = {conductor.id}
        """)
        
        print(f"Conductor {conductor.nombre}: {nuevo_score:.2f}")
```

---

## 📝 Resumen Rápido

1. **¿Tienes sistema de métricas?** → Usa la fórmula de cálculo
2. **¿NO tienes métricas?** → Usa 0.70 para todos
3. **¿Conductor nuevo?** → Usa 0.70 (neutro)
4. **¿Quieres priorizar a alguien?** → Asigna 0.90+
5. **¿Conductor problemático?** → Asigna 0.50-0.65

**Valor por defecto recomendado: 0.70**

---

## 🎓 Próximos Pasos

1. Decide qué datos tienes disponibles
2. Elige un método de cálculo (simple o complejo)
3. Implementa la función de cálculo
4. Integra con tus llamadas al API
5. Actualiza periódicamente (semanal o mensual)

¿Necesitas ayuda implementando el cálculo? ¡Pregúntame!
