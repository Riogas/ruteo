# 🧠 Arquitectura Técnica y Decisiones de Diseño

## 📐 Visión General de la Arquitectura

Este sistema implementa un **motor de asignación inteligente de rutas** que resuelve el problema complejo de asignar pedidos a vehículos considerando múltiples restricciones dinámicas.

### Características Únicas

1. **Capacidad Dinámica**: Cada vehículo puede tener un límite diferente de pedidos simultáneos
2. **Entregas Fuera de Orden**: Los conductores pueden entregar en cualquier secuencia si es más eficiente
3. **Red Vial Real**: Usa calles reales con sentidos de circulación (no distancia en línea recta)
4. **Scoring Multi-criterio**: Evalúa 5 factores simultáneamente para tomar la mejor decisión
5. **Optimización con IA**: Usa algoritmos de Google OR-Tools

---

## 🏗️ Componentes del Sistema

### 1. **Modelos de Datos** (`app/models.py`)

**Por qué Pydantic:**
- ✅ Validación automática de datos
- ✅ Serialización JSON nativa
- ✅ Documentación automática de API
- ✅ Type hints para IDE

**Modelos principales:**
- `Order`: Pedido con dirección, deadline, prioridad
- `Vehicle`: Vehículo con ubicación, capacidad dinámica, historial
- `AssignmentScore`: Score detallado con explicación
- `SystemConfig`: Configuración de pesos ajustable en tiempo real

### 2. **Servicio de Geocodificación** (`app/geocoding.py`)

**Problema que resuelve:**
El cliente ingresa "Av. Corrientes 1234" pero necesitamos coordenadas (lat, lon) para calcular rutas.

**Estrategia Multi-proveedor:**
```
1. Nominatim (OpenStreetMap) → GRATIS, sin API key
   ↓ Si falla
2. Google Maps → PRECISO, requiere API key de pago
   ↓ Si falla
3. OpenCage → BALANCE precio/calidad
```

**Optimizaciones:**
- ✅ Cache en memoria para evitar requests repetidos
- ✅ Rate limiting para respetar límites de API
- ✅ Fallback automático entre proveedores

### 3. **Motor de Rutas** (`app/routing.py`)

**Problema complejo:**
No podemos usar distancia en línea recta. Necesitamos:
- Calles reales
- Sentidos de circulación (calles flechadas)
- Tiempos reales de viaje

**Solución: OSMnx + NetworkX**

```python
# OSMnx descarga el mapa real de la ciudad
graph = ox.graph_from_place("Buenos Aires, Argentina")

# El grafo es DIRIGIDO (respeta sentidos de calles)
# Cada arista tiene:
#   - length: distancia en metros
#   - travel_time: tiempo calculado según velocidad
#   - geometry: coordenadas del camino
```

**Algoritmo de routing:**
- Dijkstra para camino más corto
- Pesos: distancia O tiempo (configurable)
- Considera restricciones de sentido único

**Cache de grafos:**
Los mapas de ciudades se descargan una vez y se cachean en disco. Esto hace que las siguientes ejecuciones sean instantáneas.

### 4. **Motor de Scoring** (`app/scoring.py`)

**El corazón del sistema de decisión.**

**Enfoque Multi-criterio:**

Cada vehículo recibe un score de 0 a 1 basado en 5 factores:

#### Factor 1: Distancia (30%)
```
Score = 1 / (1 + distancia_normalizada)
```
- Vehículos cercanos = score alto
- Vehículos lejanos = score bajo

#### Factor 2: Capacidad (20%)
```
Score = espacios_libres / capacidad_máxima
```
- Mucho espacio = score alto
- Sin espacio = score 0 (rechazado)

#### Factor 3: Urgencia Temporal (25%)
```
Score = función(tiempo_hasta_deadline, tiempo_de_viaje)
```
- Con tiempo de sobra = score alto
- Llegará tarde = score muy bajo (0.2)
- Ajustado por prioridad del pedido

#### Factor 4: Compatibilidad de Ruta (15%)
```
Score = qué tan bien encaja con entregas actuales
```
- Pedido cercano a entregas actuales = alto
- Pedido requiere desvío grande = bajo

