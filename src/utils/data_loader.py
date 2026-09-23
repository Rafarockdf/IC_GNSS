"""
Módulo para carregamento de dados.
Centraliza a lógica de leitura de arquivos e banco de dados.
"""

import pandas as pd
import sqlite3
import streamlit as st
from pathlib import Path
from typing import Optional, Tuple
import sys

# Adiciona o diretório database ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "database"))

from config import DATABASE_DIR, DADOS_DIR, DADOS_INMET_DIR, INMET_SEARCH_DIRS, CACHE_DIR
from utils.trop_parser import parse_station_trwet


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


def _cache_file_for_station(station: str) -> Path:
    return CACHE_DIR / f"{station}_TRWET.csv"


def build_or_load_trwet(station: str, force_rebuild: bool = False) -> pd.DataFrame:
    """
    Retorna o DataFrame bruto (data_completa, TRWET) de uma estação.

    Os arquivos .trop originais são lidos apenas uma vez: o resultado é
    salvo em cache (CSV) dentro de database/cache e reaproveitado nas
    próximas execuções, já que o parsing de todos os arquivos brutos é custoso.
    """
    cache_file = _cache_file_for_station(station)

    if cache_file.exists() and not force_rebuild:
        df = pd.read_csv(cache_file, parse_dates=['data_completa'])
        return df

    station_dir = DADOS_DIR / station
    if not station_dir.exists():
        return pd.DataFrame(columns=['data_completa', 'TRWET'])

    df = parse_station_trwet(station_dir)

    if not df.empty:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_file, index=False)

    return df


@st.cache_data(show_spinner=False)
def load_troposphere_data(
    station: str = "MGBH",
    year: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Carrega dados de troposfera de uma estação a partir dos arquivos .trop brutos.

    Args:
        station (str): Código da estação (ex: MGBH, MGMC)
        year (int): Ano específico, se None carrega todos
        start_date (str): Data inicial no formato YYYY-MM-DD
        end_date (str): Data final no formato YYYY-MM-DD

    Returns:
        Tuple[pd.DataFrame, pd.Series, pd.DataFrame]: (dados brutos, série diária, série mensal)
    """
    try:
        df = build_or_load_trwet(station)

        if df.empty:
            return pd.DataFrame(), pd.Series(dtype=float), pd.DataFrame()

        df_clear = transform_troposphere_data(df)

        if year:
            df_clear = df_clear[df_clear['data_completa'].dt.year == int(year)]
        if start_date:
            df_clear = df_clear[df_clear['data'] >= start_date]
        if end_date:
            df_clear = df_clear[df_clear['data'] <= end_date]

        df_day = create_troposphere_data_day(df_clear)
        df_month = create_troposphere_data_month(df_clear)

        return df_clear, df_day, df_month
    except Exception as e:
        print(f"Erro ao carregar dados de troposfera: {e}")
        return pd.DataFrame(), pd.Series(dtype=float), pd.DataFrame()


def _find_header_row(path: Path, encoding: str = "latin1") -> int:
    """Localiza a linha de cabeçalho ('Data;Hora UTC;...') em um CSV do portal INMET."""
    with open(path, "r", encoding=encoding) as f:
        for i, line in enumerate(f):
            if line.strip().lower().startswith("data;hora"):
                return i
    return 0


def _extract_station_name(path: Path, encoding: str = "latin1") -> Optional[str]:
    """Lê o cabeçalho de metadados (se existir) para extrair o nome da estação."""
    with open(path, "r", encoding=encoding) as f:
        for line in f:
            if line.upper().startswith("ESTACAO:"):
                return line.split(";")[1].strip()
            if line.lower().startswith("data;hora"):
                break
    return None


def _read_inmet_raw_file(path: Path) -> pd.DataFrame:
    header_row = _find_header_row(path)
    df = pd.read_csv(path, sep=";", encoding="latin1", skiprows=header_row, decimal=",")

    # Remove colunas "Unnamed" (sobra do ';' final de cada linha)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    # Renomeia colunas pela posição, já que a acentuação do cabeçalho pode vir corrompida
    cols = list(df.columns)
    cols[0] = "Data"
    cols[1] = "Hora UTC"
    cols[2] = "PRECIPITACAO_HORARIA_MM"
    df.columns = cols

    estacao = _extract_station_name(path) or path.stem
    df["nome_estacao"] = estacao.upper()

    hora = df["Hora UTC"].astype(str).str.replace(" UTC", "", regex=False).str.zfill(4)
    df["Data Medicao"] = pd.to_datetime(
        df["Data"].astype(str) + hora, format="%Y/%m/%d%H%M", errors="coerce"
    )
    df["PRECIPITACAO_HORARIA_MM"] = pd.to_numeric(df["PRECIPITACAO_HORARIA_MM"], errors="coerce")

    return df[["Data Medicao", "nome_estacao", "PRECIPITACAO_HORARIA_MM"]].dropna(subset=["Data Medicao"])


@st.cache_data(show_spinner=False)
def load_inmet_data(
    station_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Carrega e concatena os arquivos brutos de precipitação horária do INMET
    encontrados em INMET_SEARCH_DIRS (formato de exportação do portal INMET).

    Args:
        station_id (str): Nome (ou parte do nome) da estação para filtrar
        start_date (str): Data inicial no formato YYYY-MM-DD
        end_date (str): Data final no formato YYYY-MM-DD

    Returns:
        pd.DataFrame: colunas [Data Medicao, nome_estacao, PRECIPITACAO_HORARIA_MM]
    """
    try:
        seen_paths = set()
        frames = []
        for directory in INMET_SEARCH_DIRS:
            if not directory.exists():
                continue
            for pattern in ("*.csv", "*.CSV"):
                for csv_path in directory.glob(pattern):
                    resolved = csv_path.resolve()
                    if resolved in seen_paths:
                        continue
                    seen_paths.add(resolved)
                    try:
                        frames.append(_read_inmet_raw_file(csv_path))
                    except Exception as e:
                        print(f"Erro ao ler arquivo INMET {csv_path}: {e}")

        if not frames:
            return pd.DataFrame()

        df = pd.concat(frames, ignore_index=True)
        df = df.drop_duplicates(subset=["Data Medicao", "nome_estacao"], keep="first")
        df = df.sort_values("Data Medicao").reset_index(drop=True)

        if station_id:
            df = df[df["nome_estacao"].str.contains(station_id.upper(), na=False)]

        if start_date:
            df = df[df["Data Medicao"] >= start_date]
        if end_date:
            df = df[df["Data Medicao"] <= end_date]

        return df
    except Exception as e:
        print(f"Erro ao carregar dados INMET: {e}")
        return pd.DataFrame()


def load_precipitation_daily(station_id: Optional[str] = None) -> pd.Series:
    """Retorna a série diária (soma) de precipitação em mm."""
    df = load_inmet_data(station_id=station_id)
    if df.empty:
        return pd.Series(dtype=float)
    serie = df.set_index("Data Medicao")["PRECIPITACAO_HORARIA_MM"].resample("D").sum()
    return serie


def load_precipitation_monthly(station_id: Optional[str] = None) -> pd.DataFrame:
    """Retorna o acumulado mensal de precipitação em mm."""
    daily = load_precipitation_daily(station_id=station_id)
    if daily.empty:
        return pd.DataFrame()
    mensal = daily.resample("MS").sum().to_frame(name="PRECIPITACAO_MM")
    return mensal


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