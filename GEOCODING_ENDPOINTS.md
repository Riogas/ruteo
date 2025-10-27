# 📍 Endpoints de Geocodificación

## ✅ Endpoints Implementados

### 1. POST /api/v1/geocode ⭐ MEJORADO
**Geocodificación directa: Dirección → Coordenadas (ahora con soporte para esquinas)**

Convierte una dirección de texto a coordenadas geográficas (latitud, longitud).

**NUEVO:** Soporta direcciones con esquinas (sin número de puerta) - ideal para Uruguay!

#### Formato 1: Con número de puerta (tradicional)
```json
POST http://localhost:8080/api/v1/geocode
Content-Type: application/json

{
  "street": "Av. 18 de Julio 1234",
  "city": "Montevideo",
  "country": "Uruguay"
}
```

#### Formato 2: Con esquinas (SIN número de puerta) ⭐ NUEVO
```json
POST http://localhost:8080/api/v1/geocode
Content-Type: application/json

{
  "street": "Av. 18 de Julio",
  "corner_1": "Río Negro",
  "corner_2": "Ejido",
  "city": "Montevideo",
  "country": "Uruguay"
}
```

#### Formato 3: Combinado (número + esquina)
```json
POST http://localhost:8080/api/v1/geocode
Content-Type: application/json

{
  "street": "Av. 18 de Julio 1234",
  "corner_1": "Ejido",
  "city": "Montevideo",
  "country": "Uruguay"
}
```

#### Ejemplo de Response:
```json
{
  "lat": -34.9034,
  "lon": -56.1883,
  "address": "Av. 18 de Julio, Montevideo, Uruguay"
}
```

#### PowerShell - Dirección con esquinas:
```powershell
$body = @{
    street = "Av. 18 de Julio"
    corner_1 = "Río Negro"
    corner_2 = "Ejido"
    city = "Montevideo"
    country = "Uruguay"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://localhost:8080/api/v1/geocode" `
  -Body $body `
  -ContentType "application/json"
```

---

### Cómo funciona el sistema de esquinas

Cuando proporcionas esquinas, el sistema **automáticamente prueba múltiples formatos**:

1. **"Calle entre Esquina1 y Esquina2, Ciudad"**
   - Ejemplo: "Av. 18 de Julio entre Río Negro y Ejido, Montevideo"

2. **"Calle esquina Esquina1, Ciudad"**
   - Ejemplo: "Av. 18 de Julio esquina Río Negro, Montevideo"

3. **"Esquina1 y Esquina2, Ciudad"** (intersección directa)
   - Ejemplo: "Río Negro y Ejido, Montevideo"

4. **"Calle Número, Ciudad"** (si hay número)
   - Ejemplo: "Av. 18 de Julio 1234, Montevideo"

El sistema intenta todos los formatos hasta encontrar uno que funcione!

---

### 2. POST /api/v1/reverse-geocode ⭐ MEJORADO
**Geocodificación inversa: Coordenadas → Dirección (CON ESQUINAS)**

Convierte coordenadas geográficas a una dirección de texto legible.

**✨ NUEVO**: Incluye las **2 esquinas más cercanas** además de calle y número de puerta.

#### Ejemplo de Request:
```json
POST http://localhost:8080/api/v1/reverse-geocode
Content-Type: application/json

{
  "lat": -34.9011,
  "lon": -56.1645,
  "address": "Montevideo, Uruguay"
}
```

#### Ejemplo de Response (CON ESQUINAS):
```json
{
  "street": "18 de Julio 1234",
  "city": "Montevideo",
  "state": "Montevideo",
  "country": "Uruguay",
  "postal_code": "11200",
  "corner_1": "Ejido",
  "corner_2": "Yí",
  "full_address": "18 de Julio 1234, Montevideo, Uruguay"
}
```

**Nota**: Los campos `corner_1` y `corner_2` pueden ser `null` si no se encuentran esquinas cercanas.

#### PowerShell:
```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://localhost:8080/api/v1/reverse-geocode" `
  -Body '{"lat": -34.9011, "lon": -56.1645}' `
  -ContentType "application/json"
```

---

## 🎯 Casos de Uso

### Geocoding (Dirección → Coordenadas)
- ✅ Validar direcciones de clientes
- ✅ Convertir direcciones a coordenadas para cálculo de rutas
- ✅ Normalizar direcciones ingresadas manualmente
- ✅ Preparar datos para sistemas de mapas

