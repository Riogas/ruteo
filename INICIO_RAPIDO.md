# 🚀 INICIO RÁPIDO - Sistema de Ruteo

## ✅ ESTADO ACTUAL

El servidor está **CORRIENDO** en: **http://localhost:8080**

---

## 📍 ENLACES IMPORTANTES

| Recurso | URL |
|---------|-----|
| 🌐 **API Base** | http://localhost:8080 |
| 📖 **Documentación Interactiva** | http://localhost:8080/docs |
| 💚 **Health Check** | http://localhost:8080/health |
| 📊 **Redoc** | http://localhost:8080/redoc |

---

## 🎯 ENDPOINT PRINCIPAL

### **POST /api/v1/assign-order**

Este es el endpoint que necesitas usar. Le envías:
- ✅ Una orden de entrega
- ✅ Lista de vehículos disponibles

El sistema te devuelve:
- ✅ Qué vehículo asignar
- ✅ Score de cada vehículo (distancia, capacidad, urgencia, etc.)
- ✅ Ruta optimizada con ETAs
- ✅ Si se puede cumplir el deadline

---

## 🔥 FORMA MÁS FÁCIL DE PROBAR

### Opción 1: Navegador (Recomendado)
1. Abre: http://localhost:8080/docs
2. Busca `POST /api/v1/assign-order`
3. Clic en "Try it out"
4. Copia un ejemplo de `EJEMPLOS_PAYLOADS.md`
5. Clic en "Execute"
6. ¡Ver resultados!

### Opción 2: Python
```bash
python cliente_simple.py
```

Este script ejecuta 5 tests automáticamente.

---

## 📋 EJEMPLO MÍNIMO

```json
{
  "order": {
    "id": "ORD-001",
    "customer_name": "Juan Pérez",
    "delivery_address": "Av. Corrientes 1234, Buenos Aires",
    "deadline": "2025-12-31T18:00:00"
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
      "performance_score": 0.85
    }
  ]
}
```

---

## 🛑 DETENER EL SERVIDOR

En la terminal donde está corriendo, presiona: **Ctrl+C**

Para volver a iniciarlo:
```bash
python start_server.py
```

---

## 📚 DOCUMENTACIÓN

| Archivo | Descripción |
|---------|-------------|
| `NUEVAS_CARACTERISTICAS.md` | ✨ NUEVAS funcionalidades avanzadas |
| `USO_ENDPOINTS.md` | Guía detallada de todos los endpoints |
| `EJEMPLOS_PAYLOADS.md` | 10+ ejemplos listos para copiar/pegar |
| `ARCHITECTURE.md` | Arquitectura del sistema |
| `README.md` | Documentación completa |
| `QUICKSTART.md` | Guía de inicio rápido |

---

## 💡 QUÉ HACE EL SISTEMA

1. **Recibe una orden** con dirección del cliente
2. **Geocodifica** la dirección (la convierte en coordenadas)
3. **Evalúa TODOS los vehículos** con 6 criterios:
   - Distancia real por calles (25%)
   - Capacidad disponible (15%)
   - Urgencia del deadline (25%)
   - Compatibilidad con ruta actual (10%)
   - Performance del conductor (10%)
   - **Interferencia mínima (15%)** ✨ NUEVO
4. **Verifica factibilidad completa** ✨ NUEVO
   - Simula ruta completa con pedidos actuales + nuevo
   - Calcula tiempos reales con calles flechadas
   - Incluye 5 min de servicio por entrega
   - Verifica que TODOS los deadlines se cumplan
5. **Rechaza automáticamente** si causaría atrasos ✨ NUEVO
6. **Elige el vehículo menos afectado** (menor interferencia)
7. **Optimiza la ruta** (puede cambiar el orden de entregas)
8. **Retorna** el vehículo asignado + ruta + ETAs

---

## 🎨 CARACTERÍSTICAS

✅ **Calles reales con dirección única** (OpenStreetMap)
✅ **Capacidad dinámica** por vehículo
✅ **Entregas fuera de orden** si ahorra distancia
✅ **Verificación de deadlines** (todos los pedidos)
✅ **Tiempo de servicio: 5 minutos** por entrega
✅ **Cálculo de interferencia** (elige el móvil menos afectado)
✅ **Rechazo automático** si causaría atrasos
✅ **Optimización con OR-Tools** (Google)
✅ **Geocodificación automática**
✅ **Score multi-criterio** (6 factores)

---

## 🆘 PROBLEMAS COMUNES

### "No puedo conectarme al servidor"
- Verifica que esté corriendo: http://localhost:8080/health
- Si no responde, ejecuta: `python start_server.py`

### "Error de geocodificación"
- Usa direcciones más específicas: "Av. Corrientes 1234, Buenos Aires, Argentina"
- O pasa coordenadas directamente: `{"lat": -34.603722, "lon": -58.381592}`

### "Deadline no se puede cumplir"
- El sistema te lo avisará en `can_meet_deadline: false`
- Usa deadlines más flexibles o vehículos más cercanos

---

## 🧪 TEST RÁPIDO

Ejecuta esto en tu terminal:

```bash
curl http://localhost:8080/health
```

Deberías ver:
```json
{"status": "healthy", "version": "1.0.0", ...}
```

---

## 📞 PRÓXIMOS PASOS

1. ✅ Abre http://localhost:8080/docs
2. ✅ Prueba el endpoint con un ejemplo
3. ✅ Lee `USO_ENDPOINTS.md` para más detalles
4. ✅ Ejecuta `python cliente_simple.py` para tests automáticos
5. ✅ Integra el API en tu aplicación

---

**¡Todo listo para usar!** 🎉

**Servidor corriendo en:** http://localhost:8080
**Documentación:** http://localhost:8080/docs
