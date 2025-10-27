# 🚀 Guía de Inicio Rápido

## 📋 Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- (Opcional) Docker y Docker Compose

## ⚡ Instalación Rápida

### Opción 1: Instalación Local

```powershell
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
.\venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar archivo de configuración
copy .env.example .env

# 5. Ejecutar la API
python app/main.py
```

La API estará disponible en: http://localhost:8000

### Opción 2: Docker

```powershell
# 1. Construir y ejecutar con Docker Compose
docker-compose up -d

# 2. Ver logs
docker-compose logs -f ruteo-api
```

## 🎯 Uso Básico

### 1. Verificar que la API esté funcionando

Abrir en navegador: http://localhost:8000/docs

### 2. Probar con ejemplo de Python

```powershell
python example_usage.py
```

### 3. Probar con cliente de API

```powershell
python test_api.py
```

## 📡 Hacer un Request a la API

### Usando curl (PowerShell):

```powershell
$body = @{
    order = @{
        id = "PED-001"
        address = @{
            street = "Av. Corrientes 1234"
            city = "Buenos Aires"
            country = "Argentina"
        }
        deadline = (Get-Date).AddHours(2).ToString("yyyy-MM-ddTHH:mm:ss")
        priority = "high"
    }
    vehicles = @(
        @{
            id = "MOV-001"
            vehicle_type = "moto"
            current_location = @{
                lat = -34.603722
                lon = -58.381592
            }
            max_capacity = 6
            current_load = 2
            status = "available"
            success_rate = 0.95
            total_deliveries = 150
        }
    )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/assign-order" -Method POST -Body $body -ContentType "application/json"
```

### Usando Python:

```python
import requests
from datetime import datetime, timedelta

response = requests.post('http://localhost:8000/api/v1/assign-order', json={
    "order": {
        "id": "PED-001",
        "address": {
            "street": "Av. Corrientes 1234",
            "city": "Buenos Aires",
            "country": "Argentina"
        },
        "deadline": (datetime.now() + timedelta(hours=2)).isoformat(),
        "priority": "high"
    },
    "vehicles": [
        {
            "id": "MOV-001",
            "vehicle_type": "moto",
            "current_location": {"lat": -34.603722, "lon": -58.381592},
            "max_capacity": 6,
            "current_load": 2,
            "status": "available",
            "success_rate": 0.95,
            "total_deliveries": 150
        }
    ]
})

result = response.json()
print(f"Asignado a: {result['assigned_vehicle_id']}")
print(f"Confianza: {result['confidence_score']:.1%}")
```

## 📚 Próximos Pasos

1. Lee la documentación completa en: http://localhost:8000/docs
2. Revisa los ejemplos en `example_usage.py`
3. Ejecuta los tests: `pytest tests/`
4. Ajusta la configuración en `config/settings.yaml`

## ⚙️ Configuración

### Ajustar pesos del scoring

Edita `.env` o el request JSON:

```python
{
    "config": {
        "weight_distance": 0.30,       # Peso de distancia (30%)
        "weight_capacity": 0.20,       # Peso de capacidad (20%)
        "weight_time_urgency": 0.25,   # Peso de urgencia (25%)
        "weight_route_compatibility": 0.15,  # Compatibilidad (15%)
        "weight_vehicle_performance": 0.10   # Desempeño (10%)
    }
}
```

### Cambiar capacidad dinámica

```python
{
    "vehicles": [
        {
            "id": "MOV-001",
            "max_capacity": 8  # Aumentar a 8 pedidos simultáneos
        }
    ]
}
```

## 🔧 Troubleshooting

### Error: "No se pudo geocodificar la dirección"

**Solución**: Proporciona las coordenadas directamente:

```python
{
    "order": {
        "delivery_location": {"lat": -34.603722, "lon": -58.381592}
    }
}
```

### Error: "No hay vehículos disponibles"

**Soluciones**:
1. Verifica que los vehículos tengan `status: "available"`
2. Verifica que tengan capacidad disponible
3. Reduce el `min_score_threshold`

### La API no descarga mapas de OSM

**Primera vez**: La descarga de mapas puede tardar 1-2 minutos. Los mapas se cachean para uso futuro.

## 📞 Soporte

Para más información, consulta:
- Documentación interactiva: http://localhost:8000/docs
- Logs: `logs/api.log`
- Tests: `pytest tests/ -v`
