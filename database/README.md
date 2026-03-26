# Sistema de Banco de Dados SQLite - GNSS

## 📋 Visão Geral

Sistema de gerenciamento de banco de dados SQLite para armazenar dados de estações GNSS e microdados climáticos.

### Arquitetura Corrigida

```
database/
├── db_manager.py          # Gerenciador centralizado do banco
├── repositories.py         # Repositórios de dados (Estações e Microdados)
├── init_database.py        # Inicialização do banco (legado)
├── DDL.sql                 # Schema das tabelas
├── teste.py               # Script de teste com exemplos
└── validar.py             # Validação completa do sistema
```

## 🔧 Fluxo de Criação e Inserção CORRIGIDO

### 1. **DatabaseManager** (Nova camada)
- Gerencia a inicialização automática do banco
- Cria as tabelas via DDL.sql
- Cache para evitar recriações

### 2. **EstacoesRepository e MicrodadosRepository**
- Herdam de `BaseRepository`
- Chamam automaticamente `DatabaseManager.inicializar_banco()`
- Garantem que o banco existe antes de qualquer operação

### 3. **Fluxo Automático**
```
Criar Repositório → Inicializa Banco Automaticamente → Conectar → CRUD
```

## 🚀 Como Usar

### Opção 1: Teste Rápido
```bash
cd database
python teste.py
```

Vai:
- ✓ Criar o banco automaticamente
- ✓ Inserir 3 estações de exemplo
- ✓ Listar todas as estações
- ✓ Buscar estação por ID
- ✓ Atualizar dados

### Opção 2: Validação Completa
```bash
cd database
python validar.py
```

Testa:
- ✓ Inicialização do banco
- ✓ Criação de tabelas
- ✓ Inserção de dados
- ✓ Consultas
- ✓ Integridade referencial
- ✓ Transações

### Opção 3: Usar em Seu Código

```python
from database.repositories import EstacoesRepository
from datetime import date

# Criar repositório (banco é inicializado automaticamente)
repo = EstacoesRepository()
repo.conectar()

# Inserir estação
repo.inserir(
    id_municipio='3106200',
    id_estacao='A701',
    estacao='Belo Horizonte',
    data_fundacao=date(2009, 1, 1),
    latitude=-19.9330,
    longitude=-43.9325,
    altitude=847.0
)

# Listar todas
estacoes = repo.listar_todas()
for est in estacoes:
    print(est['estacao'])

# Buscar por ID
estacao = repo.obter_por_id('A701')
print(estacao['altitude'])

# Atualizar
repo.atualizar('A701', altitude=850.0)

# Contar
total = repo.contar()
print(f"Total: {total}")

repo.desconectar()
```

## 🔄 Operações Disponíveis

### EstacoesRepository
```python
repo.inserir(...)              # Inserir nova estação
repo.obter_por_id(id)         # Buscar por ID
repo.listar_todas()           # Listar todas
repo.listar_por_municipio(id) # Filtrar por município
repo.atualizar(id, **kwargs)  # Atualizar dados
repo.deletar(id)              # Deletar estação
repo.contar()                 # Contar total
```

### MicrodadosRepository
```python
repo.inserir(...)                      # Inserir microdados
repo.listar_por_estacao_periodo()      # Por período
repo.listar_por_estacao_ano()          # Por ano
repo.listar_por_estacao_mes()          # Por mês
repo.obter_media_temperatura()         # Calcular médias
repo.obter_precipitacao_total()        # Soma precipitação
repo.deletar_por_periodo()             # Deletar por período
repo.contar_por_estacao()              # Contar por estação
repo.contar_total()                    # Contar total
```

## 🛠️ Correções Implementadas

### ✓ Problema 1: Banco não era criado automaticamente
**Solução**: `DatabaseManager` inicializa na construção do Repositório

### ✓ Problema 2: Falta de tratamento de erros
**Solução**: Try/except implementado em `db_manager.py`

### ✓ Problema 3: DDL.sql com sintaxe incorreta
**Solução**: Vírgula adicionada antes de FOREIGN KEY

### ✓ Problema 4: Importações faltando
**Solução**: Adicionado `import sqlite3` e path adjustments

### ✓ Problema 5: Sem validação de integridade
**Solução**: Constraints SQL + Rollback em caso de erro

## 📊 Estrutura das Tabelas

### Estações
```sql
CREATE TABLE estacoes (
    id_municipio  TEXT,
    id_estacao    TEXT PRIMARY KEY,
    estacao       TEXT,
    data_fundacao DATE,
    latitude      REAL,
    longitude     REAL,
    altitude      REAL
);
```

### Microdados
```sql
CREATE TABLE microdados (
    ano, mes, data, hora,
    id_estacao TEXT FOREIGN KEY,
    precipitacao_total, pressao_atm_*,
    radiacao_global,
    temperatura_*,
    umidade_rel_*,
    vento_*
);
```

## ⚠️ Notas Importantes

1. **Banco é criado automaticamente** na primeira instanciação de um Repositório
2. **Arquivo `gnss.db`** é criado em `/database/`
3. **DDL.sql é necessário** estar no diretório `/database/`
4. **Valores NULL** são suportados para campos climáticos opcionais
5. **Transações automáticas** com rollback em caso de erro

## 🐛 Debug

Se encontrar erros:

```bash
# 1. Validar sistema completo
python database/validar.py

# 2. Verificar arquivo DDL.sql
cat database/DDL.sql

# 3. Verificar se gnss.db foi criado
ls -la database/gnss.db

# 4. Checar permissões
chmod 755 database/
```

## 📝 Exemplo Completo com BigQuery

```python
from database.repositories import EstacoesRepository
from google.cloud import bigquery
import pandas as pd
from datetime import date

# Código do c.py funciona agora sem problemas!
client = bigquery.Client.from_service_account_json(...)
df = client.query(query).to_dataframe()

repo = EstacoesRepository()  # Banco criado automaticamente
repo.conectar()

for _, row in df.iterrows():
    repo.inserir(
        id_municipio=str(row['id_municipio']),
        id_estacao=str(row['id_estacao']),
        estacao=str(row['estacao']),
        data_fundacao=row['data_fundacao'].date() if pd.notnull(row['data_fundacao']) else None,
        latitude=float(row['latitude']) if pd.notnull(row['latitude']) else None,
        longitude=float(row['longitude']) if pd.notnull(row['longitude']) else None,
        altitude=float(row['altitude']) if pd.notnull(row['altitude']) else None
    )

repo.desconectar()
```

---

✓ Sistema corrigido e testado!
