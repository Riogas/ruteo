# Script para verificar que Docker esta instalado y corriendo
# Uso: .\check-docker.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Verificacion de Docker" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Verificar que Docker este instalado
Write-Host "[1/2] Verificando instalacion de Docker..." -ForegroundColor Yellow

try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK - Docker instalado: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "ERROR - Docker no esta instalado" -ForegroundColor Red
        Write-Host "Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ERROR - Docker no esta instalado" -ForegroundColor Red
    Write-Host "Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Paso 2: Verificar que Docker Desktop este corriendo
Write-Host "[2/2] Verificando que Docker este corriendo..." -ForegroundColor Yellow

try {
    $containers = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK - Docker esta corriendo correctamente" -ForegroundColor Green
        Write-Host ""
        
        # Mostrar contenedores activos
        $containerCount = (docker ps --format "{{.Names}}" | Measure-Object -Line).Lines
        if ($containerCount -gt 0) {
            Write-Host "Contenedores activos ($containerCount):" -ForegroundColor Cyan
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        } else {
            Write-Host "No hay contenedores corriendo actualmente" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "============================================" -ForegroundColor Green
        Write-Host "  Docker esta listo para usar" -ForegroundColor Green
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Siguiente paso:" -ForegroundColor Cyan
        Write-Host "  docker compose up -d" -ForegroundColor White
        Write-Host ""
        
    } else {
        throw "Docker no esta corriendo"
    }
} catch {
    Write-Host "ERROR: Docker Desktop NO esta corriendo" -ForegroundColor Red
    Write-Host ""
    Write-Host "Pasos para iniciar Docker:" -ForegroundColor Yellow
    Write-Host "1. Busca Docker Desktop en el menu de Windows" -ForegroundColor White
    Write-Host "2. Haz clic en el icono para iniciar" -ForegroundColor White
    Write-Host "3. Espera a que aparezca el icono de Docker en la barra de tareas" -ForegroundColor White
    Write-Host "4. Ejecuta este script nuevamente para verificar" -ForegroundColor White
    Write-Host ""
    
    exit 1
}
