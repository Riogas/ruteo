# 📋 Sistema de Logging Robusto - Documentación

## 🎯 Características

### ✅ Lo que se registra:

1. **Requests completos**:
   - Timestamp (ISO 8601)
   - Método HTTP (GET, POST, etc.)
   - Path y query parameters
   - IP del cliente (real, considerando proxies)
   - User-Agent
   - Referer
   - Body del request (JSON, truncado si es muy largo)

2. **Responses**:
   - Status code
   - Tiempo de ejecución (ms)
   - Success/failure

3. **Metadata**:
   - Endpoint específico
   - Errores (si ocurren)

---

## 📁 Estructura de Logs

```
/home/riogas/ruteo/logs/
├── requests/
│   ├── requests.log              # Log activo de todos los requests
│   ├── requests_20251028_172120.log.gz  # Logs archivados
│   └── requests_20251028_153045.log.gz
├── endpoints/
│   ├── geocode.log               # Log específico del endpoint geocode
│   ├── reverse_geocode.log       # Log específico de reverse-geocode
│   ├── optimize_route.log        # Log específico de optimize-route
│   └── assign_order.log          # Log específico de assign-order
├── deploy.log                    # Log actual del deployment
├── deploy_20251028_172120.log.gz  # Logs de deployments anteriores
└── api.log                       # Log general de la aplicación
```

---

## 🔄 Rotación Automática

### ¿Cuándo se rotan los logs?

**Antes de cada deploy** (git push):
1. Se ejecuta `rotate-logs.sh`
2. Cada archivo `.log` se renombra a `.log_YYYYMMDD_HHMMSS`
3. Los archivos renombrados se comprimen (`.gz`)
4. Se crean nuevos archivos vacíos
5. Logs antiguos (>30 días) se eliminan automáticamente

### Ejemplo de rotación:

```bash
# Antes del deploy
logs/requests/requests.log  (100 MB)

# Después del deploy
logs/requests/requests.log  (vacío - nuevo deploy)
logs/requests/requests_20251028_172120.log.gz  (10 MB comprimido)
```

---

## 📊 Formato de Logs

### Log de Requests (`requests/requests.log`)

Cada línea es un JSON con este formato:

```json
{
  "timestamp": "2025-10-28T17:21:30.123456",
  "method": "POST",
  "path": "/api/v1/geocode",
  "query_params": {},
  "client_ip": "200.123.45.67",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
  "referer": "https://mi-app.com/mapa",
  "request_body": {
    "street": "Av. 18 de Julio",
    "number": "1234",
    "city": "Montevideo",
    "country": "Uruguay"
  },
  "status_code": 200,
  "duration_ms": 245.67,
  "success": true
}
```

### Log de Endpoints (`endpoints/geocode.log`)

Formato más detallado con request y response completos:

```json
{
  "timestamp": "2025-10-28T17:21:30.123456",
  "endpoint": "geocode",
  "client_ip": "200.123.45.67",
  "request": {
    "street": "Av. 18 de Julio",
    "number": "1234",
    "city": "Montevideo",
    "country": "Uruguay"
  },
  "response": {
    "latitude": -34.9032,
    "longitude": -56.1882,
    "confidence": 0.95
  },
  "error": null,
  "duration_ms": 245.67,
  "success": true
}
```

---

## 🔍 Cómo Ver los Logs

### 1. Ver logs en tiempo real

```bash
# Todos los requests
tail -f ~/ruteo/logs/requests/requests.log

# Endpoint específico
tail -f ~/ruteo/logs/endpoints/geocode.log

# Deployment
tail -f ~/ruteo/logs/deploy.log
```

### 2. Buscar requests específicos

```bash
# Buscar por IP
grep "200.123.45.67" ~/ruteo/logs/requests/requests.log

# Buscar errores (status >= 400)
grep '"status_code": [45][0-9][0-9]' ~/ruteo/logs/requests/requests.log

# Buscar requests lentos (>1000ms)
grep '"duration_ms": [0-9][0-9][0-9][0-9]' ~/ruteo/logs/requests/requests.log

# Buscar por endpoint
grep '"/api/v1/geocode"' ~/ruteo/logs/requests/requests.log
```

### 3. Ver logs archivados

```bash
# Listar logs archivados
ls -lh ~/ruteo/logs/requests/*.gz

# Ver contenido de log comprimido
zcat ~/ruteo/logs/requests/requests_20251028_172120.log.gz | tail -100

# Buscar en logs archivados
zgrep "error" ~/ruteo/logs/requests/*.gz
```

### 4. Estadísticas

```bash
# Contar requests por endpoint
cat ~/ruteo/logs/requests/requests.log | jq -r '.path' | sort | uniq -c

# Promedio de duración
cat ~/ruteo/logs/requests/requests.log | jq '.duration_ms' | awk '{sum+=$1; count++} END {print sum/count}'

# IPs más activas
cat ~/ruteo/logs/requests/requests.log | jq -r '.client_ip' | sort | uniq -c | sort -rn | head -10

# Distribución de status codes
cat ~/ruteo/logs/requests/requests.log | jq -r '.status_code' | sort | uniq -c
```

