@echo off
REM Script para ejecutar el servidor

echo ========================================
echo Sistema de Ruteo Inteligente
echo Iniciando servidor...
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist venv (
    echo ERROR: Entorno virtual no encontrado
    echo Por favor ejecuta install.bat primero
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar servidor
echo Servidor iniciando en http://localhost:8000
echo Documentación: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python app/main.py
