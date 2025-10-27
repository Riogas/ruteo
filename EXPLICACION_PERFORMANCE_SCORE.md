# 📊 EXPLICACIÓN: Performance Score

## ¿Qué es el Performance Score?

El `performance_score` es una **calificación del desempeño histórico** del conductor/vehículo, similar a la calificación de estrellas en Uber o Rappi.

---

## 🎯 ¿De dónde sale este dato?

### Opción 1: **Sistema Existente** (Recomendado)

Si ya tienes un sistema de tracking o histórico de entregas:

```python
{
  "performance_score": 4.5,  # De tu base de datos
  "success_rate": 0.95,      # 95% de entregas exitosas
  "total_deliveries": 150    # Total de entregas realizadas
}
```

**Fuentes comunes:**
- ✅ Base de datos de entregas históricas
- ✅ Sistema de calificaciones de clientes
- ✅ Sistema de tracking GPS
- ✅ Sistema de gestión de flota

### Opción 2: **Cálculo Automático** (Si no tienes histórico)

El sistema puede calcularlo automáticamente basado en:

```python
performance_score = (
    success_rate * 0.7 +           # 70% basado en tasa de éxito
    (total_deliveries / 100) * 0.3  # 30% basado en experiencia
)

# Ejemplo:
# - success_rate = 0.95 (95% de entregas exitosas)
# - total_deliveries = 150
# 
# performance_score = (0.95 * 0.7) + (min(150/100, 1.0) * 0.3)
#                   = 0.665 + 0.3
#                   = 0.965 (excelente!)
```

### Opción 3: **Valores por Defecto** (Para empezar)

Si no tienes datos históricos, usa valores por defecto:

```python
# Conductor nuevo
{
  "performance_score": 0.8,  # Neutral/bueno
  "success_rate": 1.0,       # Sin historial = asume 100%
  "total_deliveries": 0      # Sin entregas previas
}

# Conductor experimentado
{
  "performance_score": 0.95,
  "success_rate": 0.95,
  "total_deliveries": 200
}
```

---

## 🔢 Escala y Valores

```
┌─────────────────────────────────────────┐
│  0.0 - 0.5  │  Mal desempeño           │
│  0.5 - 0.7  │  Desempeño regular       │
│  0.7 - 0.85 │  Buen desempeño          │
│  0.85 - 0.95│  Muy buen desempeño      │
│  0.95 - 1.0 │  Excelente desempeño     │
└─────────────────────────────────────────┘
```

---

## 📈 Factores que Afectan el Performance Score

### 1. **Success Rate** (Tasa de Éxito)
```
success_rate = entregas_exitosas / total_entregas

Ejemplos:
- 95 de 100 entregas → 0.95 (excelente)
- 80 de 100 entregas → 0.80 (bueno)
- 50 de 100 entregas → 0.50 (malo)
```

**¿Qué cuenta como entrega exitosa?**
- ✅ Entregada a tiempo
- ✅ Sin quejas del cliente
- ✅ Sin daños en el producto
- ✅ Sin devoluciones

### 2. **Total Deliveries** (Experiencia)
```
Más entregas = más experiencia = mejor score

- 0-50 entregas: Conductor nuevo
- 50-100 entregas: Conductor con experiencia
- 100-200 entregas: Conductor experimentado
- 200+ entregas: Conductor experto
```

### 3. **Average Delivery Time** (Opcional)
```
avg_delivery_time_minutes = tiempo_promedio_de_entrega

Si es menor al tiempo estimado = mejor score
```

### 4. **Customer Ratings** (Opcional)
```
Calificaciones de clientes (1-5 estrellas)
Promedio de calificaciones / 5 = parte del score
```

---

## 💡 Cómo Obtener estos Datos

### Si tienes Base de Datos:

```sql
-- Ejemplo SQL para calcular performance
SELECT 
  driver_id,
  COUNT(*) as total_deliveries,
  SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)::float / COUNT(*) as success_rate,
  AVG(delivery_time_minutes) as avg_delivery_time,
  -- Calcular performance_score
  (SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)::float / COUNT(*) * 0.7) +
  (LEAST(COUNT(*) / 100.0, 1.0) * 0.3) as performance_score
FROM deliveries
WHERE driver_id = 'DRV-001'
GROUP BY driver_id;
```

### Si tienes API de otro sistema:

