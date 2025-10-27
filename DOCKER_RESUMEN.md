# 🎉 ¡Sistema de Ruteo - Docker Configurado!

## ✅ ¿Qué se ha creado?

### 📁 Archivos Nuevos

1. **Dockerfile** (Multi-stage, optimizado, seguro)
   - Build en 2 etapas para imagen pequeña
   - Usuario no-root por seguridad
   - Health check integrado
   - Soporte para múltiples workers

2. **docker-compose.yml** (Completo con todos los servicios)
   - API de Ruteo (Puerto 8080)
   - Redis para cache (Puerto 6379)
   - Health checks automáticos
   - Volúmenes persistentes
   - Límites de recursos configurables

3. **.dockerignore** (Optimización de build)
   - Excluye archivos innecesarios
   - Reduce tamaño de imagen
   - Build más rápido

4. **docker-start.sh** (Script Linux/Mac)
   - Comandos: up, down, restart, logs, status, test, clean
   - Colores y emojis
   - Tests automáticos

5. **docker-start.ps1** (Script Windows)
   - Misma funcionalidad que .sh
   - Nativo para PowerShell
   - Fácil de usar

6. **Makefile** (Para usuarios de Make)
   - 20+ comandos útiles
   - Simplifica operaciones comunes
   - Documentación incluida

7. **DOCKER.md** (Documentación completa - 400+ líneas)
   - Guía de inicio
   - Configuración avanzada
   - Troubleshooting
   - Despliegue en cloud (AWS, GCP, Azure)
   - Monitoreo y seguridad

8. **DOCKER_QUICKSTART.md** (Inicio rápido)
   - Instalación en 30 segundos
   - Comandos esenciales
   - Tests rápidos

9. **.env.example** (Mejorado)
   - Más variables de configuración
   - Comentarios explicativos
   - Valores por defecto seguros

10. **README.md** (Actualizado)
    - Docker como opción #1
    - Enlaces a documentación
    - Instrucciones claras

## 🚀 Cómo Usar

### Inicio Instantáneo (Cualquier máquina)

```bash
# 1. Clonar
git clone https://github.com/Riogas/ruteo.git
cd ruteo

# 2. Levantar (¡UN SOLO COMANDO!)
docker compose up -d

# 3. Verificar
curl http://localhost:8080/health
```

### Comandos Disponibles

#### Opción A: Docker Compose (Universal)
```bash
docker compose up -d      # Iniciar
docker compose logs -f    # Ver logs
docker compose ps         # Ver estado
docker compose down       # Detener
```

#### Opción B: Scripts de Ayuda (Recomendado)

**Linux/Mac:**
```bash
./docker-start.sh up      # Iniciar
./docker-start.sh logs    # Ver logs
./docker-start.sh test    # Tests automáticos
./docker-start.sh status  # Estado + recursos
./docker-start.sh down    # Detener
./docker-start.sh clean   # Limpiar todo
./docker-start.sh help    # Ver ayuda
```

**Windows:**
```powershell
.\docker-start.ps1 up     # Iniciar
.\docker-start.ps1 logs   # Ver logs
.\docker-start.ps1 test   # Tests automáticos
.\docker-start.ps1 status # Estado + recursos
.\docker-start.ps1 down   # Detener
.\docker-start.ps1 clean  # Limpiar todo
.\docker-start.ps1 help   # Ver ayuda
```

#### Opción C: Make (Linux/Mac)
```bash
make install    # Primera instalación (build + up + test)
make up         # Iniciar
make logs       # Ver logs
make test       # Ejecutar tests
make status     # Ver estado
make down       # Detener
make clean      # Limpiar
make help       # Ver todos los comandos (20+)
```

## 🎯 Servicios Incluidos

### 1. ruteo-api (API Principal)
- **Puerto**: 8080 (host) → 8000 (contenedor)
- **Endpoints**:
  - http://localhost:8080/health
  - http://localhost:8080/docs
  - http://localhost:8080/api/v1/geocode
  - http://localhost:8080/api/v1/reverse-geocode
  - http://localhost:8080/api/v1/optimize-routes
- **Features**:
  - Geocodificación forward y reverse
  - Detección de esquinas geométrica
  - Optimización de rutas
  - 2 workers por defecto

### 2. ruteo-redis (Cache)
- **Puerto**: 6379
- **Uso**: Cache de geocoding y resultados
- **Configuración**: 256MB max, LRU eviction
- **Persistencia**: Volumen Docker

## 📊 Arquitectura Docker

```
┌─────────────────────────────────────────┐
│         Docker Compose Stack            │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  ruteo-api   │───▶│ ruteo-redis  │  │
│  │  (FastAPI)   │    │   (Cache)    │  │
│  └──────┬───────┘    └──────────────┘  │
│         │                               │
│         ▼                               │
│  ┌──────────────────────────────────┐  │
│  │   Volúmenes Persistentes:        │  │
│  │   - ./logs                       │  │
│  │   - ./cache                      │  │
│  │   - redis-data (Docker volume)   │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
         │
         ▼
   Port 8080 (Host)
```

