@echo off
title Workout API Async Pro - FastAPI High-Concurrency Server
echo ========================================================================
echo    WORKOUT API ASYNC PRO - Inicializacao Rapida Plug-and-Play
echo ========================================================================
echo.

if not exist ".venv" (
    echo [1/3] Criando ambiente virtual Python (.venv)...
    python -m venv .venv
)

echo [2/3] Ativando ambiente virtual e verificando dependencias...
call .venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo [3/3] Iniciando servidor Uvicorn...
python run.py
pause