---

## 🛠️ Herramientas Útiles

### Script para analizar logs:

```bash
#!/bin/bash
# ~/ruteo/analyze-logs.sh

LOG_FILE="$HOME/ruteo/logs/requests/requests.log"

echo "📊 Análisis de Logs - $(date)"
echo "================================"
echo ""

echo "🔢 Total de requests:"
wc -l < "$LOG_FILE"
echo ""

echo "📍 Top 10 endpoints más usados:"
cat "$LOG_FILE" | jq -r '.path' | sort | uniq -c | sort -rn | head -10
echo ""

echo "⏱️ Requests más lentos:"
cat "$LOG_FILE" | jq -s 'sort_by(.duration_ms) | reverse | .[0:5]' | jq -r '.[] | "\(.duration_ms)ms - \(.method) \(.path)"'
echo ""

echo "❌ Errores (status >= 400):"
cat "$LOG_FILE" | jq 'select(.status_code >= 400)' | jq -r '"\(.timestamp) - \(.status_code) - \(.path)"' | tail -10
echo ""

echo "🌍 Top 5 IPs:"
cat "$LOG_FILE" | jq -r '.client_ip' | sort | uniq -c | sort -rn | head -5
```

---

## 🧹 Mantenimiento

### Limpieza manual de logs antiguos:

```bash
# Eliminar logs comprimidos de más de 60 días
find ~/ruteo/logs -name "*.gz" -mtime +60 -delete

# Ver espacio usado por logs
du -sh ~/ruteo/logs/*

# Limpiar logs activos (¡CUIDADO!)
# Solo si es necesario y con precaución
> ~/ruteo/logs/requests/requests.log
```

### Cambiar retención de logs:

Edita `app/rotate-logs.sh` y cambia la línea:

```bash
# De 30 días a 90 días
find "$LOG_BASE" -name "*.log.gz" -type f -mtime +90 -delete
```

---

## 🔐 Privacidad y Seguridad

### ⚠️ Importante:

1. **Los logs contienen datos sensibles**: IPs, payloads, etc.
2. **No expongas los logs públicamente**
3. **Limita el acceso**: Solo usuarios autorizados deben leerlos
4. **Cumple con GDPR/LGPD**: Si aplica, anonimiza IPs después de X días

### Anonimizar IPs en logs:

```bash
# Reemplazar IPs por hash
sed -i 's/"client_ip": "[^"]*"/"client_ip": "REDACTED"/g' ~/ruteo/logs/requests/*.log
```

---

## 📈 Monitoreo en Producción

### Alertas recomendadas:

1. **Tasa de errores alta** (>5% de requests con status >= 500)
2. **Requests muy lentos** (>5 segundos)
3. **Uso de disco** (logs >80% del espacio disponible)
4. **Picos de tráfico** (>1000 requests/minuto)

### Integración con herramientas:

- **Grafana**: Visualizar métricas de logs
- **ELK Stack**: Elasticsearch + Kibana para análisis avanzado
- **Prometheus**: Métricas agregadas
- **Sentry**: Alertas de errores en tiempo real

---

## ✅ Checklist de Verificación

Después de configurar el sistema:

- [ ] Logs de requests se están generando
- [ ] Rotación automática funciona al hacer deploy
- [ ] Logs antiguos se comprimen correctamente
- [ ] Logs muy antiguos se eliminan
- [ ] Puedes buscar y filtrar logs fácilmente
- [ ] El espacio en disco está bajo control
- [ ] Solo usuarios autorizados tienen acceso

---

## 🆘 Troubleshooting

### Logs no se generan:

```bash
# Verificar permisos
ls -la ~/ruteo/logs/

# Crear directorios si no existen
mkdir -p ~/ruteo/logs/requests ~/ruteo/logs/endpoints

# Dar permisos al usuario docker
sudo chown -R riogas:docker ~/ruteo/logs
```

### Error de espacio en disco:

```bash
# Ver espacio disponible
df -h

# Limpiar logs antiguos manualmente
find ~/ruteo/logs -name "*.gz" -mtime +7 -delete

# Ver archivos más grandes
du -sh ~/ruteo/logs/* | sort -rh
```

### Rotación no funciona:

```bash
# Ejecutar manualmente
bash ~/ruteo/app/rotate-logs.sh

# Verificar permisos de ejecución
chmod +x ~/ruteo/app/rotate-logs.sh

# Ver logs de error
journalctl -u webhook -n 50 | grep rotate
```

---

¿Preguntas? Consulta el código fuente en:
- `app/middleware/logging.py` - Middleware de logging
- `app/rotate-logs.sh` - Script de rotación
- `app/auto-deploy.sh` - Auto-deploy con rotación

