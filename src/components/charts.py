"""Componentes de visualização de gráficos."""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional


def plot_time_series(
    df: pd.DataFrame,
    date_column: str = "data_completa",
    value_column: str = "TRWET",
    title: str = "Série Temporal",
    figsize: tuple = (12, 6),
    smooth_line: Optional[pd.Series] = None
):
    """
    Plota uma série temporal.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados
        date_column (str): Nome da coluna de datas
        value_column (str): Nome da coluna com valores
        title (str): Título do gráfico
        figsize (tuple): Tamanho da figura
        smooth_line (pd.Series): Série suavizada (opcional)
    """
    try:
        date_column = df.index
        value_column = df.values
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plota dados originais
        ax.plot(
            df.index,
            df.values,
            label="Dados Originais",
            alpha=0.7,
            linewidth=1
        )
        
        # Plota linha suavizada se fornecida
        if smooth_line is not None:
            ax.plot(
                df.index,
                smooth_line,
                label="Suavizado",
                linewidth=2,
                color="red"
            )
        
        ax.set_xlabel("Data")
        ax.set_ylabel(value_column)
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Erro ao plotar série temporal: {e}")


def plot_correlation_matrix(
    df: pd.DataFrame,
    columns: Optional[list] = None,
    figsize: tuple = (10, 8)
):
    """
    Plota matriz de correlação.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados
        columns (list): Colunas para calcular correlação
        figsize (tuple): Tamanho da figura
    """
    try:
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(columns) < 2:
            st.warning("É necessário selecionar pelo menos 2 colunas numéricas")
            return
        
        corr_matrix = df[columns].corr()
        
        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            ax=ax,
            cbar_kws={"label": "Correlação"}
        )
        ax.set_title("Matriz de Correlação")
        plt.tight_layout()
        
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Erro ao plotar matriz de correlação: {e}")


def plot_decomposition(
    decomposition: dict,
    figsize: tuple = (14, 10)
):
    """
    Plota decomposição de série temporal.
    
    Args:
        decomposition (dict): Dicionário com trend, seasonal, residual
        figsize (tuple): Tamanho da figura
    """
    try:
        fig, axes = plt.subplots(4, 1, figsize=figsize)
        
        # Série original
        axes[0].plot(decomposition['observed'], label='Original', color='blue')
        axes[0].set_ylabel('Original')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Tendência
        axes[1].plot(decomposition['trend'], label='Tendência', color='orange')
        axes[1].set_ylabel('Tendência')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Sazonalidade
        axes[2].plot(decomposition['seasonal'], label='Sazonalidade', color='green')
        axes[2].set_ylabel('Sazonalidade')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        # Resíduos
        axes[3].plot(decomposition['residual'], label='Resíduos', color='red')
        axes[3].set_ylabel('Resíduos')
        axes[3].set_xlabel('Índice de Tempo')
        axes[3].legend()
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Erro ao plotar decomposição: {e}")


def plot_distribution(
    df: pd.DataFrame,
    column: str,
    figsize: tuple = (10, 6)
):
    """
    Plota distribuição de uma variável.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados
        column (str): Coluna para plotar
        figsize (tuple): Tamanho da figura
    """
    try:
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Histograma
        axes[0].hist(df[column].dropna(), bins=30, color='skyblue', edgecolor='black')
        axes[0].set_xlabel(column)
        axes[0].set_ylabel('Frequência')
        axes[0].set_title(f'Distribuição de {column}')
        axes[0].grid(True, alpha=0.3)
        
        # Box plot
        axes[1].boxplot(df[column].dropna())
        axes[1].set_ylabel(column)
        axes[1].set_title(f'Box Plot de {column}')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Erro ao plotar distribuição: {e}")
