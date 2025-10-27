# 🚚 GUÍA DE USO - Sistema de Ruteo Inteligente

## 🌐 Servidor Corriendo

**URL Base:** `http://localhost:8080`
**Documentación Interactiva:** `http://localhost:8080/docs`

---

## 📡 ENDPOINTS DISPONIBLES

### 1. **Health Check** - Verificar que el servidor funciona
```
GET /health
```

**Ejemplo con curl:**
```bash
curl http://localhost:8080/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "geocoding": "ready",
    "routing": "ready",
    "scoring": "ready",
    "optimizer": "ready"
  }
}
```

---

### 2. **Asignar Orden** - Endpoint principal del sistema
```
POST /api/v1/assign-order
```

Este es el endpoint más importante. Aquí envías una nueva orden de entrega y el sistema decide automáticamente:
- ✅ A qué vehículo asignarla
- 🗺️ La mejor ruta considerando calles con dirección única
- 📍 El orden óptimo de entregas
- ⏰ Si se puede cumplir con el deadline

#### **Payload Completo:**

```json
{
  "order": {
    "id": "ORD-001",
    "customer_name": "Juan Pérez",
    "delivery_address": "Av. Corrientes 1234, Buenos Aires, Argentina",
    "deadline": "2025-01-24T18:00:00"
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
      "driver_name": "María",
      "current_location": {
        "lat": -34.615852,
        "lon": -58.433298
      },
      "current_orders": [
        {
          "id": "ORD-100",
          "customer_name": "Ana García",
          "delivery_address": {
            "lat": -34.620000,
            "lon": -58.440000
          },
          "deadline": "2025-01-24T17:30:00"
        }
      ],
      "capacity": 6,
      "performance_score": 4.8
    }
  ]
}
```

#### **Ejemplo con curl:**

```bash
curl -X POST http://localhost:8080/api/v1/assign-order \
  -H "Content-Type: application/json" \
  -d "{
    \"order\": {
      \"id\": \"ORD-001\",
      \"customer_name\": \"Juan Pérez\",
      \"delivery_address\": \"Av. Corrientes 1234, Buenos Aires, Argentina\",
      \"deadline\": \"2025-01-24T18:00:00\"
    },
    \"available_vehicles\": [
      {
        \"id\": \"VH-001\",
        \"driver_name\": \"Carlos\",
        \"current_location\": {
          \"lat\": -34.603722,
          \"lon\": -58.381592
        },
        \"current_orders\": [],
        \"capacity\": 8,
        \"performance_score\": 4.5
      }
    ]
  }"
```

#### **Respuesta:**

```json
{
  "assigned_vehicle": {
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
  "scores": [
    {
      "vehicle_id": "VH-001",
      "total_score": 89.5,
      "distance_score": 92.0,
      "capacity_score": 100.0,
      "time_urgency_score": 85.0,
      "route_compatibility_score": 88.0,
      "performance_score": 90.0,
      "distance_km": 2.5,
      "estimated_time_minutes": 8,
      "can_meet_deadline": true
    }
  ],
  "optimized_route": {
    "vehicle_id": "VH-001",
    "total_distance_km": 2.5,
    "total_time_minutes": 8,
    "waypoints": [
      {
        "order_id": "VH-001-START",
        "location": {
          "lat": -34.603722,
          "lon": -58.381592
        },
        "arrival_time": "2025-01-24T15:30:00",
        "type": "START"
      },
      {
        "order_id": "ORD-001",
        "location": {
          "lat": -34.604444,
          "lon": -58.387222
        },
        "arrival_time": "2025-01-24T15:38:00",
        "type": "DELIVERY"
      }
    ]
  },
  "geocoding_result": {
    "original_address": "Av. Corrientes 1234, Buenos Aires, Argentina",
    "coordinates": {
      "lat": -34.604444,
      "lon": -58.387222
    },
    "normalized_address": "Avenida Corrientes 1234, Buenos Aires, Argentina",
    "provider": "nominatim",
    "confidence": 0.95
  },
  "message": "Orden asignada exitosamente al vehículo VH-001"
}
```

---

### 3. **Geocodificar Dirección** - Convertir dirección en coordenadas
```
POST /api/v1/geocode
```

Útil para probar direcciones antes de enviar órdenes.

#### **Payload:**
```json
{
  "address": "Av. 9 de Julio 1000, Buenos Aires, Argentina"
}
```

#### **Ejemplo con curl:**
```bash
curl -X POST http://localhost:8080/api/v1/geocode \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"Av. 9 de Julio 1000, Buenos Aires, Argentina\"}"
```

