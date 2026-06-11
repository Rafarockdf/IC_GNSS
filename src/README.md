# Configuração do Streamlit - IC GNSS

## Instalação e Execução

### 1. Instalar Dependências

```bash
cd src
pip install -r requirements.txt
```

### 2. Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação será aberta em `http://localhost:8501`

## Estrutura do Projeto

```
src/
├── app.py                      # Arquivo principal (home page)
├── config.py                   # Configurações globais
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
│
├── .streamlit/
│   └── config.toml            # Configuração do Streamlit
│
├── pages/                      # Páginas múltiplas da app
│   ├── 01_📊_Dashboard.py      # Dashboard principal
│   ├── 02_📈_Correlacao.py     # Análise de correlação
│   ├── 03_🔍_Decomposicao.py   # Decomposição de séries
│   └── 04_⚙️_Configuracoes.py  # Configurações
│
├── components/                 # Componentes reutilizáveis
│   ├── __init__.py
│   ├── sidebar.py             # Componentes da sidebar
│   └── charts.py              # Componentes de gráficos
│
└── utils/                      # Utilitários
    ├── __init__.py
    ├── data_loader.py         # Carregamento de dados
    └── analysis.py            # Funções de análise
```

## Páginas Disponíveis

### 📊 Dashboard
- Visualização geral dos dados
- Estatísticas por estação
- Preview dos dados brutos

### 📈 Correlação
- Análise de correlação entre variáveis
- Matriz de correlação
- Testes de significância (p-value)

### 🔍 Decomposição
- Decomposição de séries temporais
- Análise de tendência e sazonalidade
- Estatísticas dos componentes

### ⚙️ Configurações
- Preferências do usuário
- Informações do sistema
- Modo debug

## Desenvolvimento

### Adicionando Novas Páginas

1. Crie um arquivo em `pages/` com nome começando por número:
   ```python
   # pages/05_🆕_MinhaPage.py
   import streamlit as st
   
   st.title("Minha Nova Página")
   ```

2. A página aparecerá automaticamente no menu lateral

### Adicionando Novos Componentes

1. Crie uma função em `components/`:
   ```python
   def meu_componente():
       st.write("Meu componente")
   ```

2. Importe e use nas páginas:
   ```python
   from components.sidebar import meu_componente
   meu_componente()
   ```

## Configuração do Banco de Dados

A aplicação busca dados em:
- `../database/gnss.db` - Banco SQLite
- `../database/dados_gnss/` - Arquivos TROP
- `../database/dados_inmet/` - Arquivos CSV INMET

## Troubleshooting

### Erro: "ModuleNotFoundError"
- Verifique se está na pasta `src`
- Execute: `export PYTHONPATH="${PYTHONPATH}:${PWD}"`

### Erro: "No such file or directory: gnss.db"
- Certifique-se que o banco foi inicializado
- Execute: `python ../database/init_database.py`

### Dados não aparecem
- Verifique se os arquivos estão nos caminhos corretos
- Consulte a página de Configurações para ver os caminhos

## Customização

### Sistema de Temas 🎨

A aplicação possui um sistema de temas robusto com suporte a **Tema Claro** (☀️) e **Tema Escuro** (🌙).

#### Selecionar Tema

1. Abra a aplicação
2. Na barra lateral (sidebar), clique em **🎨 Tema**
3. Escolha entre:
   - **☀️ Claro**: Tema com cores claras e background branco
   - **🌙 Escuro**: Tema com cores escuras e background preto

A preferência é salva na sessão e persiste enquanto a aplicação está aberta.

#### Cores do Tema Claro
- **Primária**: Azul (#1f77b4)
- **Secundária**: Laranja (#ff7f0e)
- **Sucesso**: Verde (#2ca02c)
- **Perigo**: Vermelho (#d62728)
- **Background**: Branco (#ffffff)

#### Cores do Tema Escuro
- **Primária**: Azul (#1f77b4)
- **Secundária**: Laranja (#ff7f0e)
- **Sucesso**: Verde (#2ca02c)
- **Perigo**: Vermelho (#d62728)
- **Background**: Cinza Escuro (#0e1117)

#### Customizar Temas

Para adicionar novos temas, edite `utils/themes.py`:

```python
MEUNOVOTEMA = Theme(
    name="Meu Tema",
    primary="#color",
    secondary="#color",
    # ... outras cores
)

THEMES["meiotema"] = MEUNOVOTEMA
THEME_NAMES["meiotema"] = "🎨 Meu Tema"
```

### Mudar Cores do Tema
Edite `config.py` ou `.streamlit/config.toml`

### Adicionar Novas Estações
Edite a variável `ESTACOES` em `config.py`

### Modificar Análises
Adicione novas funções em `utils/analysis.py`

## Requisitos Mínimos

- Python 3.8+
- 2GB RAM
- Conexão com o banco de dados

## Licença

Projeto IC - GNSS Data Analyzer