### Reverse Geocoding (Coordenadas → Dirección + Esquinas)
- ✅ Obtener dirección desde GPS del móvil (con esquinas)
- ✅ Convertir ubicación actual del vehículo en dirección legible
- ✅ Mostrar "Calle X entre Esquina1 y Esquina2" en lugar de solo coordenadas
- ✅ Validar coordenadas de entrega
- ✅ Mostrar direcciones completas en reportes y logs
- ✅ Generar direcciones para puntos de interés
- ✅ Tracking de móviles con información precisa de ubicación

---

## 🔧 Configuración del Servicio

El servicio de geocodificación usa **Nominatim** (OpenStreetMap) con servidor personalizado de Uruguay:
- **URL**: `http://nominatim.riogas.uy/`
- **Sin API Key**: Gratis
- **Rate Limit**: 1 segundo entre requests
- **Cache**: Habilitado en memoria

### Proveedores soportados:
1. **Nominatim** (OpenStreetMap) - Default, gratis
2. **Google Maps** - Requiere API key (más preciso)
3. **OpenCage** - Requiere API key (balance costo/precisión)

---

## 📊 Ejemplos de Uso en el Sistema

### Flujo típico de asignación con geocoding:

```
1. Cliente ingresa dirección: "Colón 1234, Montevideo"
   ↓
2. Sistema geocodifica: POST /api/v1/geocode
   ↓
3. Obtiene coordenadas: (-34.9011, -56.1645)
   ↓
4. Calcula ruta desde vehículo a coordenadas
   ↓
5. Asigna pedido al mejor vehículo
```

### Flujo de tracking con reverse geocoding:

```
1. Móvil envía ubicación GPS: (-34.9011, -56.1645)
   ↓
2. Sistema hace reverse geocoding: POST /api/v1/reverse-geocode
   ↓
3. Obtiene dirección: "18 de Julio 1234, Montevideo"
   ↓
4. Muestra en dashboard: "Vehículo en 18 de Julio 1234"
```

---

## 🧪 Pruebas

### Script de prueba automático:
```bash
python test_geocoding.py
```

### Documentación interactiva (Swagger):
```
http://localhost:8080/docs
```

### Prueba manual con curl:
```bash
# Geocoding
curl -X POST "http://localhost:8080/api/v1/geocode" \
  -H "Content-Type: application/json" \
  -d '{"street": "Colón 1234", "city": "Montevideo", "country": "Uruguay"}'

# Reverse Geocoding
curl -X POST "http://localhost:8080/api/v1/reverse-geocode" \
  -H "Content-Type: application/json" \
  -d '{"lat": -34.9011, "lon": -56.1645}'
```

---

## ⚠️ Notas Importantes

1. **Error 404 es normal**: Si el servicio de geocodificación no encuentra la dirección, retorna 404. Esto es comportamiento esperado, no un bug.

2. **Rate Limiting**: Nominatim tiene límite de 1 request/segundo. El servicio respeta este límite automáticamente.

3. **Cache**: Los resultados se cachean en memoria para evitar requests repetidos y mejorar performance.

4. **Precisión**: La precisión depende del proveedor:
   - Nominatim: Bueno para Uruguay
   - Google Maps: Excelente pero requiere API key de pago
   - OpenCage: Intermedio, freemium

5. **Direcciones incompletas**: Si la dirección está incompleta o mal escrita, puede no encontrar resultados. Agregar ciudad y país mejora precisión.

---

## 🚀 Estado Actual

✅ Endpoint `/api/v1/geocode` - Funcionando  
✅ Endpoint `/api/v1/reverse-geocode` - Funcionando ⭐ NUEVO  
✅ Servicio de geocodificación configurado  
✅ Cache habilitado  
✅ Rate limiting implementado  
✅ Documentación actualizada  
✅ Script de pruebas creado  

---

## 📝 Próximos Pasos (Opcionales)

- [ ] Implementar cache persistente con Redis
- [ ] Agregar soporte para Google Maps API (mayor precisión)
- [ ] Implementar batch geocoding (múltiples direcciones a la vez)
- [ ] Agregar métricas de uso del servicio
- [ ] Implementar fallback automático entre proveedores
- [ ] Agregar validación de direcciones antes de geocodificar

---

## 📚 Referencias

- Documentación Nominatim: https://nominatim.org/release-docs/latest/
- Documentación geopy: https://geopy.readthedocs.io/
- Servidor Nominatim Uruguay: http://nominatim.riogas.uy/
