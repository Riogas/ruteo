# 📋 EJEMPLOS DE PAYLOADS - Sistema de Ruteo

## Copiar y pegar estos ejemplos en la documentación interactiva: http://localhost:8080/docs

---

## EJEMPLO 1: Asignación Simple
**Escenario:** Nueva orden, un solo vehículo disponible, sin órdenes previas

```json
{
  "order": {
    "id": "ORD-001",
    "customer_name": "Juan Pérez",
    "delivery_address": "Av. Corrientes 1234, Buenos Aires, Argentina",
    "deadline": "2025-01-25T18:00:00"
  },
  "available_vehicles": [
    {
      "id": "VH-001",
      "driver_name": "Carlos Rodriguez",
      "current_location": {
        "lat": -34.603722,
        "lon": -58.381592
      },
      "current_orders": [],
      "capacity": 8,
      "performance_score": 0.85
    }
  ]
}
```

---

## EJEMPLO 2: Múltiples Vehículos (Sistema elige el mejor)
**Escenario:** 3 vehículos disponibles en diferentes ubicaciones

```json
{
  "order": {
    "id": "ORD-002",
    "customer_name": "María González",
    "delivery_address": "Av. Santa Fe 2500, Buenos Aires, Argentina",
    "deadline": "2025-01-25T17:00:00"
  },
  "available_vehicles": [
    {
      "id": "VH-001",
      "driver_name": "Carlos Rodriguez",
      "current_location": {
        "lat": -34.603722,
        "lon": -58.381592
      },
      "current_orders": [],
      "capacity": 8,
      "performance_score": 0.75
    },
    {
      "id": "VH-002",
      "driver_name": "Ana Martínez",
      "current_location": {
        "lat": -34.595000,
        "lon": -58.373000
      },
      "current_orders": [],
      "capacity": 6,
      "performance_score": 0.92
    },
    {
      "id": "VH-003",
      "driver_name": "Jorge López",
      "current_location": {
        "lat": -34.615000,
        "lon": -58.445000
      },
      "current_orders": [],
      "capacity": 10,
      "performance_score": 0.68
    }
  ]
}
```

---

## EJEMPLO 3: Vehículo con Órdenes Previas
**Escenario:** Vehículo ya tiene 2 entregas, sistema optimiza la ruta completa

```json
{
  "order": {
    "id": "ORD-003",
    "customer_name": "Roberto Gómez",
    "delivery_address": "Av. Cabildo 1500, Buenos Aires, Argentina",
    "deadline": "2025-01-25T19:00:00"
  },
  "available_vehicles": [
    {
      "id": "VH-004",
      "driver_name": "Andrés Silva",
      "current_location": {
        "lat": -34.560000,
        "lon": -58.450000
      },
      "current_orders": [
        {
          "id": "ORD-100",
          "customer_name": "Cliente A",
          "delivery_address": {
            "lat": -34.565000,
            "lon": -58.455000
          },
          "deadline": "2025-01-25T17:30:00"
        },
        {
          "id": "ORD-101",
          "customer_name": "Cliente B",
          "delivery_address": {
            "lat": -34.570000,
            "lon": -58.460000
          },
          "deadline": "2025-01-25T18:30:00"
        }
      ],
      "capacity": 8,
      "performance_score": 0.88
    }
  ]
}
```

---

## EJEMPLO 4: Dirección con Coordenadas Directas
**Escenario:** Ya tienes las coordenadas, no necesitas geocodificación

```json
{
  "order": {
    "id": "ORD-004",
    "customer_name": "Laura Fernández",
    "delivery_address": {
      "lat": -34.604444,
      "lon": -58.387222
    },
    "deadline": "2025-01-25T16:30:00"
  },
  "available_vehicles": [
    {
      "id": "VH-005",
      "driver_name": "Pedro Ramírez",
      "current_location": {
        "lat": -34.600000,
        "lon": -58.380000
      },
      "current_orders": [],
      "capacity": 6,
      "performance_score": 4.6
    }
  ]
}
```