#### **Respuesta:**
```json
{
  "original_address": "Av. 9 de Julio 1000, Buenos Aires, Argentina",
  "coordinates": {
    "lat": -34.607777,
    "lon": -58.383888
  },
  "normalized_address": "Avenida 9 de Julio 1000, Buenos Aires, Argentina",
  "provider": "nominatim",
  "confidence": 0.98
}
```

---

## 🔥 EJEMPLOS PRÁCTICOS

### **Escenario 1: Nueva orden con múltiples vehículos disponibles**

El sistema evaluará TODOS los vehículos y elegirá el mejor basándose en:
- Distancia al cliente (30%)
- Capacidad disponible (20%)
- Urgencia del deadline (25%)
- Compatibilidad con ruta actual (15%)
- Performance histórico del conductor (10%)

```json
{
  "order": {
    "id": "ORD-202",
    "customer_name": "Laura Martínez",
    "delivery_address": "Av. Santa Fe 2500, Buenos Aires",
    "deadline": "2025-01-24T16:30:00"
  },
  "available_vehicles": [
    {
      "id": "VH-001",
      "driver_name": "Carlos",
      "current_location": {"lat": -34.603722, "lon": -58.381592},
      "current_orders": [],
      "capacity": 8,
      "performance_score": 4.5
    },
    {
      "id": "VH-002",
      "driver_name": "María",
      "current_location": {"lat": -34.595000, "lon": -58.373000},
      "current_orders": [
        {
          "id": "ORD-100",
          "customer_name": "Pedro",
          "delivery_address": {"lat": -34.596000, "lon": -58.374000},
          "deadline": "2025-01-24T16:00:00"
        }
      ],
      "capacity": 6,
      "performance_score": 4.8
    },
    {
      "id": "VH-003",
      "driver_name": "Jorge",
      "current_location": {"lat": -34.615000, "lon": -58.445000},
      "current_orders": [],
      "capacity": 10,
      "performance_score": 4.2
    }
  ]
}
```

### **Escenario 2: Vehículo con múltiples entregas (optimización de ruta)**

El sistema usará OR-Tools para:
- Calcular la mejor secuencia de entregas
- Respetar las calles de dirección única
- Minimizar distancia total
- Garantizar que todos los deadlines se cumplan

```json
{
  "order": {
    "id": "ORD-303",
    "customer_name": "Roberto Gómez",
    "delivery_address": "Av. Cabildo 1500, Buenos Aires",
    "deadline": "2025-01-24T19:00:00"
  },
  "available_vehicles": [
    {
      "id": "VH-BUSY",
      "driver_name": "Andrés",
      "current_location": {"lat": -34.560000, "lon": -58.450000},
      "current_orders": [
        {
          "id": "ORD-301",
          "customer_name": "Cliente A",
          "delivery_address": {"lat": -34.565000, "lon": -58.455000},
          "deadline": "2025-01-24T17:00:00"
        },
        {
          "id": "ORD-302",
          "customer_name": "Cliente B",
          "delivery_address": {"lat": -34.570000, "lon": -58.460000},
          "deadline": "2025-01-24T18:00:00"
        }
      ],
      "capacity": 8,
      "performance_score": 4.7
    }
  ]
}
```

**Resultado:** El sistema insertará ORD-303 en el orden más eficiente, ¡puede ser entre las otras dos entregas si eso ahorra distancia!

---

## 🧪 TESTING CON PYTHON

Guarda este script como `test_cliente.py`:

```python
import requests
import json
from datetime import datetime, timedelta

API_URL = "http://localhost:8080"

def test_health():
    """Probar que el servidor está vivo"""
    response = requests.get(f"{API_URL}/health")
    print(f"✓ Health Check: {response.json()}")

def test_geocode():
    """Probar geocodificación"""
    payload = {
        "address": "Obelisco, Buenos Aires, Argentina"
    }
    response = requests.post(f"{API_URL}/api/v1/geocode", json=payload)
    result = response.json()
    print(f"✓ Geocode: {result['normalized_address']}")
    print(f"  Coordenadas: ({result['coordinates']['lat']}, {result['coordinates']['lon']})")
    return result['coordinates']

def test_assign_order():
    """Probar asignación de orden"""
    deadline = (datetime.now() + timedelta(hours=3)).isoformat()
    
    payload = {
        "order": {
            "id": "TEST-001",
            "customer_name": "Cliente Prueba",
            "delivery_address": "Av. Corrientes 1000, Buenos Aires",
            "deadline": deadline
        },
        "available_vehicles": [
            {
                "id": "VH-TEST-1",
                "driver_name": "Driver Test",
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
    
    response = requests.post(f"{API_URL}/api/v1/assign-order", json=payload)
    result = response.json()
    
    print(f"✓ Orden asignada a: {result['assigned_vehicle']['driver_name']}")
    print(f"  Score total: {result['scores'][0]['total_score']:.2f}")
    print(f"  Distancia: {result['scores'][0]['distance_km']:.2f} km")
    print(f"  Tiempo estimado: {result['scores'][0]['estimated_time_minutes']} min")
    print(f"  Puede cumplir deadline: {result['scores'][0]['can_meet_deadline']}")

if __name__ == "__main__":
    print("=== PROBANDO SISTEMA DE RUTEO ===\n")
    test_health()
    print()
    test_geocode()
    print()
    test_assign_order()
```

