# 🐳 Docker - Sistema de Ruteo

## 🚀 Inicio Rápido

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/Riogas/ruteo.git
cd ruteo

# 2. Levantar todos los servicios
docker compose up -d

# 3. Verificar que está funcionando
curl http://localhost:8080/health
```

¡Listo! El servidor estará disponible en `http://localhost:8080`

### Opción 2: Solo Docker

```bash
# Build de la imagen
docker build -t ruteo-api .

# Ejecutar el contenedor
docker run -d \
  --name ruteo-api \
  -p 8080:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/cache:/app/cache \
  ruteo-api
```

## 📋 Requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM mínimo
- 1GB espacio en disco

## 🛠️ Configuración

### Variables de Entorno

Puedes personalizar el comportamiento editando `docker-compose.yml`:

```yaml
environment:
  - DEBUG=False                          # Modo debug
  - LOG_LEVEL=INFO                       # Nivel de log: DEBUG, INFO, WARNING, ERROR
  - GEOCODING_PROVIDER=nominatim         # Provider de geocoding
  - NOMINATIM_TIMEOUT=30                 # Timeout para geocoding
  - ENABLE_CACHE=true                    # Habilitar cache
```

### Puertos

Por defecto:
- **API**: `8080` (host) → `8000` (contenedor)
- **Redis**: `6379` (host) → `6379` (contenedor)

Para cambiar el puerto del host, edita en `docker-compose.yml`:
```yaml
ports:
  - "TU_PUERTO:8000"  # Ejemplo: "3000:8000"
```

## 📊 Servicios Incluidos

### 1. ruteo-api
- **Descripción**: API principal del sistema de ruteo
- **Puerto**: 8080
- **Health Check**: `http://localhost:8080/health`
- **Documentación API**: `http://localhost:8080/docs`

### 2. ruteo-redis (opcional)
- **Descripción**: Cache en memoria para mejorar performance
- **Puerto**: 6379
- **Uso**: Cache de geocoding y resultados de rutas

## 🎯 Comandos Útiles

### Gestión del Sistema

```bash
# Levantar servicios
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Ver logs solo de la API
docker compose logs -f ruteo-api

# Ver estado de servicios
docker compose ps

# Detener servicios
docker compose down

# Detener y eliminar volúmenes
docker compose down -v

# Reiniciar un servicio
docker compose restart ruteo-api

# Reconstruir e iniciar
docker compose up -d --build
```

### Debugging

```bash
# Entrar al contenedor
docker compose exec ruteo-api bash

# Ver logs de la aplicación
docker compose exec ruteo-api cat /app/logs/app.log

# Verificar health check
docker compose exec ruteo-api curl http://localhost:8000/health

# Ver uso de recursos
docker stats ruteo-api
```

### Limpieza

```bash
# Limpiar contenedores detenidos
docker container prune

# Limpiar imágenes no usadas
docker image prune

# Limpiar volúmenes no usados
docker volume prune

# Limpieza completa (cuidado!)
docker system prune -a
```

## 🔧 Personalización Avanzada

### Límites de Recursos

En `docker-compose.yml`, ajusta según tu servidor:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'        # Máximo 2 CPUs
      memory: 2G       # Máximo 2GB RAM
    reservations:
      cpus: '1'        # Mínimo 1 CPU
      memory: 512M     # Mínimo 512MB RAM
```

### Volúmenes Persistentes

Los datos se guardan en:
- `./logs` - Logs de la aplicación
- `./cache` - Cache de OSM y geocoding
- `redis-data` - Datos de Redis (volumen Docker)

Para hacer backup:
```bash
# Backup de Redis
docker compose exec ruteo-redis redis-cli SAVE
docker cp ruteo-redis:/data/dump.rdb ./backup/

# Backup de logs y cache
tar -czf backup-$(date +%Y%m%d).tar.gz logs cache
```

## 🌐 Acceso Remoto

### Opción 1: Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Opción 2: Exponer directamente

En `docker-compose.yml`:
```yaml
ports:
  - "0.0.0.0:8080:8000"  # Accesible desde cualquier IP
