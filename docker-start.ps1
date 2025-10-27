# ============================================
# Script de inicio rápido para Docker (Windows)
# ============================================
# Uso: .\docker-start.ps1 [comando]
# Comandos: up, down, restart, logs, status

param(
    [string]$Command = "up"
)

# Colores
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Banner
Write-Host ""
Write-ColorOutput "╔════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║   Sistema de Ruteo - Docker Manager   ║" "Cyan"
Write-ColorOutput "╚════════════════════════════════════════╝" "Cyan"
Write-Host ""

# Verificar que Docker está instalado
try {
    $dockerVersion = docker --version
    Write-ColorOutput "✅ Docker instalado: $dockerVersion" "Green"
} catch {
    Write-ColorOutput "❌ Docker no está instalado" "Red"
    Write-Host "Por favor instala Docker Desktop desde: https://docs.docker.com/desktop/install/windows-install/"
    exit 1
}

try {
    $composeVersion = docker compose version
    Write-ColorOutput "✅ Docker Compose instalado: $composeVersion" "Green"
} catch {
    Write-ColorOutput "❌ Docker Compose no está instalado" "Red"
    exit 1
}

Write-Host ""

# Función para mostrar uso
function Show-Usage {
    Write-Host "Uso: .\docker-start.ps1 [comando]"
    Write-Host ""
    Write-Host "Comandos disponibles:"
    Write-Host "  up        - Levantar todos los servicios"
    Write-Host "  down      - Detener todos los servicios"
    Write-Host "  restart   - Reiniciar todos los servicios"
    Write-Host "  logs      - Ver logs en tiempo real"
    Write-Host "  status    - Ver estado de servicios"
    Write-Host "  build     - Reconstruir imágenes"
    Write-Host "  clean     - Limpiar contenedores y volúmenes"
    Write-Host "  test      - Ejecutar tests básicos"
    Write-Host ""
}

# Función para levantar servicios
function Start-Services {
    Write-ColorOutput "🚀 Iniciando servicios..." "Cyan"
    
    # Crear directorios si no existen
    if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" | Out-Null }
    if (!(Test-Path "cache")) { New-Item -ItemType Directory -Path "cache" | Out-Null }
    if (!(Test-Path "cache/osm")) { New-Item -ItemType Directory -Path "cache/osm" | Out-Null }
    
    # Levantar servicios
    docker compose up -d
    
    Write-Host ""
    Write-ColorOutput "⏳ Esperando que los servicios estén listos..." "Yellow"
    Start-Sleep -Seconds 10
    
    # Verificar health
    $status = docker compose ps
    if ($status -match "healthy") {
        Write-ColorOutput "✅ Servicios iniciados correctamente" "Green"
        Write-Host ""
        Write-Host "📍 Servicios disponibles:"
        Write-Host "   - API:           http://localhost:8080"
        Write-Host "   - Documentación: http://localhost:8080/docs"
        Write-Host "   - Health Check:  http://localhost:8080/health"
        Write-Host ""
        
        # Test básico
        Write-ColorOutput "🧪 Probando API..." "Cyan"
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-ColorOutput "✅ API respondiendo correctamente" "Green"
            }
        } catch {
            Write-ColorOutput "⚠️  API aún no responde, puede tardar un poco más" "Yellow"
        }
    } else {
        Write-ColorOutput "⚠️  Servicios iniciados pero aún no están healthy" "Yellow"
        Write-Host "Ejecuta 'docker compose logs -f' para ver el progreso"
    }
}

# Función para detener servicios
function Stop-Services {
    Write-ColorOutput "🛑 Deteniendo servicios..." "Cyan"
    docker compose down
    Write-ColorOutput "✅ Servicios detenidos" "Green"
}

# Función para reiniciar servicios
function Restart-Services {
    Write-ColorOutput "🔄 Reiniciando servicios..." "Cyan"
    docker compose restart
    Write-ColorOutput "✅ Servicios reiniciados" "Green"
}

# Función para ver logs
function Show-Logs {
    Write-ColorOutput "📋 Mostrando logs (Ctrl+C para salir)..." "Cyan"
    docker compose logs -f
}

# Función para ver status
function Show-Status {
    Write-ColorOutput "📊 Estado de servicios:" "Cyan"
    Write-Host ""
    docker compose ps
    Write-Host ""
    Write-ColorOutput "💾 Uso de recursos:" "Cyan"
    docker stats --no-stream ruteo-api ruteo-redis
}

# Función para rebuild
function Rebuild-Services {
    Write-ColorOutput "🔨 Reconstruyendo imágenes..." "Cyan"
    docker compose build --no-cache
    Write-ColorOutput "✅ Imágenes reconstruidas" "Green"
    Write-Host ""
    Write-Host "Ejecuta '.\docker-start.ps1 up' para iniciar con las nuevas imágenes"
}

# Función para limpiar
function Clean-All {
    Write-ColorOutput "⚠️  ADVERTENCIA: Esto eliminará contenedores, volúmenes y caché" "Red"
    $confirmation = Read-Host "¿Estás seguro? (s/N)"
    
    if ($confirmation -eq 's' -or $confirmation -eq 'S') {
        Write-ColorOutput "🧹 Limpiando..." "Cyan"
        docker compose down -v
        
        if (Test-Path "cache") { Remove-Item -Recurse -Force "cache\*" }
        if (Test-Path "logs") { Remove-Item -Recurse -Force "logs\*" }
        
        Write-ColorOutput "✅ Limpieza completada" "Green"
    } else {
        Write-Host "Limpieza cancelada"
    }
}

# Función para tests
function Run-Tests {
    Write-ColorOutput "🧪 Ejecutando tests básicos..." "Cyan"
    Write-Host ""
    
    # Health check
    Write-Host "1. Health Check..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "   ✅ Health check OK" "Green"
        }
    } catch {
        Write-ColorOutput "   ❌ Health check falló" "Red"
        exit 1
    }
    
    # Geocoding forward
    Write-Host "2. Geocoding Forward..."
    try {
        $body = @{address = "18 de Julio 1000, Montevideo"} | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/geocode" `
            -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
        Write-ColorOutput "   ✅ Geocoding forward OK" "Green"
    } catch {
        Write-ColorOutput "   ❌ Geocoding forward falló" "Red"
    }
    
    # Geocoding reverse
    Write-Host "3. Geocoding Reverse..."
    try {
        $body = @{lat = -34.9033; lon = -56.1882} | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/reverse-geocode" `
            -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
        Write-ColorOutput "   ✅ Geocoding reverse OK" "Green"
    } catch {
        Write-ColorOutput "   ❌ Geocoding reverse falló" "Red"
    }
    
    Write-Host ""
    Write-ColorOutput "✅ Tests completados" "Green"
}

# Procesar comando
switch ($Command.ToLower()) {
    {$_ -in "up", "start"} {
        Start-Services
    }
    {$_ -in "down", "stop"} {
        Stop-Services
    }
    "restart" {
        Restart-Services
    }
    "logs" {
        Show-Logs
    }
    {$_ -in "status", "ps"} {
        Show-Status
    }
    "build" {
        Rebuild-Services
    }
    "clean" {
        Clean-All
    }
    "test" {
        Run-Tests
    }
    {$_ -in "help", "--help", "-h"} {
        Show-Usage
    }
    default {
        Write-ColorOutput "❌ Comando desconocido: $Command" "Red"
        Write-Host ""
        Show-Usage
        exit 1
    }
}

Write-Host ""
Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "Cyan"
Write-ColorOutput "Para más información: .\docker-start.ps1 help" "Green"
Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "Cyan"
