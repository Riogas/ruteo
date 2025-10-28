# 🚚 Sistema Inteligente de Ruteo Dinámico

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastA## 📚 Documentación Adicional

- **[QUICKSTART.md](QUICKSTART.md)**: Guía rápida de instalación y primeros pasos
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Explicación técnica detallada de la arquitectura y decisiones de diseño
- **[EJEMPLOS_PAYLOADS.md](EJEMPLOS_PAYLOADS.md)**: Ejemplos de payloads para copiar y pegar en la API
- **[EXPLICACION_PERFORMANCE_SCORE.md](EXPLICACION_PERFORMANCE_SCORE.md)**: Qué es y cómo funciona el performance_score
- **[COMO_CALCULAR_PERFORMANCE_SCORE.md](COMO_CALCULAR_PERFORMANCE_SCORE.md)**: Guía práctica para calcular e implementar performance_score
- **[API Docs](http://localhost:8080/docs)**: Documentación interactiva de la API (cuando esté corriendo)ttps://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

Sistema avanzado de asignación y ruteo de pedidos con IA que resuelve el problema complejo de asignar entregas a vehículos considerando múltiples restricciones dinámicas en tiempo real.

### ✨ Características Principales

- ✅ **Capacidad dinámica** por vehículo (lote configurable, default 6 pedidos)
- ✅ **Optimización geoespacial** con calles flechadas y rutas reales (OSMnx)
- ✅ **Priorización temporal** según fecha/hora comprometida
- ✅ **Agrupación inteligente** de entregas cercanas
- ✅ **Predicción de tiempos** de viaje y entrega
- ✅ **Flexibilidad de orden** permitiendo entregas fuera de secuencia si es óptimo
- ✅ **Scoring multi-criterio** con 5 factores: distancia, capacidad, tiempo, ruta, desempeño
- ✅ **Optimización con IA** usando Google OR-Tools
- ✅ **Geocodificación automática** con fallback multi-proveedor
- ✅ **API REST completa** con documentación automática

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        API REST (FastAPI)                        │
│                    POST /api/v1/assign-order                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Geocoding       │ │ Route Calculator │ │  AI Optimizer   │
│ Service         │ │ (OSM + NetworkX) │ │ (ML + OR-Tools) │
└─────────────────┘ └──────────────────┘ └─────────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
                   ┌──────────────────┐
                   │ Scoring Engine   │
                   │ Multi-criteria   │
                   └──────────────────┘
```

## 🚀 Inicio Rápido

### Opción 1: Docker 🐳 (Recomendado - Listo para Producción)

La forma más fácil de ejecutar el sistema en **cualquier máquina** con un solo comando:

```bash
# 1. Clonar el repositorio
git clone https://github.com/Riogas/ruteo.git
cd ruteo

# 2. Levantar con Docker Compose
docker compose up -d

# 3. ¡Listo! Verificar que funciona
curl http://localhost:8080/health
```

**Servicios disponibles:**
- 🌐 API: http://localhost:8080
- 📚 Documentación: http://localhost:8080/docs
- ✅ Health: http://localhost:8080/health

**Scripts de ayuda:**
```bash
# Linux/Mac
./docker-start.sh up      # Iniciar
./docker-start.sh logs    # Ver logs
./docker-start.sh test    # Ejecutar tests
./docker-start.sh down    # Detener

# Windows
.\docker-start.ps1 up     # Iniciar
.\docker-start.ps1 logs   # Ver logs
.\docker-start.ps1 test   # Ejecutar tests
.\docker-start.ps1 down   # Detener
```

📖 **Más información**: Ver [DOCKER.md](DOCKER.md) para configuración avanzada

---

### Opción 2: Instalación Local (Desarrollo)

```powershell
# 1. Clonar o navegar al proyecto
cd ruteo

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Copiar configuración de ejemplo
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# 6. Ejecutar el servidor
python app/main.py
```

El servidor estará disponible en `http://localhost:8080`

```powershell
# Construir y ejecutar con Docker Compose
docker-compose up -d

# Ver logs
docker-compose logs -f ruteo-api

# Detener
docker-compose down
```

### Verificar Instalación

Abre tu navegador en: **http://localhost:8000/docs**

Deberías ver la documentación interactiva de la API (Swagger UI).

## 📦 Uso

```python
import requests

# Solicitar asignación de pedido
response = requests.post('http://localhost:8000/api/v1/assign-order', json={
    "order": {
        "id": "PED-001",
        "address": "Av. Corrientes 1234, Buenos Aires",
        "deadline": "2025-10-22T18:00:00",
        "priority": "high"
    },
    "vehicles": [
        {
            "id": "MOV-001",
            "current_location": {"lat": -34.603722, "lon": -58.381592},
            "current_orders": 3,
            "max_capacity": 6,
            "vehicle_type": "moto"
        }
    ],
    "config": {
        "default_max_capacity": 6
    }
})

result = response.json()
# {
#   "assigned_vehicle": "MOV-001",
#   "confidence_score": 0.92,
#   "estimated_delivery_time": "2025-10-22T17:45:00",
#   "route_details": {...}
# }
```

## 🧠 Algoritmo de IA

El sistema utiliza un enfoque multi-criterio que combina:

1. **Optimización de rutas** (TSP con restricciones temporales)
2. **Machine Learning** para predecir tiempos
3. **Scoring ponderado** considerando:
   - Distancia al nuevo pedido
   - Capacidad disponible
   - Tiempo disponible hasta deadline
   - Compatibilidad de ruta (agrupación geográfica)
   - Historial de desempeño del conductor

## 📊 Características Técnicas

- **Calles flechadas**: Usa grafo dirigido de OpenStreetMap
- **Rutas reales**: Cálculo sobre red vial real, no distancia euclidiana
- **Tiempo real**: Considera tráfico y restricciones horarias
- **Escalable**: Arquitectura preparada para microservicios

## 🔧 Configuración

Ver `config/settings.yaml` para configurar:
- API keys de geocodificación
- Parámetros de optimización
- Pesos del scoring
- Cache de rutas

## � Documentación Adicional

- **[QUICKSTART.md](QUICKSTART.md)**: Guía rápida de instalación y primeros pasos
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Explicación técnica detallada de la arquitectura y decisiones de diseño
- **[API Docs](http://localhost:8000/docs)**: Documentación interactiva de la API (cuando esté corriendo)

## 🧪 Testing

```powershell
# Ejecutar tests unitarios
pytest tests/ -v

# Ejecutar ejemplo de uso
python example_usage.py

# Probar API (requiere que esté corriendo)
python test_api.py
```

## 📂 Estructura del Proyecto

```
ruteo/
├── app/
│   ├── main.py              # API FastAPI
│   ├── models.py            # Modelos de datos (Pydantic)
│   ├── geocoding.py         # Servicio de geocodificación
│   ├── routing.py           # Motor de cálculo de rutas (OSMnx)
│   ├── scoring.py           # Motor de scoring multi-criterio
│   └── optimizer.py         # Optimizador con IA (OR-Tools)
├── config/
│   └── settings.yaml        # Configuración del sistema
├── tests/
│   └── test_basic.py        # Tests unitarios
├── logs/                    # Logs de la aplicación
├── cache/                   # Cache de mapas OSM
├── example_usage.py         # Ejemplo completo de uso
├── test_api.py             # Cliente de testing de API
├── requirements.txt         # Dependencias Python
├── Dockerfile              # Configuración Docker
├── docker-compose.yml      # Orquestación de servicios
└── README.md               # Este archivo
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🐛 Reportar Bugs

Si encuentras un bug, por favor abre un issue con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Logs relevantes

## 📊 Roadmap

- [x] Sistema de scoring multi-criterio
- [x] Integración con OSMnx para rutas reales
- [x] Optimización con OR-Tools
- [x] API REST completa
- [x] Geocodificación multi-proveedor
- [x] Capacidad dinámica por vehículo
- [ ] Panel de administración web
- [ ] Integración con bases de datos (PostgreSQL + PostGIS)
- [ ] ML para predicción de tiempos
- [ ] Visualización de rutas en mapa interactivo
- [ ] Integración con GPS en tiempo real
- [ ] App móvil para conductores
- [ ] Sistema de notificaciones

## 👨‍💻 Autor

Sistema de Ruteo Inteligente - Desarrollado para optimización logística

## �📝 Licencia

MIT License - Ver archivo LICENSE para más detalles

## 🙏 Agradecimientos

- **OpenStreetMap** por los datos de mapas
- **Google OR-Tools** por el motor de optimización
- **FastAPI** por el framework de API
- **Geopy** y **OSMnx** por las herramientas geoespaciales

---

⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub!
#   T e s t   a u t o - d e p l o y   c o n   w e b h o o k  
 