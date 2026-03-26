import sys
import os
from google.cloud import bigquery
import pandas as pd

# 1. Configuração de Caminhos
diretorio_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if diretorio_projeto not in sys.path:
    sys.path.append(diretorio_projeto)

from database.repositories import EstacoesRepository

# 2. Configuração BigQuery
CHAVE_JSON = r"C:\Users\RafaelLuizGonçalvesS\Downloads\pure-lodge-464519-d5-abf8344703b5.json"
client = bigquery.Client.from_service_account_json(CHAVE_JSON)

query = """
    SELECT 
        id_municipio,
        id_estacao,
        estacao,
        data_fundacao,
        latitude,
        longitude,
        altitude 
    FROM `basedosdados.br_inmet_bdmep.estacao` 
"""

print("Iniciando coleta no BigQuery...")
df_estacoes = client.query(query).to_dataframe()
print(f"Coletadas {len(df_estacoes)} estações.")

# 3. Salvando no SQLite usando seu Repositório
repo = EstacoesRepository()

try:
    repo.conectar()
    
    print("Inserindo dados no SQLite...")
    sucesso = 0
    erros = 0

    for _, row in df_estacoes.iterrows():
        try:
            # Tratamento para data (converte de Timestamp do Pandas para date do Python)
            data_fund = None
            if pd.notnull(row['data_fundacao']):
                data_fund = row['data_fundacao'].date()

            repo.inserir(
                id_municipio=str(row['id_municipio']),
                id_estacao=str(row['id_estacao']),
                estacao=str(row['estacao']),
                data_fundacao=data_fund,
                latitude=float(row['latitude']) if pd.notnull(row['latitude']) else None,
                longitude=float(row['longitude']) if pd.notnull(row['longitude']) else None,
                altitude=float(row['altitude']) if pd.notnull(row['altitude']) else None
            )
            sucesso += 1
        except Exception as e:
            # Provavelmente erro de ID duplicado (Primary Key) se rodar 2 vezes
            erros += 1
            continue

    print(f"Processo finalizado: {sucesso} inseridos, {erros} ignorados (já existentes).")

finally:
    repo.desconectar()