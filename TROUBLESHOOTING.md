# 🛠️ Guía de Solución de Problemas

## Problemas Comunes y Soluciones

### 1. Error al instalar dependencias

#### Problema: Error con `osmnx` o librerías geoespaciales

**Windows:**
```powershell
# Instalar Visual C++ Build Tools
# Descargar desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# O instalar conda y usar conda-forge
conda install -c conda-forge osmnx
```

**Solución alternativa:**
Usar Docker (evita problemas de compilación):
```powershell
docker-compose up -d
```

#### Problema: Error con `ortools`

```powershell
# OR-Tools requiere Python 3.8-3.11
python --version  # Verificar versión

# Si tienes Python 3.12+, instala 3.11:
# Descargar desde: https://www.python.org/downloads/
```

### 2. Problemas de geocodificación

#### Problema: "No se pudo geocodificar la dirección"

**Solución 1**: Proporcionar coordenadas directamente
```python
{
    "order": {
        "delivery_location": {"lat": -34.603722, "lon": -58.381592}
    }
}
```

**Solución 2**: Configurar API key de Google Maps
```powershell
# Editar .env
GOOGLE_MAPS_API_KEY=tu_api_key_aqui
```

**Solución 3**: Esperar y reintentar (Nominatim tiene rate limit)
```python
# El sistema reintenta automáticamente con otros proveedores
```

### 3. Problemas con OSMnx

#### Problema: "No se puede descargar el mapa"

**Causa**: Primera vez tarda en descargar mapas de OSM

**Solución**: Esperar 1-2 minutos en la primera ejecución
```
[INFO] Descargando grafo desde OSM para Buenos Aires...
[Esperar pacientemente...]
[INFO] ✓ Grafo descargado: 12,345 nodos
```

**Cache**: Las siguientes ejecuciones son instantáneas

#### Problema: Error de red al descargar mapas

```powershell
# Verificar conexión a internet
ping overpass-api.de

# Limpiar cache si está corrupto
Remove-Item -Recurse cache\osm\*
```

### 4. Puerto en uso

#### Problema: "Address already in use: port 8000"

```powershell
# Opción 1: Matar proceso en puerto 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Opción 2: Usar otro puerto
# Editar .env
PORT=8001
```

### 5. Entorno virtual

#### Problema: `venv\Scripts\activate` no funciona

**PowerShell Execution Policy:**
```powershell
# Ver política actual
Get-ExecutionPolicy

# Cambiar temporalmente
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activar entorno
.\venv\Scripts\activate
```

**Alternativa:**
```powershell
# Usar activate.bat en cmd
venv\Scripts\activate.bat
```

### 6. Dependencias faltantes

#### Problema: "No module named 'xxx'"

```powershell
# Verificar entorno activo
# Debe decir (venv) al inicio de la línea

# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt
```

### 7. Memoria insuficiente

#### Problema: MemoryError al cargar mapas grandes

**Solución 1**: Reducir área de búsqueda
```python
# En routing.py, cambiar:
radius_meters=10000  # En vez de 20000
```

**Solución 2**: Usar Docker con más memoria
```yaml
# En docker-compose.yml
services:
  ruteo-api:
    mem_limit: 2g
```

### 8. Logs no se generan

#### Problema: No se crean archivos de log

```powershell
# Verificar que existe el directorio
if (!(Test-Path logs)) { New-Item -ItemType Directory -Path logs }

# Verificar permisos
icacls logs
```

### 9. API no responde

#### Problema: Request timeout

**Checklist:**
1. ✅ Servidor está corriendo: `run.bat`
2. ✅ Puerto correcto: `http://localhost:8000`
3. ✅ Firewall no bloquea: Permitir Python en firewall
4. ✅ Ver logs: `type logs\api.log`

### 10. Tests fallan

#### Problema: pytest no encuentra módulos

```powershell
# Asegurar que estás en el directorio correcto
cd ruteo

# Instalar en modo desarrollo
pip install -e .

# Ejecutar tests
pytest tests/ -v
```

---

## 🔍 Debugging

### Habilitar logging detallado

**En .env:**
```
DEBUG=True
LOG_LEVEL=DEBUG
```

**Logs en tiempo real:**
```powershell
# Windows PowerShell
Get-Content logs\api.log -Wait

# CMD
type logs\api.log
```

### Ver requests HTTP

```python
# En test_api.py o tu código
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Verificar configuración

```python
# En Python REPL
from app.models import SystemConfig
config = SystemConfig()
print(config.model_dump())
```

---

## 📞 Obtener Ayuda

### 1. Verificar documentación
- **README.md** - Información general
- **QUICKSTART.md** - Inicio rápido
- **ARCHITECTURE.md** - Detalles técnicos
- **API Docs** - http://localhost:8000/docs

### 2. Revisar logs
```powershell
# Ver últimas 50 líneas
Get-Content logs\api.log -Tail 50
```

### 3. Modo debug interactivo
```python
# Ejecutar ejemplo paso a paso
python
>>> from example_usage import *
>>> # Ejecutar línea por línea
```

### 4. Verificar versiones
```powershell
python --version
pip list | findstr fastapi
pip list | findstr osmnx
pip list | findstr ortools
```

---

## ✅ Checklist de Instalación

Antes de reportar un problema, verifica:

- [ ] Python 3.10+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas: `pip list`
- [ ] Archivo .env existe
- [ ] Puerto 8000 libre
- [ ] Conexión a internet (para descargar mapas)
- [ ] Permisos de escritura en `logs/` y `cache/`
- [ ] Firewall permite Python

---

## 🚀 Si todo falla: Reinicio limpio

```powershell
# 1. Eliminar entorno virtual
Remove-Item -Recurse venv

# 2. Limpiar cache
Remove-Item -Recurse cache\*
Remove-Item -Recurse logs\*

# 3. Reinstalar desde cero
.\install.bat

# 4. Probar
.\run.bat
```

---

## 🐳 Usar Docker (Sin problemas de dependencias)

```powershell
# Instalar Docker Desktop
# https://www.docker.com/products/docker-desktop/

# Ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

---

Si ninguna solución funciona, revisa los logs en detalle:
```powershell
type logs\api.log | findstr ERROR
```

Y comparte el mensaje de error específico para obtener ayuda más precisa.
