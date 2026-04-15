#!/bin/bash
# Script de setup para ambiente de desenvolvimento

echo "================================"
echo "🚀 Setup - Automação Logtudo BI"
echo "================================"

# Verificar Python
echo ""
echo "1️⃣  Verificando Python..."
python --version || { echo "❌ Python não instalado!"; exit 1; }

# Criar virtual environment
echo ""
echo "2️⃣  Criando ambiente virtual..."
python -m venv .venv

# Ativar virtual environment (Linux/Mac)
if [[ -f .venv/bin/activate ]]; then
    echo "   Ativando .venv (Linux/Mac)..."
    source .venv/bin/activate
fi

# Instalar dependências
echo ""
echo "3️⃣  Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Instalar browsers Playwright
echo ""
echo "4️⃣  Instalando browsers Playwright..."
playwright install

# Criar arquivo .env
echo ""
echo "5️⃣  Configurando arquivo .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   ✅ Arquivo .env criado"
    echo "   ⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais!"
else
    echo "   ℹ️  Arquivo .env já existe"
fi

echo ""
echo "================================"
echo "✅ Setup concluído!"
echo "================================"
echo ""
echo "⏭️  Próximos passos:"
echo "   1. Edite o arquivo .env com suas credenciais"
echo "   2. Execute: python main.py"
echo ""