---

## EJEMPLO 5: Deadline Urgente
**Escenario:** Entrega urgente en 1 hora, sistema prioriza

```json
{
  "order": {
    "id": "ORD-URGENT",
    "customer_name": "Cliente Urgente",
    "delivery_address": "Obelisco, Buenos Aires, Argentina",
    "deadline": "2025-01-25T10:00:00"
  },
  "available_vehicles": [
    {
      "id": "VH-006",
      "driver_name": "Express Driver",
      "current_location": {
        "lat": -34.603684,
        "lon": -58.381559
      },
      "current_orders": [],
      "capacity": 6,
      "performance_score": 5.0
    }
  ]
}
```

---

## EJEMPLO 6: Capacidad Limitada
**Escenario:** Vehículo casi lleno (7/8 órdenes), sistema evalúa si acepta

```json
{
  "order": {
    "id": "ORD-006",
    "customer_name": "Último Cliente",
    "delivery_address": "Av. 9 de Julio 1000, Buenos Aires",
    "deadline": "2025-01-25T20:00:00"
  },
  "available_vehicles": [
    {
      "id": "VH-FULL",
      "driver_name": "Driver Ocupado",
      "current_location": {
        "lat": -34.607777,
        "lon": -58.383888
      },
      "current_orders": [
        {"id": "ORD-201", "customer_name": "C1", "delivery_address": {"lat": -34.608, "lon": -58.384}, "deadline": "2025-01-25T16:00:00"},
        {"id": "ORD-202", "customer_name": "C2", "delivery_address": {"lat": -34.609, "lon": -58.385}, "deadline": "2025-01-25T16:30:00"},
        {"id": "ORD-203", "customer_name": "C3", "delivery_address": {"lat": -34.610, "lon": -58.386}, "deadline": "2025-01-25T17:00:00"},
        {"id": "ORD-204", "customer_name": "C4", "delivery_address": {"lat": -34.611, "lon": -58.387}, "deadline": "2025-01-25T17:30:00"},
        {"id": "ORD-205", "customer_name": "C5", "delivery_address": {"lat": -34.612, "lon": -58.388}, "deadline": "2025-01-25T18:00:00"},
        {"id": "ORD-206", "customer_name": "C6", "delivery_address": {"lat": -34.613, "lon": -58.389}, "deadline": "2025-01-25T18:30:00"},
        {"id": "ORD-207", "customer_name": "C7", "delivery_address": {"lat": -34.614, "lon": -58.390}, "deadline": "2025-01-25T19:00:00"}
      ],
      "capacity": 8,
      "performance_score": 4.5
    }
  ]
}
```

---

## EJEMPLO 7: Competencia entre Vehículos
**Escenario:** Dos vehículos cerca, pero uno tiene mejor performance

```json
{
  "order": {
    "id": "ORD-007",
    "customer_name": "Cliente Premium",
    "delivery_address": "Av. Libertador 1000, Buenos Aires",
    "deadline": "2025-01-25T15:00:00"
  },
  "available_vehicles": [
    {
      "id": "VH-NEAR",
      "driver_name": "Driver Cercano (Performance bajo)",
      "current_location": {
        "lat": -34.587000,
        "lon": -58.420000
      },
      "current_orders": [],
      "capacity": 6,
      "performance_score": 3.5
    },
    {
      "id": "VH-FAR",
      "driver_name": "Driver Lejano (Performance alto)",
      "current_location": {
        "lat": -34.600000,
        "lon": -58.380000
      },
      "current_orders": [],
      "capacity": 8,
      "performance_score": 5.0
    }
  ]
}
```

---

## EJEMPLO 8: Diferentes Capacidades
**Escenario:** Vehículos con capacidades muy diferentes

