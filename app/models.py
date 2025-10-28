"""
Modelos de datos para el sistema de ruteo inteligente.

Define todas las estructuras de datos usando Pydantic para:
- Validación automática
- Serialización JSON
- Documentación de API automática
- Type hints para mejor desarrollo
"""

from datetime import datetime
from typing import Optional, List, Dict, Literal, Any
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict


# ============================================================================
# CONSTANTES DEL SISTEMA
# ============================================================================

# Tiempo fijo de servicio por entrega (minutos)
# Incluye: descarga del producto, firma del cliente, verificación, etc.
SERVICE_TIME_MINUTES = 5


# ============================================================================
# ENUMERACIONES
# ============================================================================

class VehicleType(str, Enum):
    """Tipos de vehículos disponibles"""
    MOTO = "moto"
    AUTO = "auto"
    CAMIONETA = "camioneta"
    BICICLETA = "bicicleta"


class OrderPriority(str, Enum):
    """Niveles de prioridad de pedidos"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class OrderStatus(str, Enum):
    """Estados posibles de un pedido"""
    PENDING = "pending"           # Pendiente de asignación
    ASSIGNED = "assigned"         # Asignado a un vehículo
    IN_TRANSIT = "in_transit"     # En camino
    DELIVERED = "delivered"       # Entregado
    CANCELLED = "cancelled"       # Cancelado
    FAILED = "failed"             # Falló la entrega


# ============================================================================
# MODELOS GEOESPACIALES
# ============================================================================

class Coordinates(BaseModel):
    """Coordenadas geográficas (latitud, longitud) con soporte UTM"""
    lat: float = Field(..., ge=-90, le=90, description="Latitud")
    lon: float = Field(..., ge=-180, le=180, description="Longitud")
    utm_x: Optional[float] = Field(None, description="Coordenada UTM X (Este)")
    utm_y: Optional[float] = Field(None, description="Coordenada UTM Y (Norte)")
    utm_zone: Optional[str] = Field(None, description="Zona UTM (ej: 21S)")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "lat": -34.603722,
            "lon": -58.381592,
            "utm_x": 366439.84,
            "utm_y": 6170832.45,
            "utm_zone": "21S"
        }
    })


class Address(BaseModel):
    """
    Dirección completa con información estructurada.
    
    Soporta múltiples formatos de direcciones:
    - Con número de puerta: "Av. 18 de Julio" + number: "1234"
    - Con esquinas: "Av. 18 de Julio" con corner_1 y corner_2
    - Combinado: "Av. 18 de Julio" + number: "1234" + corner_1: "Ejido"
    """
    street: str = Field(..., description="Calle principal (sin número de puerta)")
    number: Optional[str] = Field(None, description="Número de puerta")
    city: str = Field(..., description="Ciudad")
    state: Optional[str] = Field(None, description="Provincia/Estado/Departamento")
    country: str = Field(default="Uruguay", description="País")
    postal_code: Optional[str] = Field(None, description="Código postal")
    full_address: Optional[str] = Field(None, description="Dirección completa como texto")
    
    # Nuevos campos para esquinas (opcional)
    corner_1: Optional[str] = Field(None, description="Primera esquina (calle que cruza)")
    corner_2: Optional[str] = Field(None, description="Segunda esquina (otra calle que cruza)")
    
    coordinates: Optional[Coordinates] = Field(None, description="Coordenadas geocodificadas")
    
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "street": "Av. 18 de Julio",
                "number": "1234",
                "city": "Montevideo",
                "country": "Uruguay",
                "full_address": "Av. 18 de Julio 1234, Montevideo, Uruguay"
            },
            {
                "street": "Av. 18 de Julio",
                "corner_1": "Río Negro",
                "corner_2": "Ejido",
                "city": "Montevideo",
                "country": "Uruguay",
                "full_address": "Av. 18 de Julio entre Río Negro y Ejido, Montevideo"
            },
            {
                "street": "Av. 18 de Julio",
                "number": "1234",
                "corner_1": "Ejido",
                "city": "Montevideo",
                "country": "Uruguay",
                "full_address": "Av. 18 de Julio 1234 esquina Ejido, Montevideo"
            }
        ]
    })


# ============================================
# MODELOS DE ZONAS (Zones)
# ============================================


class ZoneRequest(BaseModel):
    """
    Solicitud para determinar la zona de una dirección o coordenadas.
    
    Debe proporcionar EXACTAMENTE UNA de las siguientes opciones:
    - address: Dirección completa (será geocodificada)
    - lat + lon: Coordenadas geográficas directas
    """
    address: Optional[str] = Field(
        None,
        description="Dirección completa a geocodificar (ej: '18 de Julio 1234, Montevideo')"
    )
    lat: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Latitud del punto"
    )
    lon: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Longitud del punto"
    )
    
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "address": "18 de Julio 1234, Salto"
            },
            {
                "lat": -31.3820,
                "lon": -57.9640
            }
        ]
    })
    
    @validator('lon')
    def validate_inputs(cls, v, values):
        """Valida que solo se use address O coordenadas (lat+lon), no ambos"""
        has_address = values.get('address') is not None
        has_lat = values.get('lat') is not None
        has_lon = v is not None
        
        # Debe tener address O ambas coordenadas
        if has_address and (has_lat or has_lon):
            raise ValueError("Proporcione 'address' O coordenadas (lat, lon), no ambos")
        
        # Si tiene una coordenada, debe tener ambas
        if (has_lat and not has_lon) or (has_lon and not has_lat):
            raise ValueError("Si proporciona coordenadas, debe incluir tanto 'lat' como 'lon'")
        
        # Debe tener al menos una opción
        if not has_address and not (has_lat and has_lon):
            raise ValueError("Debe proporcionar 'address' O coordenadas (lat, lon)")
        
        return v


class ZoneResponse(BaseModel):
    """
    Respuesta con información de la zona encontrada.
    """
    coordinates: Coordinates = Field(
        ...,
        description="Coordenadas del punto consultado (con UTM)"
    )
    zone_found: bool = Field(
        ...,
        description="Indica si el punto está dentro de alguna zona"
    )
    zone_id: Optional[str] = Field(
        None,
        description="ID único de la zona"
    )
    zone_name: Optional[str] = Field(
        None,
        description="Nombre de la zona"
    )
    zone_properties: Optional[Dict[str, Any]] = Field(
        None,
        description="Propiedades adicionales de la zona"
    )
    
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "coordinates": {
                    "lat": -31.3820,
                    "lon": -57.9640,
                    "utm_x": 426543.21,
                    "utm_y": 6524123.45,
                    "utm_zone": "21S"
                },
                "zone_found": True,
                "zone_id": "313943121",
                "zone_name": "Salto",
                "zone_properties": {
                    "id": "313943121",
                    "name": "Salto"
                }
            }
        ]
    })


class StreetsRequest(BaseModel):
    """
    Solicitud para listar calles de un departamento/localidad en Uruguay.
    """
    departamento: str = Field(..., description="Departamento de Uruguay (ej: Montevideo, Canelones, Maldonado)")
    localidad: Optional[str] = Field(None, description="Localidad específica dentro del departamento (opcional)")
    
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "departamento": "Montevideo"
            },
            {
                "departamento": "Canelones",
                "localidad": "Ciudad de la Costa"
            },
            {
                "departamento": "Maldonado",
                "localidad": "Punta del Este"
            }
        ]
    })


class StreetsResponse(BaseModel):
    """
    Respuesta con listado de calles (sin duplicados).
    """
    departamento: str = Field(..., description="Departamento consultado")
    localidad: Optional[str] = Field(None, description="Localidad consultada (si se especificó)")
    total_calles: int = Field(..., description="Cantidad total de calles únicas encontradas")
    calles: List[str] = Field(..., description="Lista de nombres de calles (ordenadas alfabéticamente)")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "departamento": "Montevideo",
            "localidad": None,
            "total_calles": 3,
            "calles": [
                "18 de Julio",
                "Bulevar Artigas",
                "Rambla República de Chile"
            ]
        }
    })


# ============================================================================
# MODELOS DE PEDIDOS
# ============================================================================

class OrderItem(BaseModel):
    """Item individual dentro de un pedido"""
    name: str = Field(..., description="Nombre del producto")
    quantity: int = Field(default=1, ge=1, description="Cantidad de unidades")
    weight_kg: float = Field(..., ge=0, description="Peso por unidad en kg")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Laptop HP",
            "quantity": 1,
            "weight_kg": 2.5
        }
    })


class Order(BaseModel):
    """
    Pedido a entregar.
    
    Representa un pedido individual con toda su información:
    - Identificación única
    - Dirección de entrega
    - Fecha/hora límite de entrega
    - Prioridad
    - Peso/volumen (para validar capacidad)
    """
    id: str = Field(..., description="ID único del pedido")
    customer_name: Optional[str] = Field(None, description="Nombre del cliente")
    customer_phone: Optional[str] = Field(None, description="Teléfono del cliente")
    
    # Ubicación
    address: Optional[Address] = Field(None, description="Dirección estructurada")
    delivery_address: Optional[str] = Field(None, description="Dirección de entrega como texto")
    delivery_location: Optional[Coordinates] = Field(None, description="Coordenadas de entrega (si ya están geocodificadas)")
    
    # Temporal
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha/hora de creación")
    deadline: datetime = Field(..., description="Fecha/hora máxima de entrega")
    estimated_duration: int = Field(default=10, description="Tiempo estimado de entrega en el sitio (minutos)")
    
    # Prioridad y estado
    priority: OrderPriority = Field(default=OrderPriority.MEDIUM, description="Prioridad del pedido")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Estado actual")
    
    # Items del pedido
    items: List[OrderItem] = Field(default_factory=list, description="Items incluidos en el pedido")
    
    # Características físicas
    weight_kg: Optional[float] = Field(None, ge=0, description="Peso total en kilogramos (calculado automáticamente si no se provee)")
    volume_m3: Optional[float] = Field(None, ge=0, description="Volumen en metros cúbicos")
    fragile: bool = Field(default=False, description="¿Es frágil?")
    
    # Metadata
    notes: Optional[str] = Field(None, description="Notas adicionales")
    metadata: Dict = Field(default_factory=dict, description="Metadata adicional")
    
    @validator('deadline')
    def deadline_must_be_future(cls, v, values):
        """Validar que el deadline sea futuro"""
        created = values.get('created_at', datetime.now())
        if v <= created:
            raise ValueError('El deadline debe ser posterior a la fecha de creación')
        return v
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "PED-001",
            "customer_name": "Juan Pérez",
            "customer_phone": "+54 11 1234-5678",
            "address": {
                "street": "Av. Corrientes 1234",
                "city": "Buenos Aires",
                "country": "Argentina"
            },
            "deadline": "2025-10-22T18:00:00",
            "priority": "high",
            "weight_kg": 2.5
        }
    })


# ============================================================================
# MODELOS DE VEHÍCULOS
# ============================================================================

class VehicleStatus(str, Enum):
    """Estado del vehículo"""
    AVAILABLE = "available"       # Disponible
    BUSY = "busy"                # Ocupado
    OFFLINE = "offline"          # Fuera de servicio
    MAINTENANCE = "maintenance"   # En mantenimiento


class Vehicle(BaseModel):
    """
    Vehículo/Móvil para entregas.
    
    Representa un vehículo con:
    - Ubicación actual en tiempo real
    - Capacidad dinámica configurable
    - Pedidos actualmente asignados
    - Tipo de vehículo y características
    """
    id: str = Field(..., description="ID único del vehículo")
    driver_name: Optional[str] = Field(None, description="Nombre del conductor")
    driver_phone: Optional[str] = Field(None, description="Teléfono del conductor")
    
    # Tipo y características
    vehicle_type: VehicleType = Field(..., description="Tipo de vehículo")
    license_plate: Optional[str] = Field(None, description="Patente")
    
    # Ubicación actual
    current_location: Coordinates = Field(..., description="Ubicación GPS actual")
    last_update: datetime = Field(default_factory=datetime.now, description="Última actualización de ubicación")
    
    # Capacidad dinámica
    max_capacity: int = Field(default=6, ge=1, le=20, description="Capacidad máxima de pedidos simultáneos")
    current_load: int = Field(default=0, ge=0, description="Cantidad de pedidos actualmente asignados")
    
    # Pedidos actuales - AHORA son objetos Order completos (no solo IDs)
    # Necesitamos objetos completos para verificar deadlines, prioridades y ubicaciones
    current_orders: List['Order'] = Field(default_factory=list, description="Pedidos actualmente asignados (objetos completos)")
    
    # Estado y disponibilidad
    status: VehicleStatus = Field(default=VehicleStatus.AVAILABLE, description="Estado del vehículo")
    available_until: Optional[datetime] = Field(None, description="Disponible hasta (fin de turno)")
    
    # Performance histórico
    avg_delivery_time_minutes: Optional[float] = Field(None, description="Tiempo promedio de entrega (minutos)")
    success_rate: float = Field(default=1.0, ge=0, le=1, description="Tasa de éxito (0-1)")
    total_deliveries: int = Field(default=0, ge=0, description="Total de entregas realizadas")
    average_delay_minutes: float = Field(default=0.0, description="Retraso promedio en minutos")
    performance_score: float = Field(default=0.5, ge=0, le=1, description="Score de performance (0-1)")
    
    # Restricciones de peso y volumen
    max_weight_kg: Optional[float] = Field(None, description="Peso máximo que puede cargar")
    current_weight_kg: float = Field(default=0.0, ge=0, description="Peso actual cargado en kg")
    max_volume_m3: Optional[float] = Field(None, description="Volumen máximo que puede cargar")
    
    @validator('current_load')
    def load_must_not_exceed_capacity(cls, v, values):
        """Validar que la carga actual no exceda la capacidad"""
        max_cap = values.get('max_capacity', 6)
        if v > max_cap:
            raise ValueError(f'La carga actual ({v}) no puede exceder la capacidad máxima ({max_cap})')
        return v
    
    @property
    def available_capacity(self) -> int:
        """Capacidad disponible"""
        return self.max_capacity - self.current_load
    
    @property
    def is_available(self) -> bool:
        """¿Está disponible para recibir más pedidos?"""
        return (
            self.status == VehicleStatus.AVAILABLE and
            self.current_load < self.max_capacity
        )
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "MOV-001",
            "driver_name": "Carlos García",
            "vehicle_type": "moto",
            "current_location": {
                "lat": -34.603722,
                "lon": -58.381592
            },
            "max_capacity": 6,
            "current_load": 3,
            "current_orders": ["PED-010", "PED-015", "PED-020"],
            "status": "available"
        }
    })


# ============================================================================
# MODELOS DE CONFIGURACIÓN
# ============================================================================

class SystemConfig(BaseModel):
    """
    Configuración dinámica del sistema.
    
    Permite ajustar parámetros en tiempo real:
    - Capacidades por defecto
    - Pesos de scoring
    - Parámetros de optimización
    """
    default_max_capacity: int = Field(default=6, ge=1, description="Capacidad por defecto para nuevos vehículos")
    
    # Pesos del scoring (deben sumar 1.0)
    weight_distance: float = Field(default=0.25, ge=0, le=1, description="Peso de la distancia en el scoring")
    weight_capacity: float = Field(default=0.20, ge=0, le=1, description="Peso de la capacidad en el scoring")
    weight_time_urgency: float = Field(default=0.25, ge=0, le=1, description="Peso de la urgencia temporal en el scoring")
    weight_route_compatibility: float = Field(default=0.10, ge=0, le=1, description="Peso de la compatibilidad de ruta en el scoring")
    weight_vehicle_performance: float = Field(default=0.05, ge=0, le=1, description="Peso del rendimiento del vehículo en el scoring")
    weight_interference: float = Field(default=0.15, ge=0, le=1, description="Peso de la interferencia con pedidos pendientes en el scoring")
    
    # Parámetros de optimización
    max_computation_time_seconds: float = Field(default=5.0, ge=0.1)
    consider_traffic: bool = Field(default=True)
    allow_out_of_order_delivery: bool = Field(default=True, description="¿Permitir entregas fuera de orden?")
    
    @validator('weight_interference')
    def weights_must_sum_to_one(cls, v, values):
        """Validar que los pesos sumen 1.0"""
        total = (
            values.get('weight_distance', 0) +
            values.get('weight_capacity', 0) +
            values.get('weight_time_urgency', 0) +
            values.get('weight_route_compatibility', 0) +
            values.get('weight_vehicle_performance', 0) +
            v
        )
        if not (0.99 <= total <= 1.01):  # Tolerancia para errores de punto flotante
            raise ValueError(f'Los pesos deben sumar 1.0, actualmente suman {total}')
        return v


# ============================================================================
# MODELOS DE RUTAS Y RESULTADOS
# ============================================================================

class RouteSegment(BaseModel):
    """Segmento individual de una ruta"""
    from_location: Coordinates
    to_location: Coordinates
    distance_meters: float = Field(..., ge=0)
    duration_seconds: float = Field(..., ge=0)
    path: Optional[List[Coordinates]] = Field(None, description="Coordenadas del camino")


class Route(BaseModel):
    """Ruta completa calculada"""
    vehicle_id: str
    segments: List[RouteSegment]
    total_distance_meters: float = Field(..., ge=0)
    total_duration_seconds: float = Field(..., ge=0)
    estimated_arrival: datetime
    orders_in_route: List[str] = Field(..., description="IDs de pedidos en orden de entrega")


class AssignmentScore(BaseModel):
    """
    Score detallado de una asignación propuesta.
    
    Muestra el desglose de la puntuación para transparencia:
    - Score total
    - Contribución de cada factor
    - Razones de la decisión
    """
    total_score: float = Field(..., ge=0, le=1, description="Score total (0-1, más alto es mejor)")
    
    # Scores individuales
    distance_score: float = Field(..., ge=0, le=1)
    capacity_score: float = Field(..., ge=0, le=1)
    time_urgency_score: float = Field(..., ge=0, le=1)
    route_compatibility_score: float = Field(..., ge=0, le=1)
    vehicle_performance_score: float = Field(..., ge=0, le=1)
    
    # Detalles
    distance_to_delivery_km: float
    available_capacity: int
    time_until_deadline_minutes: float
    estimated_arrival_time: datetime
    will_arrive_on_time: bool
    
    # Explicación
    reasoning: List[str] = Field(default_factory=list, description="Razones de la puntuación")


class AssignmentResult(BaseModel):
    """
    Resultado de la asignación de un pedido.
    
    Respuesta completa del sistema con:
    - Vehículo asignado
    - Confianza de la decisión
    - Ruta sugerida
    - Alternativas consideradas
    """
    order_id: str
    assigned_vehicle_id: Optional[str] = Field(None, description="ID del vehículo asignado (None si no hay disponibles)")
    
    # Score y confianza
    confidence_score: float = Field(..., ge=0, le=1, description="Confianza en la asignación (0-1)")
    score_details: Optional[AssignmentScore] = None
    
    # Ruta y tiempos
    estimated_pickup_time: Optional[datetime] = None
    estimated_delivery_time: Optional[datetime] = None
    route: Optional[Route] = None
    
    # Alternativas consideradas
    alternatives: List[Dict] = Field(default_factory=list, description="Top 3 alternativas consideradas")
    
    # Información adicional
    message: str = Field(default="Asignación exitosa")
    warnings: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "order_id": "PED-001",
            "assigned_vehicle_id": "MOV-001",
            "confidence_score": 0.92,
            "estimated_delivery_time": "2025-10-22T17:45:00",
            "message": "Asignación exitosa"
        }
    })


# ============================================================================
# MODELOS DE REQUEST/RESPONSE API
# ============================================================================

class AssignmentRequest(BaseModel):
    """
    Request para asignar un pedido a un vehículo.
    
    Entrada principal de la API que contiene:
    - Pedido a asignar
    - Lista de vehículos disponibles
    - Configuración del sistema
    """
    order: Order = Field(..., description="Pedido a asignar")
    vehicles: List[Vehicle] = Field(..., description="Vehículos disponibles")
    config: Optional[SystemConfig] = Field(default_factory=SystemConfig, description="Configuración del sistema")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "order": {
                "id": "PED-001",
                "address": {
                    "street": "Av. Corrientes 1234",
                    "city": "Buenos Aires",
                    "country": "Argentina"
                },
                "deadline": "2025-10-22T18:00:00",
                "priority": "high"
            },
            "vehicles": [
                {
                    "id": "MOV-001",
                    "vehicle_type": "moto",
                    "current_location": {"lat": -34.603722, "lon": -58.381592},
                    "max_capacity": 6,
                    "current_load": 3
                }
            ]
        }
    })


class HealthCheckResponse(BaseModel):
    """Response del health check"""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# MODELOS PARA BATCH ASSIGNMENT
# ============================================================================

class BatchAssignmentRequest(BaseModel):
    """
    Request para asignar múltiples pedidos a vehículos.
    
    Procesa varios pedidos en un solo request, optimizando globalmente
    las asignaciones para toda la flota.
    """
    orders: List[Order] = Field(
        ...,
        description="Lista de pedidos pendientes a asignar",
        min_length=1
    )
    vehicles: List[Vehicle] = Field(
        ...,
        description="Vehículos disponibles para asignación"
    )
    config: Optional[SystemConfig] = Field(
        default=None,
        description="Configuración del sistema (opcional, usa defaults si no se provee)"
    )
    fast_mode: bool = Field(
        default=True,
        description="Modo rápido con pre-filtering (recomendado para >10 pedidos)"
    )
    max_candidates_per_order: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Número máximo de candidatos a evaluar completamente por pedido en modo fast"
    )
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "orders": [
                {
                    "id": "ORD-001",
                    "customer_name": "Juan Pérez",
                    "delivery_address": "Av. Corrientes 1234, CABA",
                    "delivery_location": {"lat": -34.603722, "lon": -58.381592},
                    "deadline": "2024-10-24T18:00:00",
                    "priority": "high",
                    "items": [{"name": "Notebook", "quantity": 1, "weight_kg": 2.5}]
                },
                {
                    "id": "ORD-002",
                    "customer_name": "María López",
                    "delivery_address": "Av. Santa Fe 4567, CABA",
                    "delivery_location": {"lat": -34.593722, "lon": -58.401592},
                    "deadline": "2024-10-24T17:30:00",
                    "priority": "urgent",
                    "items": [{"name": "Mouse", "quantity": 2, "weight_kg": 0.5}]
                }
            ],
            "vehicles": [
                {
                    "id": "MOTO-001",
                    "vehicle_type": "moto",
                    "current_location": {"lat": -34.603722, "lon": -58.381592},
                    "capacity": 6,
                    "current_load": 2
                }
            ],
            "fast_mode": True,
            "max_candidates_per_order": 3
        }
    })


class BatchAssignmentResult(BaseModel):
    """Resultado individual de asignación de un pedido"""
    order_id: str = Field(..., description="ID del pedido")
    assigned_vehicle_id: Optional[str] = Field(None, description="ID del vehículo asignado (null si no se pudo asignar)")
    score: Optional[float] = Field(None, description="Score de la asignación (0-1)")
    assignment_time: float = Field(..., description="Tiempo que tomó asignar este pedido (segundos)")
    reasons: List[str] = Field(default_factory=list, description="Razones de la decisión")


class BatchAssignmentResponse(BaseModel):
    """Response del endpoint de batch assignment"""
    total_orders: int = Field(..., description="Total de pedidos procesados")
    assigned: int = Field(..., description="Pedidos asignados exitosamente")
    unassigned: int = Field(..., description="Pedidos no asignados")
    total_time: float = Field(..., description="Tiempo total de procesamiento (segundos)")
    fast_mode_used: bool = Field(..., description="Si se usó modo fast")
    assignments: List[BatchAssignmentResult] = Field(..., description="Detalles de cada asignación")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total_orders": 5,
            "assigned": 4,
            "unassigned": 1,
            "total_time": 2.34,
            "fast_mode_used": True,
            "assignments": [
                {
                    "order_id": "ORD-001",
                    "assigned_vehicle_id": "MOTO-001",
                    "score": 0.875,
                    "assignment_time": 0.45,
                    "reasons": ["Vehículo más cercano", "Alta capacidad disponible"]
                },
                {
                    "order_id": "ORD-002",
                    "assigned_vehicle_id": None,
                    "score": None,
                    "assignment_time": 0.12,
                    "reasons": ["Ningún vehículo disponible cumple requisitos"]
                }
            ]
        }
    })


# ============================================================================
# DISTANCE CALCULATION MODELS
# ============================================================================

class LocationInput(BaseModel):
    """
    Entrada de ubicación para cálculo de distancia.
    Puede ser una dirección O coordenadas (no ambas).
    """
    address: Optional[Address] = Field(None, description="Dirección completa")
    coordinates: Optional[Coordinates] = Field(None, description="Coordenadas geográficas")
    
    @validator('coordinates')
    def validate_location_input(cls, v, values):
        """Valida que se proporcione address O coordinates (no ambas, no ninguna)"""
        has_address = values.get('address') is not None
        has_coordinates = v is not None
        
        if not has_address and not has_coordinates:
            raise ValueError("Debe proporcionar 'address' o 'coordinates'")
        
        if has_address and has_coordinates:
            raise ValueError("Proporcione solo 'address' o 'coordinates', no ambas")
        
        return v
    
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "address": {
                    "street": "Av. 18 de Julio",
                    "number": "1234",
                    "city": "Montevideo",
                    "country": "Uruguay"
                }
            },
            {
                "coordinates": {
                    "lat": -34.9011,
                    "lon": -56.1645
                }
            }
        ]
    })


class DistanceCalculationRequest(BaseModel):
    """
    Solicitud para calcular distancia y tiempo entre dos puntos.
    Usa red vial real con flechamientos (calles de un solo sentido).
    """
    origin: LocationInput = Field(..., description="Punto de origen (dirección o coordenadas)")
    destination: LocationInput = Field(..., description="Punto de destino (dirección o coordenadas)")
    optimize_by: Literal["time", "distance"] = Field(
        default="time",
        description="Optimizar ruta por tiempo o distancia"
    )
    include_geometry: bool = Field(
        default=False,
        description="Incluir geometría de la ruta en la respuesta"
    )
    
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "origin": {
                    "address": {
                        "street": "Av. 18 de Julio",
                        "number": "1234",
                        "city": "Montevideo",
                        "country": "Uruguay"
                    }
                },
                "destination": {
                    "coordinates": {
                        "lat": -34.9011,
                        "lon": -56.1645
                    }
                },
                "optimize_by": "time",
                "include_geometry": False
            },
            {
                "origin": {
                    "coordinates": {
                        "lat": -34.9055,
                        "lon": -56.1913
                    }
                },
                "destination": {
                    "coordinates": {
                        "lat": -34.8708,
                        "lon": -56.1681
                    }
                },
                "optimize_by": "distance",
                "include_geometry": True
            }
        ]
    })


class DistanceCalculationResponse(BaseModel):
    """
    Respuesta con distancia y tiempo calculados usando red vial real.
    """
    distance_km: float = Field(..., description="Distancia total en kilómetros")
    distance_meters: float = Field(..., description="Distancia total en metros")
    duration_minutes: float = Field(..., description="Tiempo estimado en minutos")
    duration_seconds: float = Field(..., description="Tiempo estimado en segundos")
    origin_coordinates: Coordinates = Field(..., description="Coordenadas del origen")
    destination_coordinates: Coordinates = Field(..., description="Coordenadas del destino")
    optimized_by: str = Field(..., description="Criterio de optimización usado (time o distance)")
    route_geometry: Optional[List[Coordinates]] = Field(
        None,
        description="Geometría de la ruta (lista de coordenadas), solo si include_geometry=true"
    )
    calculation_time_ms: float = Field(..., description="Tiempo de cálculo en milisegundos")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "distance_km": 5.234,
            "distance_meters": 5234.0,
            "duration_minutes": 12.5,
            "duration_seconds": 750.0,
            "origin_coordinates": {
                "lat": -34.9055,
                "lon": -56.1913
            },
            "destination_coordinates": {
                "lat": -34.8708,
                "lon": -56.1681
            },
            "optimized_by": "time",
            "route_geometry": None,
            "calculation_time_ms": 245.67
        }
    })


# ============================================================================
# ACTUALIZACIÓN DE REFERENCIAS CIRCULARES
# ============================================================================
# Necesario para que Pydantic pueda resolver List['Order'] en Vehicle.current_orders
Vehicle.model_rebuild()