## 🔧 Personalización

### Cambiar Puerto
Edita `docker-compose.yml`:
```yaml
ports:
  - "3000:8000"  # Usa puerto 3000 en vez de 8080
```

### Ajustar Recursos
Edita `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Máximo 4 CPUs
      memory: 4G     # Máximo 4GB RAM
```

### Variables de Entorno
Edita `docker-compose.yml` en `environment`:
```yaml
- DEBUG=False
- LOG_LEVEL=INFO
- GEOCODING_PROVIDER=nominatim
- ENABLE_CACHE=true
```

## 🧪 Tests Incluidos

Los scripts ejecutan automáticamente:
1. ✅ Health check de la API
2. ✅ Geocoding forward
3. ✅ Geocoding reverse
4. ✅ Verificación de servicios

```bash
# Ejecutar tests
./docker-start.sh test      # Linux/Mac
.\docker-start.ps1 test     # Windows
make test                   # Con Make
```

## 📦 Despliegue en Producción

### Servidor Local
```bash
# En tu servidor
git clone https://github.com/Riogas/ruteo.git
cd ruteo
docker compose up -d

# Acceder desde otras máquinas
# http://TU_IP:8080
```

### Cloud (AWS, GCP, Azure)
Ver documentación completa en [DOCKER.md](DOCKER.md) sección "Despliegue en Cloud"

### Con Nginx (Reverse Proxy)
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

## 🛡️ Seguridad

✅ **Usuario no-root**: Contenedor corre con usuario `ruteo` (UID 1000)  
✅ **Multi-stage build**: Imagen final sin herramientas de compilación  
✅ **Health checks**: Monitoreo automático de servicios  
✅ **Red aislada**: Servicios en red bridge privada  
✅ **Volúmenes**: Datos persistentes fuera del contenedor  

## 📈 Monitoreo

```bash
# Ver logs en tiempo real
docker compose logs -f

# Ver uso de recursos
docker stats ruteo-api ruteo-redis

# Ver estado de health
docker compose ps
```

## 🚨 Troubleshooting Rápido

### Puerto ocupado
```bash
# Ver qué usa el puerto 8080
netstat -ano | findstr :8080  # Windows
lsof -i :8080                 # Linux/Mac

# Cambiar puerto en docker-compose.yml
```

### Contenedor no inicia
```bash
# Ver logs de error
docker compose logs ruteo-api

# Reiniciar desde cero
docker compose down -v
docker compose up -d --build
```

### Limpiar y empezar de nuevo
```bash
./docker-start.sh clean      # Linux/Mac
.\docker-start.ps1 clean     # Windows
make clean                   # Con Make
```

## 📚 Documentación

- **[DOCKER.md](DOCKER.md)** - Documentación completa (400+ líneas)
- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - Inicio rápido
- **[README.md](README.md)** - Documentación general
- **[API Docs](http://localhost:8080/docs)** - Documentación interactiva

## 🎁 Ventajas de Esta Configuración

✅ **Un solo comando**: `docker compose up -d`  
✅ **Portátil**: Funciona en Windows, Linux, Mac  
✅ **Optimizado**: Imagen pequeña (<500MB)  
✅ **Seguro**: Usuario no-root, health checks  
✅ **Completo**: Incluye cache Redis  
✅ **Documentado**: 3 archivos de documentación  
✅ **Scripts incluidos**: Automatización lista  
✅ **Listo para producción**: Configuración profesional  

## 🚀 Próximos Pasos

1. **Probar localmente**:
   ```bash
   docker compose up -d
   curl http://localhost:8080/health
   ```

2. **Desplegar en servidor**:
   ```bash
   ssh usuario@tu-servidor
   git clone https://github.com/Riogas/ruteo.git
   cd ruteo
   docker compose up -d
   ```

3. **Configurar dominio** (opcional):
   - Configurar Nginx como reverse proxy
   - Obtener certificado SSL con Let's Encrypt
   - Apuntar dominio a tu servidor

4. **Monitorear**:
   ```bash
   docker compose logs -f
   docker stats
   ```

## 📞 Soporte

- **GitHub**: https://github.com/Riogas/ruteo
- **Issues**: https://github.com/Riogas/ruteo/issues
- **Docs API**: http://localhost:8080/docs

---

## ✨ ¡Todo Listo!

Tu sistema de ruteo ahora puede:
- ✅ Desplegarse en cualquier máquina con Docker
- ✅ Levantarse con un solo comando
- ✅ Escalarse fácilmente
- ✅ Monitorearse automáticamente
- ✅ Moverse de un servidor a otro sin problemas

**¡Disfruta tu sistema de ruteo containerizado!** 🎉🚀
