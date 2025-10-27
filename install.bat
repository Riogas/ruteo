@echo off
REM Script de instalación para Windows

echo ========================================
echo Sistema de Ruteo Inteligente
echo Script de Instalación
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.10 o superior desde https://www.python.org
    pause
    exit /b 1
)

echo [1/5] Python encontrado
python --version
echo.

REM Crear entorno virtual
echo [2/5] Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo OK
echo.

REM Activar entorno virtual
echo [3/5] Activando entorno virtual...
call venv\Scripts\activate.bat
echo OK
echo.

REM Instalar dependencias
echo [4/5] Instalando dependencias (esto puede tardar unos minutos)...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Fallo al instalar dependencias
    pause
    exit /b 1
)
echo OK
echo.

REM Crear archivo .env
echo [5/5] Configurando archivo .env...
if not exist .env (
    copy .env.example .env
    echo Archivo .env creado. Por favor edítalo si necesitas configurar API keys.
) else (
    echo Archivo .env ya existe, no se sobrescribe.
)
echo.

echo ========================================
echo INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo Para ejecutar el sistema:
echo   1. Activa el entorno: venv\Scripts\activate
echo   2. Ejecuta: python app/main.py
echo   3. Abre: http://localhost:8000/docs
echo.
echo O ejecuta: run.bat
echo.
pause
