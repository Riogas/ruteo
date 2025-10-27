# Reiniciar Servidor
Write-Host \"
 Reiniciando servidor...\
\" -ForegroundColor Cyan
Get-ChildItem -Path . -Directory -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "*.pyc" -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*ruteo*" } | Stop-Process -Force
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\jgomez\Documents\Projects\ruteo'; .\venv\Scripts\python.exe start_server.py"
Start-Sleep -Seconds 6
try { 
    Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5 | Out-Null
    Write-Host " ACTIVO!\
" -ForegroundColor Green 
} catch { 
    Start-Sleep -Seconds 3
    Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5 | Out-Null
    Write-Host " ACTIVO!\
" -ForegroundColor Green 
}
