# 🚀 Scripts de Gestión del Servidor

Este directorio contiene scripts PowerShell para facilitar la gestión del servidor FastAPI.

## 📜 Scripts Disponibles

### 1. `restart_server.ps1` - Reinicio Completo
**Uso:**
```powershell
.\restart_server.ps1
```

**Qué hace:**
1. Limpia cache de Python (`__pycache__`, `*.pyc`)
2. Detiene procesos Python anteriores del proyecto
3. Inicia un nuevo servidor en ventana separada
4. Verifica que el servidor esté activo (health check)
5. Muestra URLs disponibles

**Cuándo usar:**
- Después de cambiar código en `app/`
- Después de modificar modelos o endpoints
- Cuando el servidor tiene errores y necesitas reinicio limpio

---

### 2. `start_server_simple.ps1` - Inicio Simple
**Uso:**
```powershell
.\start_server_simple.ps1
```

**Qué hace:**
1. Inicia el servidor en ventana separada
2. Verifica que el servidor esté activo
3. Muestra URLs disponibles

**Cuándo usar:**
- Primera vez que inicias el servidor
- No hay procesos anteriores corriendo

---

### 3. `start_server.py` - Inicio Directo (Python)
**Uso:**
```powershell
.\venv\Scripts\python.exe start_server.py
```

**Qué hace:**
- Inicia uvicorn directamente en la terminal actual
- Modo blocking (no abre ventana nueva)

**Cuándo usar:**
- Cuando quieres ver logs en tiempo real en la misma ventana
- Para debugging detallado

---

## 🌐 URLs del Servidor

Una vez iniciado, el servidor está disponible en:

- **API Base:** http://localhost:8080
- **Health Check:** http://localhost:8080/health
- **Documentación Interactiva (Swagger):** http://localhost:8080/docs
- **Documentación Alternativa (ReDoc):** http://localhost:8080/redoc

---

## 🔧 Comandos Rápidos

### Verificar si el servidor está corriendo:
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/health"
```

### Detener todos los procesos Python del proyecto:
```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*ruteo*" } | Stop-Process -Force
```

### Limpiar cache de Python:
```powershell
Get-ChildItem -Path . -Directory -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Filter "*.pyc" -Recurse | Remove-Item -Force
```

---

## 💡 Troubleshooting

### El servidor no inicia:
1. Verifica que el ambiente virtual esté activado: `.\venv\Scripts\Activate.ps1`
2. Verifica dependencias: `pip install -r requirements.txt`
3. Revisa logs en la ventana del servidor

### Puerto 8080 ocupado:
```powershell
# Ver qué está usando el puerto
Get-NetTCPConnection -LocalPort 8080 | Select-Object OwningProcess, State
```

### Cambios no se reflejan:
1. Usa `.\restart_server.ps1` (limpia cache automáticamente)
2. Si persiste, reinicia manualmente el servidor en su ventana

---

## 📝 Notas

- El servidor usa **auto-reload** por defecto (detecta cambios automáticamente)
- Los scripts abren el servidor en **ventana separada** para no bloquear tu terminal
- El **health check** verifica que el servidor responda antes de confirmar éxito

---

## 🆕 Cambios Recientes

### Reverse Geocoding con Detección Geométrica de Esquinas (27 Oct 2025)
- ✅ Implementado algoritmo geométrico con Overpass API + Shapely
- ✅ Radio de búsqueda: 100 metros
- ✅ Preferencia por calle principal detectada por Nominatim
- ✅ Fallback automático si Overpass no disponible
- ✅ Precisión: ±1-50 metros (geométrico) o ±50-200m (fallback)

Para probar:
```bash
# Reverse geocoding con esquinas
curl -X POST "http://localhost:8080/api/geocoding/reverse" \
  -H "Content-Type: application/json" \
  -d '{"lat": -34.906067, "lon": -56.193614}'

# Respuesta esperada incluye corner_1 y corner_2
```
