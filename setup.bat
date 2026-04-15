@echo off
REM Script de setup para ambiente de desenvolvimento (Windows)

echo.
echo ================================
echo 🚀 Setup - Automacao Logtudo BI
echo ================================

REM Verificar Python
echo.
echo 1) Verificando Python...
python --version >nul 2>&1 || (
    echo ❌ Python nao instalado!
    exit /b 1
)

REM Criar virtual environment
echo.
echo 2) Criando ambiente virtual...
python -m venv .venv

REM Ativar virtual environment 
echo.
echo 3) Ativando .venv...
call .venv\Scripts\activate.bat

REM Instalar dependências
echo.
echo 4) Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Instalar browsers Playwright
echo.
echo 5) Instalando browsers Playwright...
playwright install

REM Criar arquivo .env
echo.
echo 6) Configurando arquivo .env...
if not exist .env (
    copy .env.example .env
    echo.    ✅ Arquivo .env criado
    echo.    ⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais!
) else (
    echo.    ℹ️  Arquivo .env ja existe
)

echo.
echo ================================
echo ✅ Setup concluido!
echo ================================
echo.
echo Proximos passos:
echo.   1. Edite o arquivo .env com suas credenciais
echo.   2. Execute: python main.py
echo.
pause
