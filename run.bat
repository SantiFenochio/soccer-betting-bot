@echo off
REM Archivo para ejecutar el bot en Windows

echo ======================================
echo   SOCCER BETTING BOT
echo ======================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Por favor instala Python 3.8 o superior
    pause
    exit /b 1
)

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Ejecutar bot
echo Iniciando bot...
python main.py

pause
