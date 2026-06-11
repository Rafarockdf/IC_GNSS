"""
Módulo de análise de dados.
Implementa funções de análise estatística e séries temporais.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
from scipy.stats import pearsonr, spearmanr
from statsmodels.tsa.seasonal import seasonal_decompose


def correlate_data(
    df: pd.DataFrame,
    col1: str,
    col2: str,
    method: str = "pearson"
) -> Tuple[float, float]:
    """
    Calcula correlação entre duas colunas.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados
        col1 (str): Nome da primeira coluna
        col2 (str): Nome da segunda coluna
        method (str): Tipo de correlação ('pearson' ou 'spearman')
        
    Returns:
        Tuple[float, float]: (correlação, p-value)
    """
    try:
        # Remove NaN values
        valid_mask = df[[col1, col2]].notna().all(axis=1)
        col1_data = df.loc[valid_mask, col1]
        col2_data = df.loc[valid_mask, col2]
        
        if len(col1_data) < 2:
            return np.nan, np.nan
        
        if method == "spearman":
            corr, pvalue = spearmanr(col1_data, col2_data)
        else:
            corr, pvalue = pearsonr(col1_data, col2_data)
        
        return corr, pvalue
    except Exception as e:
        print(f"Erro ao calcular correlação: {e}")
        return np.nan, np.nan


def decompose_series(
    df: pd.DataFrame,
    column: str,
    period: int = 365,
    model: str = "additive"
) -> dict:
    """
    Decomposição de série temporal.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados
        column (str): Coluna a decompor
        period (int): Período de sazonalidade
        model (str): 'additive' ou 'multiplicative'
        
    Returns:
        dict: Dicionário com trend, seasonal, residual
    """
    try:
        # Remove NaN values
        series = df[column].dropna()
        
        if len(series) < 2 * period:
            return None
        
        decomposition = seasonal_decompose(
            series,
            model=model,
            period=period,
            extrapolate='fill_ea'
        )
        
        return {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'observed': decomposition.observed,
        }
    except Exception as e:
        print(f"Erro ao decompor série: {e}")
        return None


def calculate_statistics(
    df: pd.DataFrame,
    column: str
) -> dict:
    """
    Calcula estatísticas descritivas.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados
        column (str): Coluna para calcular estatísticas
        
    Returns:
        dict: Dicionário com estatísticas
    """
    try:
        data = df[column].dropna()
        
        return {
            'mean': data.mean(),
            'median': data.median(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'q25': data.quantile(0.25),
            'q75': data.quantile(0.75),
            'count': len(data),
        }
    except Exception as e:
        print(f"Erro ao calcular estatísticas: {e}")
        return {}


def smooth_data(
    df: pd.DataFrame,
    column: str,
    window: int = 7,
    method: str = "rolling"
) -> pd.Series:
    """
    Suaviza dados usando média móvel ou exponencial.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados
        column (str): Coluna a suavizar
        window (int): Tamanho da janela
        method (str): 'rolling' ou 'exponential'
        
    Returns:
        pd.Series: Série suavizada
    """
    try:
        if method == "exponential":
            return df[column].ewm(span=window, adjust=False).mean()
        else:
            return df[column].rolling(window=window, center=True).mean()
    except Exception as e:
        print(f"Erro ao suavizar dados: {e}")
        return df[column]
