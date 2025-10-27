# 🎯 Ejemplos Prácticos - Sistema con Docker

## Escenario 1: Desarrollador Local

**Objetivo**: Probar el sistema en tu laptop

```bash
# 1. Clonar
git clone https://github.com/Riogas/ruteo.git
cd ruteo

# 2. Levantar
docker compose up -d

# 3. Probar
curl http://localhost:8080/health

# 4. Ver documentación interactiva
# Abrir en navegador: http://localhost:8080/docs

# 5. Cuando termines
docker compose down
```

---

## Escenario 2: Servidor de Pruebas

**Objetivo**: Instalar en servidor Ubuntu para equipo

```bash
# En el servidor (vía SSH)
ssh usuario@servidor.com

# Instalar Docker si no está
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clonar proyecto
git clone https://github.com/Riogas/ruteo.git
cd ruteo

# Levantar
docker compose up -d

# Verificar
curl http://localhost:8080/health

# Ver logs
docker compose logs -f

# Acceder desde otra máquina
# http://IP_SERVIDOR:8080
```

---

## Escenario 3: Servidor de Producción con Nginx

**Objetivo**: Despliegue profesional con dominio y HTTPS

### Paso 1: Instalar en servidor
```bash
ssh usuario@servidor.com
git clone https://github.com/Riogas/ruteo.git
cd ruteo

# Levantar
docker compose up -d
```

