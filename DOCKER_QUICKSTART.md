# 🐳 Docker - Inicio en 30 Segundos

## Instalación Instantánea

```bash
# Clonar
git clone https://github.com/Riogas/ruteo.git
cd ruteo

# Levantar (un solo comando!)
docker compose up -d

# Verificar
curl http://localhost:8080/health
```

## ✅ ¡Listo!

Tu sistema de ruteo ya está funcionando en:
- **API**: http://localhost:8080
- **Documentación**: http://localhost:8080/docs

## 📋 Comandos Básicos

### Con Docker Compose
```bash
docker compose up -d      # Iniciar
docker compose logs -f    # Ver logs
docker compose ps         # Ver estado
docker compose down       # Detener
```

### Con Scripts de Ayuda

**Linux/Mac:**
```bash
./docker-start.sh up      # Iniciar
./docker-start.sh logs    # Ver logs
./docker-start.sh test    # Ejecutar tests
./docker-start.sh status  # Ver estado
./docker-start.sh down    # Detener
```

**Windows:**
```powershell
.\docker-start.ps1 up     # Iniciar
.\docker-start.ps1 logs   # Ver logs
.\docker-start.ps1 test   # Ejecutar tests
.\docker-start.ps1 status # Ver estado
.\docker-start.ps1 down   # Detener
```

### Con Make (Linux/Mac)
```bash
make up        # Iniciar
make logs      # Ver logs
make test      # Ejecutar tests
make status    # Ver estado
make down      # Detener
make help      # Ver todos los comandos
```

## 🧪 Probar la API

### Health Check
```bash
curl http://localhost:8080/health
```

### Geocoding Forward
```bash
curl -X POST http://localhost:8080/api/v1/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "18 de Julio 1000, Montevideo"}'
```

### Geocoding Reverse (con esquinas!)
```bash
curl -X POST http://localhost:8080/api/v1/reverse-geocode \
  -H "Content-Type: application/json" \
  -d '{"lat": -34.9033, "lon": -56.1882}'
```

### Optimización de Rutas
```bash
curl -X POST http://localhost:8080/api/v1/optimize-routes \
  -H "Content-Type: application/json" \
  -d @test_batch_15.json
```

## 🔧 Configuración

### Cambiar Puerto

Edita `docker-compose.yml`:
```yaml
ports:
  - "3000:8000"  # Usa puerto 3000 en vez de 8080
```

### Variables de Entorno

Edita `docker-compose.yml` en la sección `environment`:
```yaml
environment:
  - DEBUG=False
  - LOG_LEVEL=INFO
  - GEOCODING_PROVIDER=nominatim
```

## 📊 Monitoreo

### Ver Logs
```bash
# Todos los servicios
docker compose logs -f

# Solo la API
docker compose logs -f ruteo-api

# Solo Redis
docker compose logs -f ruteo-redis

# Últimas 100 líneas
docker compose logs --tail=100
```

### Ver Estado
```bash
# Estado de servicios
docker compose ps

# Uso de recursos
docker stats ruteo-api ruteo-redis
```

## 🚨 Troubleshooting

### Puerto 8080 ocupado
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8081:8000"  # Usar 8081
```

### Contenedor no inicia
```bash
# Ver logs
docker compose logs ruteo-api

# Reiniciar desde cero
docker compose down -v
docker compose up -d --build
```

### Limpiar y empezar de nuevo
```bash
# Con scripts
./docker-start.sh clean     # Linux/Mac
.\docker-start.ps1 clean    # Windows

# Con docker compose
docker compose down -v
rm -rf cache/* logs/*
docker compose up -d --build
```

## 📖 Más Información

- **Documentación completa**: [DOCKER.md](DOCKER.md)
- **API Docs**: http://localhost:8080/docs
- **Configuración**: [.env.example](.env.example)

## 🎯 Ventajas de Docker

✅ **Portabilidad**: Funciona en cualquier máquina  
✅ **Aislamiento**: No afecta tu sistema  
✅ **Consistencia**: Mismo ambiente en dev y prod  
✅ **Simplicidad**: Un solo comando para levantar todo  
✅ **Escalabilidad**: Fácil de replicar y escalar  

---

**¿Problemas?** Abre un issue en [GitHub](https://github.com/Riogas/ruteo/issues)
