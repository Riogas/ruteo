# ============================================================================
# Script de Inicio del Servidor FastAPI - Ruteo
# ============================================================================
# Uso: .\start_server_simple.ps1
# Descripción: Inicia el servidor (sin detener procesos anteriores)
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host " 🚀 INICIANDO SERVIDOR FASTAPI - RUTEO" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor
Write-Host "🚀 Lanzando servidor..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\jgomez\Documents\Projects\ruteo'; .\venv\Scripts\python.exe start_server.py"
Write-Host "   ✅ Proceso iniciado" -ForegroundColor Green
Write-Host ""

# Esperar y verificar
Write-Host "⏳ Esperando que el servidor esté listo..." -ForegroundColor Yellow
Start-Sleep -Seconds 6

try {
    Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5 | Out-Null
    Write-Host "   ✅ SERVIDOR ACTIVO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host " 🎉 Servidor disponible en: http://localhost:8080" -ForegroundColor Green
    Write-Host " 📚 Documentación API: http://localhost:8080/docs" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "   ⏳ Aún no está listo, reintentando..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    try {
        Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5 | Out-Null
        Write-Host "   ✅ SERVIDOR ACTIVO!" -ForegroundColor Green
        Write-Host ""
        Write-Host "============================================================================" -ForegroundColor Cyan
        Write-Host " 🎉 Servidor disponible en: http://localhost:8080" -ForegroundColor Green
        Write-Host " 📚 Documentación API: http://localhost:8080/docs" -ForegroundColor Green
        Write-Host "============================================================================" -ForegroundColor Cyan
        Write-Host ""
    } catch {
        Write-Host "   ❌ ERROR: El servidor no respondió" -ForegroundColor Red
        Write-Host "   💡 Revisa la ventana del servidor para ver errores" -ForegroundColor Yellow
        Write-Host ""
    }
}
