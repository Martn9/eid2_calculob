@echo off
cd /d "%~dp0"

where py >nul 2>&1
if %errorlevel%==0 (
    set "PY_CMD=py -3"
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        set "PY_CMD=python"
    ) else (
        echo Error: Python no esta instalado o no esta en el PATH.
        pause
        exit /b 1
    )
)

if not exist "venv" (
    %PY_CMD% -m venv venv
    if errorlevel 1 (
        echo Error al crear el entorno virtual.
        pause
        exit /b 1
    )
)

venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error al instalar las dependencias.
    pause
    exit /b 1
)

echo.
echo Entorno listo. Para ejecutar el programa:
echo   venv\Scripts\python.exe main.py
pause
