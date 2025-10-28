# 🚀 Guía de Migración - Separación del Número de Puerta

## ⚠️ CAMBIO IMPORTANTE (Breaking Change)

A partir de esta versión, el campo `street` ya **NO debe incluir el número de puerta**. 

Ahora existe un campo separado `number` para el número de puerta.

---

## 📋 Tabla de Cambios

| Campo | Antes | Ahora |
|-------|-------|-------|
| `street` | `"Av. 18 de Julio 1234"` | `"Av. 18 de Julio"` |
| `number` | ❌ No existía | ✅ `"1234"` (opcional) |

---

## 🔄 Ejemplos de Migración

### **Ejemplo 1: Geocodificación Simple**

#### ❌ Formato Antiguo (Ya NO funciona bien)
```json
POST /geocode

{
    "street": "Av. 18 de Julio 1234",
    "city": "Montevideo",
    "country": "Uruguay"
}
```

#### ✅ Formato Nuevo (Recomendado)
```json
POST /geocode

{
    "street": "Av. 18 de Julio",
    "number": "1234",
    "city": "Montevideo",
    "country": "Uruguay"
}
```

---

### **Ejemplo 2: Con Esquinas**

#### ❌ Formato Antiguo
```json
{
    "street": "Av. 18 de Julio 1234",
    "corner_1": "Ejido",
    "city": "Montevideo",
    "country": "Uruguay"
}
```

#### ✅ Formato Nuevo
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

### **Ejemplo 3: Reverse Geocoding**

#### Respuesta Antigua
```json
{
    "street": "18 de Julio 1234",
    "corner_1": "Ejido",
    "corner_2": "Yí",
    "city": "Montevideo",
    "country": "Uruguay"
}
```

#### ✅ Respuesta Nueva
```json
{
    "street": "18 de Julio",
    "number": "1234",
    "corner_1": "Ejido",
    "corner_2": "Yí",
    "city": "Montevideo",
    "country": "Uruguay"
}
```

---

### **Ejemplo 4: Optimización de Rutas**

#### ❌ Formato Antiguo
```json
POST /optimize-route

{
    "order": {
        "id": "PED-001",
        "address": {
            "street": "Av. Corrientes 1234",
            "city": "Buenos Aires"
        }
    },
    "vehicles": [...]
}
```

#### ✅ Formato Nuevo
```json
POST /optimize-route

{
    "order": {
        "id": "PED-001",
        "address": {
            "street": "Av. Corrientes",
            "number": "1234",
            "city": "Buenos Aires"
        }
    },
    "vehicles": [...]
}
```

---

## 🐍 Código Python - Migración

### Opción 1: Actualizar manualmente

```python
# ❌ ANTES
address = {
    "street": "Av. 18 de Julio 1234",
    "city": "Montevideo"
}

# ✅ AHORA
address = {
    "street": "Av. 18 de Julio",
    "number": "1234",
    "city": "Montevideo"
}
```

### Opción 2: Script de migración automática

```python
import re

def migrate_address(old_address: dict) -> dict:
    """
    Convierte direcciones del formato antiguo al nuevo.
    
    Detecta números al final de la calle y los separa.
    """
    street = old_address.get("street", "")
    
    # Regex para detectar número al final (ej: "Av. 18 de Julio 1234")
    match = re.match(r"^(.+?)\s+(\d+)$", street.strip())
    
    if match:
        # Encontró número, separarlo
        new_address = old_address.copy()
        new_address["street"] = match.group(1).strip()
        new_address["number"] = match.group(2)
        return new_address
    else:
        # No hay número o ya está en formato nuevo
        return old_address

# Ejemplos de uso
old = {"street": "Av. 18 de Julio 1234", "city": "Montevideo"}
new = migrate_address(old)
print(new)
# Output: {"street": "Av. 18 de Julio", "number": "1234", "city": "Montevideo"}

old2 = {"street": "Av. 18 de Julio", "corner_1": "Ejido", "city": "Montevideo"}
new2 = migrate_address(old2)
print(new2)
# Output: {"street": "Av. 18 de Julio", "corner_1": "Ejido", "city": "Montevideo"}
```

---

## 🌐 Código JavaScript - Migración

