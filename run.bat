@echo off
REM StudioSpec Pro - Windows Launcher
chcp 65001 >nul
title StudioSpec Pro - Audio Workstation Inspector
echo ========================================================
echo   🎛️ StudioSpec Pro - Audio Workstation Inspector
echo ========================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERRORE] Python non trovato nel sistema.
        echo Installa Python 3.8+ dal Microsoft Store o da python.org
        pause
        exit /b 1
    ) else (
        set PY_CMD=py
    )
) else (
    set PY_CMD=python
)

echo Avvio dashboard in corso...
%PY_CMD% main.py %*
if %errorlevel% neq 0 (
    echo.
    echo Si è verificato un errore durante l'esecuzione.
    pause
)
