"""
Arquivo de configuração da aplicação Streamlit.
Centraliza constantes e configurações do projeto.
"""

import os
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = Path(__file__).parent
DATABASE_DIR = BASE_DIR / "database"
DADOS_DIR = BASE_DIR / "database" / "dados_gnss"
DADOS_INMET_DIR = BASE_DIR / "database" / "dados_inmet"

# Diretórios onde procurar arquivos brutos do INMET (portal INMET, ; separado, latin1)
INMET_SEARCH_DIRS = [
    DADOS_INMET_DIR,
    BASE_DIR / "EstudoGNSS",
]

# Cache de dados processados (evita reprocessar os arquivos .trop a cada execução)
CACHE_DIR = DATABASE_DIR / "cache"

# Configuração do banco de dados
DB_PATH = DATABASE_DIR / "gnss.db"
DB_PATH_STRING = str(DB_PATH)

# Estações disponíveis
ESTACOES = {
    "MGBH": "Belo Horizonte",
    "MGMC": "Montes Claros",
    "MGJF": "Juiz de Fora",
}

# Configuração de estilo
STREAMLIT_CONFIG = {
    "page_title": "GNSS Data Analyzer",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Cores do tema
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff9896",
    "info": "#17becf",
}

# Configurações de análise
ANALYSIS_CONFIG = {
    "default_station": "MGBH",
    "date_format": "%Y-%m-%d",
    "datetime_format": "%Y-%m-%d %H:%M:%S",
    "max_data_points": 10000,
}

# Variáveis ambientais
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