### Opción 1: Actualizar manualmente

```javascript
// ❌ ANTES
const address = {
    street: "Av. 18 de Julio 1234",
    city: "Montevideo"
};

// ✅ AHORA
const address = {
    street: "Av. 18 de Julio",
    number: "1234",
    city: "Montevideo"
};
```

### Opción 2: Función de migración

```javascript
function migrateAddress(oldAddress) {
    const street = oldAddress.street || "";
    
    // Regex para detectar número al final
    const match = street.match(/^(.+?)\s+(\d+)$/);
    
    if (match) {
        // Separar calle y número
        return {
            ...oldAddress,
            street: match[1].trim(),
            number: match[2]
        };
    }
    
    // Ya está en formato nuevo o no tiene número
    return oldAddress;
}

// Ejemplos
console.log(migrateAddress({
    street: "Av. 18 de Julio 1234",
    city: "Montevideo"
}));
// Output: { street: "Av. 18 de Julio", number: "1234", city: "Montevideo" }
```

---

## 📝 Casos Especiales

### Caso 1: Dirección sin número
```json
{
    "street": "Av. 18 de Julio",
    "city": "Montevideo"
}
```
✅ **Funciona igual**, el campo `number` es opcional.

---

### Caso 2: Solo esquinas (sin calle principal)
```json
{
    "corner_1": "Río Negro",
    "corner_2": "Ejido",
    "city": "Montevideo"
}
```
✅ **No requiere cambios**, este formato sigue funcionando.

---

### Caso 3: Full address completa
```json
{
    "full_address": "Av. 18 de Julio 1234, Montevideo, Uruguay"
}
```
✅ **No requiere cambios**, el sistema sigue aceptando direcciones completas como texto.

---

## 🧪 Testing

### Probar el nuevo formato

```bash
# Test 1: Con número separado
curl -X POST http://localhost:8080/geocode \
  -H "Content-Type: application/json" \
  -d '{
    "street": "Av. 18 de Julio",
    "number": "1234",
    "city": "Montevideo",
    "country": "Uruguay"
  }'

# Test 2: Sin número
curl -X POST http://localhost:8080/geocode \
  -H "Content-Type: application/json" \
  -d '{
    "street": "Av. 18 de Julio",
    "corner_1": "Ejido",
    "city": "Montevideo",
    "country": "Uruguay"
  }'

# Test 3: Reverse geocoding
curl -X POST http://localhost:8080/reverse-geocode \
  -H "Content-Type: application/json" \
  -d '{
    "lat": -34.9059,
    "lon": -56.1913
  }'
```

---

## ❓ FAQ

### ¿Qué pasa si envío el formato antiguo?

El sistema intentará geocodificar, pero:
- ⚠️ **Menos precisión**: Puede no detectar correctamente el número
- ⚠️ **Resultados incorrectos**: Especialmente con calles que tienen números en el nombre (ej: "18 de Julio")

**Recomendación**: Actualiza tu código lo antes posible.

---

### ¿Debo actualizar TODO mi código de inmediato?

- ✅ **Sí**, para nuevas implementaciones
- ⚠️ **Pronto**, para código existente (se recomienda migrar en 1-2 semanas)

---

### ¿Puedo seguir usando `full_address`?

✅ **Sí**, el campo `full_address` sigue funcionando para direcciones completas como texto.

```json
{
    "full_address": "Av. 18 de Julio 1234, Montevideo, Uruguay"
}
```

---

## 📞 Soporte

Si tienes problemas con la migración:

1. Revisa el `CHANGELOG.md`
2. Consulta la documentación Swagger: `http://localhost:8080/docs`
3. Abre un issue en GitHub

---

## ✅ Checklist de Migración

- [ ] Actualizar código que envía requests a `/geocode`
- [ ] Actualizar código que envía requests a `/batch-geocode`
- [ ] Actualizar código que envía requests a `/optimize-route`
- [ ] Actualizar código que procesa responses de `/reverse-geocode`
- [ ] Probar todos los endpoints con el nuevo formato
- [ ] Actualizar tests automáticos
- [ ] Actualizar documentación interna

---

¡Listo! 🎉 Ahora tu API está usando la estructura de datos más clara y profesional.