```json
{
  "order": {
    "id": "ORD-008",
    "customer_name": "Cliente Normal",
    "delivery_address": "Av. Rivadavia 5000, Buenos Aires",
    "deadline": "2025-01-25T16:00:00"
  },
  "available_vehicles": [
    {
      "id": "VH-SMALL",
      "driver_name": "Moto (Capacidad 3)",
      "current_location": {
        "lat": -34.615000,
        "lon": -58.440000
      },
      "current_orders": [
        {"id": "ORD-301", "customer_name": "C1", "delivery_address": {"lat": -34.616, "lon": -58.441}, "deadline": "2025-01-25T15:00:00"},
        {"id": "ORD-302", "customer_name": "C2", "delivery_address": {"lat": -34.617, "lon": -58.442}, "deadline": "2025-01-25T15:30:00"}
      ],
      "capacity": 3,
      "performance_score": 4.8
    },
    {
      "id": "VH-MEDIUM",
      "driver_name": "Auto (Capacidad 6)",
      "current_location": {
        "lat": -34.620000,
        "lon": -58.450000
      },
      "current_orders": [],
      "capacity": 6,
      "performance_score": 4.5
    },
    {
      "id": "VH-LARGE",
      "driver_name": "Camioneta (Capacidad 12)",
      "current_location": {
        "lat": -34.625000,
        "lon": -58.460000
      },
      "current_orders": [],
      "capacity": 12,
      "performance_score": 4.0
    }
  ]
}
```

---

## EJEMPLO 9: Orden Lejana
**Escenario:** Cliente en las afueras, todos los vehículos están lejos

```json
{
  "order": {
    "id": "ORD-FAR",
    "customer_name": "Cliente Lejano",
    "delivery_address": "La Plata, Buenos Aires, Argentina",
    "deadline": "2025-01-25T21:00:00"
  },
  "available_vehicles": [
    {
      "id": "VH-CENTER",
      "driver_name": "Driver Centro",
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
```

---

## EJEMPLO 10: Solo Geocodificación
**Endpoint:** POST /api/v1/geocode

```json
{
  "address": "Teatro Colón, Buenos Aires, Argentina"
}
```

**Otros ejemplos:**
```json
{"address": "Estadio Monumental, Buenos Aires"}
{"address": "Puerto Madero, Buenos Aires"}
{"address": "Palermo Soho, Buenos Aires"}
{"address": "Av. Corrientes 5000, Buenos Aires"}
```

---

## 🔥 CONSEJOS PARA PROBAR

### En la documentación interactiva (http://localhost:8080/docs):

1. **Clic en el endpoint** que quieres probar
2. **Clic en "Try it out"**
3. **Copiar y pegar** uno de estos ejemplos en el campo de texto
4. **Modificar** fechas si es necesario (usa fechas futuras)
5. **Clic en "Execute"**
6. **Ver la respuesta** abajo

### Modificar fechas:
Reemplaza `"2025-01-25T18:00:00"` con una fecha futura. Formato:
- `YYYY-MM-DDTHH:MM:SS`
- Ejemplo: `2025-12-31T23:59:59`

### Modificar coordenadas:
Buenos Aires (centro):
- Obelisco: `-34.603684, -58.381559`
- Plaza de Mayo: `-34.608333, -58.373056`
- Palermo: `-34.5875, -58.4316`
- Puerto Madero: `-34.612778, -58.363056`

---

## 📊 QUÉ OBSERVAR EN LAS RESPUESTAS

### Scores:
- **Total > 80:** Excelente asignación
- **Total 60-80:** Buena asignación
- **Total < 60:** Asignación aceptable pero no óptima

### Tiempos:
- `estimated_time_minutes`: Tiempo estimado de viaje
- `can_meet_deadline`: Si se puede cumplir el deadline

### Ruta optimizada:
- `waypoints`: Secuencia de entregas
- Puede cambiar el orden de las entregas previas si ahorra distancia

### Geocodificación:
- `normalized_address`: Dirección limpia y estandarizada
- `confidence`: Qué tan seguro está el sistema
- `provider`: Qué servicio se usó (nominatim, google, opencage)

---

**¡Prueba estos ejemplos directamente en http://localhost:8080/docs!** 🚀