```python
import requests

def get_driver_performance(driver_id):
    # Obtener de tu sistema existente
    response = requests.get(f"https://tu-sistema.com/api/drivers/{driver_id}/stats")
    data = response.json()
    
    return {
        "performance_score": data["rating"] / 5.0,  # Si usas estrellas
        "success_rate": data["success_rate"],
        "total_deliveries": data["total_trips"]
    }
```

---

## 🚀 Ejemplos Prácticos

### Ejemplo 1: Conductor Nuevo

```json
{
  "id": "VH-001",
  "driver_name": "Juan Pérez (Nuevo)",
  "performance_score": 0.80,      // ← Neutral para empezar
  "success_rate": 1.0,            // Sin fallos aún
  "total_deliveries": 5,          // Solo 5 entregas
  "avg_delivery_time_minutes": null
}
```

### Ejemplo 2: Conductor Experimentado

```json
{
  "id": "VH-002",
  "driver_name": "María López (Experta)",
  "performance_score": 0.95,      // ← Excelente histórico
  "success_rate": 0.96,           // 96% de éxito
  "total_deliveries": 250,        // Muy experimentada
  "avg_delivery_time_minutes": 32.5
}
```

### Ejemplo 3: Conductor con Problemas

```json
{
  "id": "VH-003",
  "driver_name": "Pedro Gómez (En mejora)",
  "performance_score": 0.65,      // ← Necesita mejorar
  "success_rate": 0.78,           // 78% de éxito
  "total_deliveries": 100,
  "avg_delivery_time_minutes": 45.2  // Más lento que promedio
}
```

---

## ⚙️ Cómo se Usa en el Sistema

El `performance_score` representa el **10% del score total** en la decisión de asignación:

```
Score Final = 
  30% Distancia +
  20% Capacidad +
  25% Urgencia Temporal +
  15% Compatibilidad de Ruta +
  10% Performance Score        ← AQUÍ
```

**Impacto:**
- Conductor con score 0.95 vs 0.65 = diferencia de 3% en score final
- No es determinante, pero ayuda a **desempatar** entre opciones similares
- Premia a **buenos conductores** y distribuye carga equitativamente

---

## 🔄 Actualización del Performance Score

### Después de cada entrega:

```python
# Pseudocódigo de cómo actualizar
def update_performance_after_delivery(driver_id, delivery_successful):
    driver = get_driver(driver_id)
    
    # Actualizar total
    driver.total_deliveries += 1
    
    # Actualizar tasa de éxito
    if delivery_successful:
        successful_count = driver.total_deliveries * driver.success_rate + 1
    else:
        successful_count = driver.total_deliveries * driver.success_rate
    
    driver.success_rate = successful_count / driver.total_deliveries
    
    # Recalcular performance_score
    driver.performance_score = (
        driver.success_rate * 0.7 +
        min(driver.total_deliveries / 100, 1.0) * 0.3
    )
    
    save_driver(driver)
```

---

## 📝 Resumen

| Dato | Descripción | Rango | Cómo Obtenerlo |
|------|-------------|-------|----------------|
| `performance_score` | Score global del conductor | 0.0 - 1.0 | Calculado o de BD |
| `success_rate` | % de entregas exitosas | 0.0 - 1.0 | Histórico de entregas |
| `total_deliveries` | Total de entregas realizadas | 0 - ∞ | Contador en BD |
| `avg_delivery_time_minutes` | Tiempo promedio de entrega | minutos | Promedio histórico |

---

## 💡 Recomendaciones

### Para Empezar (Sin Datos):
```python
# Usa estos valores por defecto
{
  "performance_score": 0.85,  # Bueno
  "success_rate": 1.0,        # Optimista
  "total_deliveries": 0       # Nuevo
}
```

### Con Sistema Existente:
```python
# Consulta tu base de datos
performance_score = calculate_from_history(driver_id)
```

### Importante:
- ✅ **Es opcional**: El sistema funciona sin él (usa 0.8 por defecto)
- ✅ **Mejora con el tiempo**: Más datos = mejor precisión
- ✅ **Se actualiza**: Después de cada entrega
- ✅ **Es justo**: Premia buenos conductores

---

## 🎯 En Resumen

**¿De dónde sale?**
→ De tu histórico de entregas o lo calculas con la fórmula

**¿Qué significa?**
→ Qué tan confiable y experimentado es el conductor

**¿Cómo se asigna?**
→ Manualmente (por ahora) o automáticamente desde tu BD

**¿Es obligatorio?**
→ No, el sistema usa 0.85 por defecto si no lo envías

**¿Se puede actualizar?**
→ Sí, después de cada entrega exitosa/fallida
