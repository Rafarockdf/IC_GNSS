#!/bin/bash
# Script para executar a aplicação Streamlit

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   GNSS Data Analyzer - Streamlit App   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "app.py" ]; then
    echo -e "${RED}✗ Erro: app.py não encontrado${NC}"
    echo -e "${YELLOW}Execute este script a partir da pasta 'src'${NC}"
    exit 1
fi

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Erro: Python 3 não está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 encontrado${NC}"

# Verificar se o venv existe
if [ ! -d "../venv" ]; then
    echo -e "${YELLOW}⚠ Ambiente virtual não encontrado. Criando...${NC}"
    python3 -m venv ../venv
    source ../venv/bin/activate
    echo -e "${GREEN}✓ Ambiente virtual criado${NC}"
else
    echo -e "${GREEN}✓ Ambiente virtual encontrado${NC}"
    source ../venv/bin/activate
fi

# Instalar dependências
echo -e "${YELLOW}⚠ Instalando/atualizando dependências...${NC}"
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependências instaladas com sucesso${NC}"
else
    echo -e "${RED}✗ Erro ao instalar dependências${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Iniciando aplicação Streamlit...      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}A aplicação será aberta em:${NC} http://localhost:8501"
echo -e "${YELLOW}Para sair, pressione:${NC} Ctrl+C"
echo ""

# Executar a aplicação
streamlit run app.py

deactivate