"""
Módulo para carregamento de dados.
Centraliza a lógica de leitura de arquivos e banco de dados.
"""

import pandas as pd
import sqlite3
from pathlib import Path
from typing import Optional, Tuple
import sys

# Adiciona o diretório database ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "database"))

from config import DATABASE_DIR, DADOS_INMET_DIR
def transform_troposphere_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    try:
        df['data_completa'] = pd.to_datetime(df['data_completa'])
        df['data'] = pd.to_datetime(df['data_completa'].dt.date)
        return df
    except Exception as e:
        print(f"Erro ao carregar dados de troposfera: {e}")
        return pd.DataFrame()

def create_troposphere_data_day(
    df: pd.DataFrame
) -> pd.DataFrame:
    try:
        TRWET = pd.DataFrame(df[['data_completa','TRWET']])
        TRWET.set_index('data_completa', inplace=True)
        df_diario = TRWET['TRWET'].resample('D').mean()
        return df_diario
    except Exception as e:
        print(f"Erro ao carregar dados diários: {e}")
        return pd.DataFrame()
    
def create_troposphere_data_month(
    df: pd.DataFrame
) -> pd.DataFrame:
    try:
        TRWET = pd.DataFrame(df[['data_completa','TRWET']])
        TRWET.set_index('data_completa', inplace=True)
        df_diario = TRWET['TRWET'].resample('D').mean()
        df_mensal = df_diario.resample('MS').mean().to_frame()
        return df_mensal
    except Exception as e:
        print(f"Erro ao carregar dados mensal: {e}")
        return pd.DataFrame()
    
def load_troposphere_data(
    station: str = "MGBH",
    year: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Carrega dados de troposfera de um arquivo TROP específico.
    
    Args:
        station (str): Código da estação (ex: MGBH, MGMC)
        year (int): Ano específico, se None carrega todos
        start_date (str): Data inicial no formato YYYY-MM-DD
        end_date (str): Data final no formato YYYY-MM-DD
        
    Returns:
        pd.DataFrame: DataFrame com os dados carregados
    """
    try:
        df = pd.read_csv('/home/rafael-luiz/Desktop/IC_gnss/src/data/dados/dados_troposfera_MGBH.csv')
        df_clear = transform_troposphere_data(df)
        df_day = create_troposphere_data_day(df_clear)
        df_month = create_troposphere_data_month(df_clear)
        if not df.empty:
            df_clear['data'] = pd.to_datetime(df_clear['data'], errors='coerce')
            
            if start_date:
                df_clear = df_clear[df_clear['data'] >= start_date]
            if end_date:
                df_clear = df_clear[df_clear['data'] <= end_date]
        
        return df_clear, df_day, df_month
    except Exception as e:
        print(f"Erro ao carregar dados de troposfera: {e}")
        return pd.DataFrame()






def load_inmet_data(
    station_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Carrega dados INMET de arquivo CSV.
    
    Args:
        station_id (str): ID da estação INMET
        start_date (str): Data inicial no formato YYYY-MM-DD
        end_date (str): Data final no formato YYYY-MM-DD
        
    Returns:
        pd.DataFrame: DataFrame com os dados INMET
    """
    try:
        # Procura por arquivos CSV de dados INMET
        csv_files = list(DADOS_INMET_DIR.glob("dados_*.csv"))
        
        if not csv_files:
            return pd.DataFrame()
        
        # Carrega o primeiro arquivo encontrado
        df = pd.read_csv(csv_files[0])
        
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            
            if start_date:
                df = df[df['Data'] >= start_date]
            if end_date:
                df = df[df['Data'] <= end_date]
        
        return df
    except Exception as e:
        print(f"Erro ao carregar dados INMET: {e}")
        return pd.DataFrame()


def load_from_database(
    query: str,
    db_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Carrega dados diretamente do banco de dados SQLite.
    
    Args:
        query (str): Query SQL a executar
        db_path (str): Caminho do banco de dados
        
    Returns:
        pd.DataFrame: Resultado da query
    """
    try:
        if db_path is None:
            db_path = str(DATABASE_DIR / "gnss.db")
        
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    except Exception as e:
        print(f"Erro ao carregar dados do banco: {e}")
        return pd.DataFrame()