### Paso 2: Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/ruteo
```

Contenido:
```nginx
server {
    listen 80;
    server_name ruteo.tudominio.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/ruteo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Paso 3: Obtener HTTPS con Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ruteo.tudominio.com
```

**Resultado**: https://ruteo.tudominio.com (con SSL)

---

## Escenario 4: Múltiples Ambientes

**Objetivo**: Dev, Staging, Producción en un mismo servidor

```bash
# Estructura
/opt/ruteo-dev/
/opt/ruteo-staging/
/opt/ruteo-prod/
```

### Dev (Puerto 8080)
```bash
cd /opt/ruteo-dev
git clone https://github.com/Riogas/ruteo.git .
# Editar docker-compose.yml: puerto 8080
docker compose up -d
```

### Staging (Puerto 8081)
```bash
cd /opt/ruteo-staging
git clone https://github.com/Riogas/ruteo.git .
# Editar docker-compose.yml: puerto 8081
docker compose up -d
```

### Producción (Puerto 8082)
```bash
cd /opt/ruteo-prod
git clone https://github.com/Riogas/ruteo.git .
# Editar docker-compose.yml: puerto 8082
docker compose up -d
```

---

## Escenario 5: CI/CD con GitHub Actions

**Objetivo**: Despliegue automático al hacer push

Crear `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/ruteo
            git pull origin main
            docker compose down
            docker compose up -d --build
```

Configurar secrets en GitHub:
- `SERVER_HOST`: IP del servidor
- `SERVER_USER`: usuario SSH
- `SSH_PRIVATE_KEY`: clave privada SSH

---

## Escenario 6: Monitoreo con Logs

**Objetivo**: Monitorear uso y errores

### Logs en tiempo real
```bash
# Todos los servicios
docker compose logs -f

# Solo API
docker compose logs -f ruteo-api

# Filtrar errores
docker compose logs | grep ERROR

# Últimas 100 líneas
docker compose logs --tail=100
```

### Exportar logs
```bash
# A archivo
docker compose logs > logs_$(date +%Y%m%d).txt

# Comprimir
docker compose logs | gzip > logs_$(date +%Y%m%d).txt.gz
```

### Rotar logs automáticamente
Crear script `rotate-logs.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
docker compose logs > /backups/logs_$DATE.txt
find /backups -name "logs_*.txt" -mtime +30 -delete
```

Cronjob diario:
```bash
crontab -e
# Agregar:
0 0 * * * /opt/ruteo/rotate-logs.sh
```

---

## Escenario 7: Backup y Restore

**Objetivo**: Proteger datos

### Backup Manual
```bash
# Crear directorio
mkdir -p /backups/ruteo

# Backup de datos
tar -czf /backups/ruteo/backup_$(date +%Y%m%d).tar.gz \
    logs cache

# Backup de Redis
docker compose exec ruteo-redis redis-cli SAVE
docker cp ruteo-redis:/data/dump.rdb /backups/ruteo/redis_$(date +%Y%m%d).rdb
```

### Backup Automático
Script `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backups/ruteo"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Datos
tar -czf $BACKUP_DIR/data_$DATE.tar.gz logs cache

# Redis
docker compose exec ruteo-redis redis-cli SAVE
docker cp ruteo-redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Limpiar backups antiguos (>7 días)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete
```

Cronjob:
```bash
0 2 * * * /opt/ruteo/backup.sh
```

### Restore
```bash
# Detener servicios
docker compose down

# Restaurar datos
tar -xzf /backups/ruteo/data_20250127.tar.gz

# Restaurar Redis
docker cp /backups/ruteo/redis_20250127.rdb ruteo-redis:/data/dump.rdb

# Reiniciar
docker compose up -d
```

---

## Escenario 8: Escalar con Múltiples Workers

**Objetivo**: Manejar más carga

Editar `docker-compose.yml`:
```yaml
services:
  ruteo-api:
    # ... configuración existente ...
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

O escalar con replicas:
```bash
docker compose up -d --scale ruteo-api=3
```

---

## Escenario 9: Debugging en Producción

**Objetivo**: Resolver problemas sin bajar el servicio

### Entrar al contenedor
```bash
# Shell interactivo
docker compose exec ruteo-api bash

# Ver procesos
docker compose top

# Ver recursos
docker stats ruteo-api
```

### Ejecutar comandos
```bash
# Ver versión de Python
docker compose exec ruteo-api python --version

# Listar archivos
docker compose exec ruteo-api ls -la /app

# Ver variables de entorno
docker compose exec ruteo-api env

# Probar conexión a Redis
docker compose exec ruteo-api curl http://ruteo-redis:6379
```

### Probar API dentro del contenedor
```bash
docker compose exec ruteo-api curl http://localhost:8000/health
```

---

## Escenario 10: Migrar a Otro Servidor

**Objetivo**: Mover sistema completo

### En servidor original
```bash
# Backup completo
cd /opt/ruteo
tar -czf ruteo-complete.tar.gz .

# Copiar a nuevo servidor
scp ruteo-complete.tar.gz usuario@nuevo-servidor:/opt/
```

### En servidor nuevo
```bash
# Extraer
cd /opt
tar -xzf ruteo-complete.tar.gz
mv ruteo-complete ruteo

# Levantar
cd ruteo
docker compose up -d

# Verificar
curl http://localhost:8080/health
```

---

## Escenario 11: Actualizar Sistema

**Objetivo**: Aplicar nuevas versiones

### Método 1: Con script
```bash
./docker-start.sh down
git pull origin main
./docker-start.sh build
./docker-start.sh up
```

### Método 2: Con Make
```bash
make update
```

### Método 3: Manual
```bash
docker compose down
git pull origin main
docker compose build --no-cache
docker compose up -d
```

### Verificar actualización
```bash
docker compose exec ruteo-api python -c "import app; print(app.__version__)"
```

---

## Escenario 12: Health Monitoring

**Objetivo**: Monitorear salud 24/7

### Script de monitoreo
`monitor.sh`:
```bash
#!/bin/bash
while true; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
    
    if [ "$STATUS" != "200" ]; then
        echo "$(date): API DOWN (Status: $STATUS)" >> monitor.log
        # Enviar alerta (email, Slack, etc.)
        ./send-alert.sh "API is down!"
        
        # Reintentar reiniciar
        docker compose restart ruteo-api
    else
        echo "$(date): API OK" >> monitor.log
    fi
    
    sleep 60  # Verificar cada minuto
done
```

### Ejecutar en background
```bash
nohup ./monitor.sh &
```

---

## Tips Finales

### Ver información del sistema
```bash
# Versión de Docker
docker --version

# Imágenes locales
docker images | grep ruteo

# Contenedores activos
docker ps | grep ruteo

# Espacio usado
docker system df

# Información de contenedor
docker inspect ruteo-api
```

### Limpieza periódica
```bash
# Limpiar contenedores detenidos
docker container prune -f

# Limpiar imágenes no usadas
docker image prune -a -f

# Limpiar volúmenes no usados
docker volume prune -f

# Limpieza completa
docker system prune -a --volumes -f
```

### Performance tuning
```bash
# Ver uso de recursos
docker stats --no-stream

# Límites personalizados en docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 512M
```

---

**¿Más escenarios?** Abre un issue en GitHub con tu caso de uso!