```

⚠️ **Seguridad**: Si expones públicamente, considera:
- Usar HTTPS (certificado SSL)
- Implementar autenticación
- Configurar firewall
- Rate limiting

## 🧪 Testing

```bash
# Test básico de health
curl http://localhost:8080/health

# Test de geocoding forward
curl -X POST http://localhost:8080/api/v1/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "18 de Julio y Ejido, Montevideo"}'

# Test de geocoding reverso
curl -X POST http://localhost:8080/api/v1/reverse-geocode \
  -H "Content-Type: application/json" \
  -d '{"lat": -34.9033, "lon": -56.1882}'

# Test de optimización de rutas
curl -X POST http://localhost:8080/api/v1/optimize-routes \
  -H "Content-Type: application/json" \
  -d @test_batch_15.json
```

## 📈 Monitoreo

### Health Checks

Docker verifica automáticamente cada 30s:
```bash
# Ver estado de health
docker compose ps
```

Estados posibles:
- `healthy` ✅ - Funcionando correctamente
- `unhealthy` ❌ - Hay problemas
- `starting` 🔄 - Iniciando

### Logs

```bash
# Ver últimas 100 líneas
docker compose logs --tail=100

# Buscar errores
docker compose logs | grep ERROR

# Exportar logs
docker compose logs > logs_export.txt
```

## 🚨 Troubleshooting

### Problema: Puerto 8080 ocupado

```bash
# Verificar qué usa el puerto
netstat -ano | findstr :8080  # Windows
lsof -i :8080                 # Linux/Mac

# Cambiar puerto en docker-compose.yml
ports:
  - "8081:8000"  # Usar 8081 en vez de 8080
```

### Problema: Contenedor no inicia

```bash
# Ver logs detallados
docker compose logs ruteo-api

# Verificar si hay errores de build
docker compose up --build

# Reiniciar desde cero
docker compose down -v
docker compose up -d --build
```

### Problema: Bajo rendimiento

```bash
# Aumentar recursos en docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G

# Verificar uso de recursos
docker stats
```

### Problema: Cache crece mucho

```bash
# Limpiar cache manualmente
rm -rf cache/*
docker compose restart ruteo-api

# Configurar límite de Redis
# En docker-compose.yml, línea del comando de redis:
command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

## 🔐 Seguridad

### Recomendaciones de Producción

1. **No usar root**: El Dockerfile ya usa usuario no-root
2. **Variables sensibles**: Usar secrets en vez de environment
3. **Red aislada**: Los servicios usan red bridge privada
4. **Health checks**: Activados por defecto
5. **Restart policy**: `unless-stopped` configurado

### Secrets (Docker Swarm)

```yaml
secrets:
  google_api_key:
    external: true

services:
  ruteo-api:
    secrets:
      - google_api_key
    environment:
      - GOOGLE_MAPS_API_KEY_FILE=/run/secrets/google_api_key
```

## 📦 Despliegue en Cloud

### AWS (ECS)

```bash
# Build y push a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URL
docker build -t ruteo-api .
docker tag ruteo-api:latest YOUR_ECR_URL/ruteo-api:latest
docker push YOUR_ECR_URL/ruteo-api:latest
```

### Google Cloud (Cloud Run)

```bash
# Build y push a GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/ruteo-api
gcloud run deploy ruteo-api --image gcr.io/YOUR_PROJECT/ruteo-api --platform managed
```

### Azure (Container Instances)

```bash
# Build y push a ACR
az acr build --registry YOUR_ACR --image ruteo-api .
az container create --resource-group YOUR_RG --name ruteo-api --image YOUR_ACR.azurecr.io/ruteo-api --ports 8000
```

## 📝 Notas

- La primera ejecución puede tardar 2-3 minutos mientras descarga OSM data
- El cache de OSM se guarda en `./cache/osm` y persiste entre reinicios
- Redis es opcional pero mejora significativamente el rendimiento
- Los logs rotan automáticamente cuando superan 100MB

## 🆘 Soporte

- **Documentación API**: http://localhost:8080/docs
- **GitHub Issues**: https://github.com/Riogas/ruteo/issues
- **Logs**: `docker compose logs -f`

---

**¡Listo para producción!** 🚀