**Ejecutar:**
```bash
python test_cliente.py
```

---

## 📋 CAMPOS IMPORTANTES

### **Order (Orden)**
- `id`: Identificador único de la orden
- `customer_name`: Nombre del cliente
- `delivery_address`: Puede ser STRING (dirección) o OBJETO (coordenadas)
- `deadline`: Fecha/hora límite en formato ISO 8601

### **Vehicle (Vehículo)**
- `id`: Identificador único del vehículo
- `driver_name`: Nombre del conductor
- `current_location`: Coordenadas actuales (lat, lon)
- `current_orders`: Lista de órdenes ya asignadas
- `capacity`: Capacidad máxima (número de órdenes)
- `performance_score`: Score del conductor (0-5)

### **Coordenadas**
```json
{
  "lat": -34.603722,
  "lon": -58.381592
}
```

---

## ⚙️ CONFIGURACIÓN AVANZADA

Edita el archivo `.env` para cambiar:

```env
# Puerto del servidor
API_PORT=8080

# Proveedor de geocodificación
GEOCODING_PROVIDER=nominatim

# Google Maps (mejor precisión, requiere API key)
# GOOGLE_MAPS_API_KEY=tu_key_aqui

# Tipo de red de calles
OSM_NETWORK_TYPE=drive  # drive, walk, bike, all

# Tiempo máximo de optimización
MAX_OPTIMIZATION_TIME_SECONDS=30

# Capacidad predeterminada
DEFAULT_VEHICLE_CAPACITY=6
```

---

## 🎯 CARACTERÍSTICAS CLAVE

### ✅ **Respeta Calles de Dirección Única**
- Usa OpenStreetMap con grafos dirigidos
- Calcula rutas reales respetando el sentido de circulación

### ✅ **Capacidad Dinámica**
- Cada vehículo tiene su propia capacidad
- Puedes cambiarla por vehículo en cada request

### ✅ **Entregas Fuera de Orden**
- OR-Tools optimiza la secuencia
- Puede entregar en otro orden si ahorra distancia

### ✅ **Deadlines Inteligentes**
- Verifica que se puedan cumplir todos los deadlines
- Prioriza órdenes urgentes

### ✅ **Scoring Multi-Criterio**
- Distancia: 30%
- Capacidad: 20%
- Urgencia: 25%
- Compatibilidad de ruta: 15%
- Performance del conductor: 10%

---

## 🔄 FLUJO COMPLETO

```
1. Cliente hace pedido
   ↓
2. Sistema recibe orden + lista de vehículos disponibles
   ↓
3. Geocodifica la dirección del cliente
   ↓
4. Calcula scores para CADA vehículo:
   - Distancia real por calles
   - Capacidad disponible
   - Urgencia del deadline
   - Compatibilidad con ruta actual
   - Performance histórico
   ↓
5. Selecciona el vehículo con mejor score
   ↓
6. Optimiza la secuencia de entregas (si tiene múltiples)
   ↓
7. Retorna: vehículo asignado + ruta optimizada + ETAs
```

---

## 🚀 COMANDOS RÁPIDOS

**Iniciar servidor:**
```bash
python start_server.py
```

**Ver documentación interactiva:**
- Abre: http://localhost:8080/docs
- Prueba endpoints directamente desde el navegador

**Detener servidor:**
- Presiona `Ctrl+C` en la terminal

---

## 💡 TIPS

1. **Usa `/docs`** para probar el API interactivamente
2. **Las direcciones** pueden ser strings o coordenadas directas
3. **El sistema cachea** rutas y geocodificaciones para mayor velocidad
4. **Puedes enviar 0 órdenes** en `current_orders` para un vehículo vacío
5. **Performance score** del conductor afecta la asignación (0-5)

---

## 📞 SOPORTE

- Documentación completa: Ver archivos `README.md`, `ARCHITECTURE.md`
- Troubleshooting: Ver `TROUBLESHOOTING.md`
- Ejemplos: Ver `example_usage.py` y `test_api.py`

---

**¡Sistema listo para usar!** 🎉
