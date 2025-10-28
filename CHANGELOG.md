# Changelog - Sistema de Ruteo

## [Unreleased] - 2025-10-28

### ✨ Changed - BREAKING CHANGE

#### Separación del número de puerta en el modelo `Address`

**Antes:**
```json
{
    "street": "Av. 18 de Julio 1234",
    "corner_1": "Ejido",
    "city": "Montevideo",
    "country": "Uruguay"
}
```

**Ahora:**
```json
{
    "street": "Av. 18 de Julio",
    "number": "1234",
    "corner_1": "Ejido",
    "city": "Montevideo",
    "country": "Uruguay"
}
```

#### ¿Por qué este cambio?

- ✅ **Mejor estructura de datos**: Separar la calle del número permite validaciones más específicas
- ✅ **Más flexible**: Puedes tener direcciones con o sin número de forma explícita
- ✅ **Mejor para bases de datos**: Facilita búsquedas y filtros
- ✅ **Estándar internacional**: La mayoría de APIs de geocoding usan esta estructura

#### Campos del modelo `Address` actualizados:

```python
class Address(BaseModel):
    street: str              # Calle SIN número (requerido)
    number: Optional[str]    # Número de puerta (opcional) ✨ NUEVO
    city: str                # Ciudad (requerido)
    corner_1: Optional[str]  # Primera esquina (opcional)
    corner_2: Optional[str]  # Segunda esquina (opcional)
    state: Optional[str]     # Departamento/Estado (opcional)
    country: str             # País (default: "Uruguay")
    postal_code: Optional[str]  # Código postal (opcional)
    full_address: Optional[str] # Dirección completa (opcional)
    coordinates: Optional[Coordinates]  # Coordenadas (opcional)
```

#### Endpoints afectados:

- ✅ `POST /geocode` - Geocodificación
- ✅ `POST /reverse-geocode` - Geocodificación inversa (ahora devuelve `number` separado)
- ✅ `POST /batch-geocode` - Geocodificación en lote
- ⚠️ `POST /optimize-route` - Actualizar tus requests si usas este endpoint

#### Migración para usuarios existentes:

Si tienes código que usa la API, actualiza tus requests:

**Python:**
```python
# Antes
address = {
    "street": "Av. 18 de Julio 1234",
    "city": "Montevideo"
}

# Ahora
address = {
    "street": "Av. 18 de Julio",
    "number": "1234",
    "city": "Montevideo"
}
```

**JavaScript:**
```javascript
// Antes
const address = {
    street: "Av. 18 de Julio 1234",
    city: "Montevideo"
};

// Ahora
const address = {
    street: "Av. 18 de Julio",
    number: "1234",
    city: "Montevideo"
};
```

#### Retrocompatibilidad:

- ❌ **NO hay retrocompatibilidad automática**
- ⚠️ Si envías `"street": "Av. 18 de Julio 1234"` sin el campo `number`, el sistema intentará geocodificar pero puede dar resultados menos precisos
- ✅ Se recomienda actualizar todos los clientes para usar el nuevo formato

#### Ejemplos completos:

**1. Dirección con número:**
```json
{
    "street": "Av. 18 de Julio",
    "number": "1234",
    "city": "Montevideo",
    "country": "Uruguay"
}
```

**2. Dirección con esquinas (sin número):**
```json
{
    "street": "Av. 18 de Julio",
    "corner_1": "Río Negro",
    "corner_2": "Ejido",
    "city": "Montevideo",
    "country": "Uruguay"
}
```

**3. Dirección combinada:**
```json
{
    "street": "Av. 18 de Julio",
    "number": "1234",
    "corner_1": "Ejido",
    "city": "Montevideo",
    "country": "Uruguay"
}
```

---

## [1.0.0] - 2025-10-27

### ✨ Added
- Sistema de ruteo inteligente con optimización
- Geocodificación con soporte de esquinas
- Geocodificación inversa con detección de esquinas
- API RESTful con FastAPI
- Documentación Swagger personalizada moderna
- Soporte Docker + Docker Compose
- Cache con Redis
- Integración con OSMnx y NetworkX