#### Factor 5: Desempeño del Conductor (10%)
```
Score = (tasa_de_éxito × 0.7) + (experiencia × 0.3)
```
- Buenos conductores = score alto
- Nuevos conductores = score medio

**Score Total:**
```python
score_total = (
    score_distancia × 0.30 +
    score_capacidad × 0.20 +
    score_urgencia × 0.25 +
    score_compatibilidad × 0.15 +
    score_desempeño × 0.10
)
```

**Ventajas:**
- ✅ **Transparente**: Cada decisión es explicable
- ✅ **Ajustable**: Los pesos se cambian en tiempo real
- ✅ **Balanceado**: No depende de un solo factor
- ✅ **Justo**: Distribuye carga entre conductores

### 5. **Motor de Optimización** (`app/optimizer.py`)

**Problema: TSP con Time Windows**

Dado un vehículo con N pedidos asignados, ¿en qué orden entregarlos?

**Restricciones:**
- Minimizar distancia/tiempo total
- Respetar deadlines de cada pedido
- Permitir entregas "fuera de orden"

**Solución: Google OR-Tools**

```python
# OR-Tools usa metaheurísticas avanzadas:
# - Guided Local Search
# - Simulated Annealing
# - Tabu Search

routing = pywrapcp.RoutingModel(...)
routing.AddDimension(time_dimension)  # Ventanas de tiempo
solution = routing.SolveWithParameters(...)
```

**Por qué OR-Tools:**
- ✅ Usado en producción por Google Maps
- ✅ Resuelve VRP (Vehicle Routing Problem) eficientemente
- ✅ Soporta restricciones complejas
- ✅ Escalable a problemas grandes

**Clustering Optimizer:**

Agrupa pedidos cercanos geográficamente para entregarlos juntos:
- Encuentra pedidos en radio de 3-5 km
- Verifica compatibilidad de deadlines
- Sugiere batch de entregas

### 6. **API REST** (`app/main.py`)

**FastAPI** para API moderna y performante.

**Endpoint principal: `POST /api/v1/assign-order`**

**Flujo completo:**
```
1. Recibe request con pedido y vehículos disponibles
   ↓
2. Geocodifica dirección si es necesario
   ↓
3. Valida datos de entrada
   ↓
4. Evalúa TODOS los vehículos con scoring engine
   ↓
5. Selecciona el mejor (score más alto)
   ↓
6. (Opcional) Optimiza secuencia de entregas
   ↓
7. Retorna resultado con:
   - Vehículo asignado
   - Score de confianza
   - Desglose de la decisión
   - Alternativas consideradas
   - Warnings si aplican
```

**Features de la API:**
- ✅ Documentación automática (Swagger UI)
- ✅ Validación de request/response
- ✅ Manejo de errores robusto
- ✅ CORS habilitado
- ✅ Health checks

---

## 🎯 Decisiones de Diseño

### ¿Por qué no Machine Learning tradicional?

**Consideramos:**
- Redes neuronales
- Random forests
- Gradient boosting

**Decidimos NO usarlos porque:**
1. ❌ Requieren datos históricos extensos
2. ❌ Son "cajas negras" (difícil explicar decisiones)
3. ❌ Necesitan reentrenamiento constante
4. ❌ Difícil ajustar en tiempo real

**Nuestra solución (scoring + OR-Tools):**
1. ✅ Funciona desde día 1 (sin datos históricos)
2. ✅ Cada decisión es explicable
3. ✅ Ajustable en tiempo real (cambiar pesos)
4. ✅ Combina optimización matemática con heurísticas

### ¿Por qué OSMnx y no Google Maps API?

**Google Maps Directions API:**
- ✅ Muy preciso
- ✅ Considera tráfico en tiempo real
- ❌ **Caro**: $5 por 1000 requests
- ❌ Requiere API key
- ❌ Límites de uso

**OSMnx (OpenStreetMap):**
- ✅ **Gratis** y sin límites
- ✅ Datos de calles flechadas
- ✅ Cache local de mapas
- ✅ Suficientemente preciso para asignación
- ⚠️ No considera tráfico en tiempo real

