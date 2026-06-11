@echo off
REM Script para executar a aplicação Streamlit no Windows

echo ====================================
echo   GNSS Data Analyzer - Streamlit App
echo ====================================
echo.

REM Verificar se estamos no diretório correto
if not exist "app.py" (
    echo Erro: app.py nao encontrado
    echo Execute este script a partir da pasta 'src'
    pause
    exit /b 1
)

REM Verificar se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Python nao esta instalado ou nao esta no PATH
    pause
    exit /b 1
)

echo ✓ Python encontrado

REM Verificar e ativar venv
if not exist "..\venv" (
    echo ⚠ Ambiente virtual nao encontrado. Criando...
    python -m venv ..\venv
)

call ..\venv\Scripts\activate.bat

REM Instalar dependências
echo ⚠ Instalando/atualizando dependências...
pip install -q -r requirements.txt

if %errorlevel% neq 0 (
    echo Erro ao instalar dependências
    pause
    exit /b 1
)

echo ✓ Dependências instaladas com sucesso
echo.
echo ====================================
echo  Iniciando aplicacao Streamlit...
echo ====================================
echo.
echo A aplicacao sera aberta em: http://localhost:8501
echo Para sair, pressione: Ctrl+C
echo.

REM Executar a aplicação
streamlit run app.py

call ..\venv\Scripts\deactivate.bat
pause
