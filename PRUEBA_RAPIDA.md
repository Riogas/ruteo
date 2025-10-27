# ⚡ Prueba Rápida - 2 Minutos

## 🎯 Objetivo
Verificar que Docker funciona correctamente en **2 minutos**.

## ✅ Pasos

### 1️⃣ Levantar Sistema (30 segundos)
```bash
docker compose up -d
```

Espera a ver:
```
✔ Container ruteo-redis  Started
✔ Container ruteo-api    Started
```

### 2️⃣ Esperar Health Check (30 segundos)
```bash
# Verificar estado
docker compose ps
```

Debe mostrar `healthy`:
```
NAME         STATUS          PORTS
ruteo-api    Up (healthy)    0.0.0.0:8080->8000/tcp
ruteo-redis  Up (healthy)    0.0.0.0:6379->6379/tcp
```

### 3️⃣ Test Rápido (60 segundos)

#### Test 1: Health Check
```bash
curl http://localhost:8080/health
```
✅ Esperado: `{"status":"ok"}`

#### Test 2: Geocoding Forward
```bash
curl -X POST http://localhost:8080/api/v1/geocode \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"18 de Julio 1000, Montevideo\"}"
```
✅ Esperado: Coordenadas de 18 de Julio 1000

#### Test 3: Geocoding Reverse con Esquinas
```bash
curl -X POST http://localhost:8080/api/v1/reverse-geocode \
  -H "Content-Type: application/json" \
  -d "{\"lat\": -34.90297, \"lon\": -56.17886}"
```
✅ Esperado: Dirección con corner_1 y corner_2

#### Test 4: Documentación
Abre en navegador:
```
http://localhost:8080/docs
```
✅ Esperado: Interfaz Swagger con todos los endpoints

## 🎉 Si todos los tests pasaron

**¡FELICITACIONES!** Tu sistema está funcionando correctamente.

## 🔍 Comandos Útiles

```bash
# Ver logs
docker compose logs -f

# Ver estado
docker compose ps

# Detener
docker compose down

# Reiniciar
docker compose restart

# Limpiar todo
docker compose down -v
```

## 🚨 Si algo falló

### Contenedor no está healthy
```bash
# Ver logs de error
docker compose logs ruteo-api

# Reintentar
docker compose down
docker compose up -d
```

### Puerto 8080 ocupado
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8081:8000"  # Usar 8081 en vez de 8080

# Reiniciar
docker compose up -d
```

### Error al iniciar
```bash
# Reconstruir desde cero
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## 📊 Test Automático con Script

### Windows
```powershell
.\docker-start.ps1 test
```

### Linux/Mac
```bash
./docker-start.sh test
```

Verás:
```
🧪 Ejecutando tests...

1. Health Check...
   ✅ Health OK

2. Geocoding Forward...
   ✅ Forward OK

3. Geocoding Reverse...
   ✅ Reverse OK

✅ Tests completados
```

## ⏱️ Tiempo Total Estimado

| Paso | Tiempo |
|------|--------|
| Levantar servicios | 30s |
| Health check | 30s |
| Tests manuales | 60s |
| **TOTAL** | **2 min** |

## 🎯 Próximos Pasos

1. ✅ Explorar API Docs: http://localhost:8080/docs
2. ✅ Probar con tus propias coordenadas
3. ✅ Revisar logs: `docker compose logs -f`
4. ✅ Leer documentación completa: [DOCKER.md](DOCKER.md)

---

**¿Todo funciona?** ¡Perfecto! Tu sistema está listo para usar. 🚀