**Nuestra estrategia:**
Usar OSMnx para asignación (rápido, barato), Google Maps opcional para navegación del conductor.

### ¿Por qué Capacidad Dinámica?

Tu requerimiento: "cada móvil tiene un lote dinámico... tienen hasta 6 pedidos para tener en simultaneo, no se puede mas... (este valor puede variar en el tiempo)"

**Implementación:**
```python
class Vehicle:
    max_capacity: int = 6  # Configurable por vehículo
    current_load: int      # Pedidos actuales
    
    @property
    def available_capacity(self):
        return self.max_capacity - self.current_load
```

**Ventajas:**
- ✅ Motos pueden tener capacidad 4
- ✅ Camionetas pueden tener capacidad 12
- ✅ Se puede ajustar en tiempo real por vehículo
- ✅ El scoring considera capacidad disponible

### ¿Por qué Entregas Fuera de Orden?

Tu requerimiento: "los móviles pueden no cumplir los pedidos en el orden que van apareciendo... a veces se les ocurre que pueden ir y entregar 2 o 3 en el mismo punto"

**Implementación:**
- OR-Tools optimiza la SECUENCIA de entregas
- No forzamos orden FIFO
- El algoritmo encuentra el orden óptimo considerando:
  - Distancias entre puntos
  - Deadlines de cada pedido
  - Agrupación geográfica

**Resultado:**
Si hay 3 pedidos cerca entre sí, aunque uno sea más antiguo y otro más nuevo, el sistema puede decidir entregarlos juntos si es más eficiente.

---

## 🚀 Escalabilidad

### Actual (Monolito)
```
FastAPI → Servicios (geocoding, routing, scoring) → Response
```

### Futuro (Microservicios)
```
API Gateway
    ↓
┌───────────┬──────────────┬─────────────┐
│ Geocoding │   Routing    │   Scoring   │
│  Service  │   Service    │   Service   │
└───────────┴──────────────┴─────────────┘
    ↓           ↓                ↓
  Cache      PostgreSQL       Redis
           (PostGIS)
```

### Optimizaciones para Producción

1. **Base de datos:**
   - PostgreSQL con PostGIS para datos geoespaciales
   - Redis para cache de rutas y scores

2. **Cache de grafos:**
   - Los mapas de OSM se cachean en disco
   - Primera carga: 1-2 min, siguientes: instantáneo

3. **Procesamiento paralelo:**
   - Evaluar vehículos en paralelo
   - Calcular múltiples rutas simultáneamente

4. **ML para predicciones:**
   - Predecir tiempos de entrega basado en histórico
   - Predecir probabilidad de éxito por conductor

---

## 📊 Métricas y Monitoreo

**Métricas clave a monitorear:**

1. **Eficiencia de asignación:**
   - Tiempo promedio de respuesta de API
   - Score promedio de asignaciones
   - Tasa de rechazo (sin vehículos disponibles)

2. **Performance de vehículos:**
   - Tasa de entregas a tiempo
   - Distancia promedio por entrega
   - Utilización de capacidad

3. **Calidad de predicciones:**
   - Diferencia entre tiempo estimado vs real
   - Precisión de deadlines

---

## 🔐 Seguridad y Confiabilidad

1. **Validación de entrada:**
   - Pydantic valida todos los requests
   - Rechaza datos inválidos automáticamente

2. **Manejo de errores:**
   - Try/catch en todos los servicios
   - Fallback automático (ej: geocoding)
   - Logs detallados para debugging

3. **Rate limiting:**
   - Respetar límites de APIs externas
   - Prevenir abuso del sistema

---

## 🎓 Conclusión

Este sistema es **complejo pero robusto**, diseñado para:
- ✅ Funcionar en producción desde día 1
- ✅ Ser ajustable en tiempo real
- ✅ Escalar a miles de pedidos/día
- ✅ Explicar cada decisión tomada
- ✅ Adaptarse a restricciones cambiantes

**Próximos pasos sugeridos:**
1. Integrar con base de datos real
2. Añadir panel de administración
3. Implementar ML para predicciones
4. Añadir visualización de rutas en mapa
5. Integrar con sistema de tracking GPS real
