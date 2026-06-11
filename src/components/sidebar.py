"""Componentes da barra lateral (sidebar)."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from config import ESTACOES, ANALYSIS_CONFIG
from utils.themes import apply_theme_css, get_theme


def sidebar_theme_selector():
    """
    Cria o seletor de tema na barra lateral.
    
    Returns:
        str: Nome do tema selecionado ('light' ou 'dark')
    """
    st.sidebar.header("🎨 Tema")
    
    # Inicializar tema na sessão se não existir
    if 'selected_theme' not in st.session_state:
        st.session_state.selected_theme = 'light'
    
    # Seletor de tema com opções simples
    theme_choice = st.sidebar.radio(
        "Escolha o tema:",
        options=['light', 'dark'],
        format_func=lambda x: '☀️ Claro' if x == 'light' else '🌙 Escuro',
        index=0 if st.session_state.selected_theme == 'light' else 1,
        key="theme_radio"
    )
    
    # Salvar na sessão
    st.session_state.selected_theme = theme_choice
    
    return theme_choice


def sidebar_filters():
    """
    Cria os filtros na barra lateral.
    
    Returns:
        dict: Dicionário com os filtros selecionados
    """
    st.sidebar.header("⚙️ Filtros")
    
    # Seleção de estação
    station = st.sidebar.selectbox(
        "Selecione a Estação:",
        options=list(ESTACOES.keys()),
        format_func=lambda x: f"{x} - {ESTACOES[x]}"
    )
    
    # Seleção de período
    st.sidebar.subheader("Período")
    date_range = st.sidebar.date_input(
        "Intervalo de Datas:",
        value=(
            datetime.now() - timedelta(days=365),
            datetime.now()
        ),
        key="date_range"
    )
    
    # Seleção de variáveis
    st.sidebar.subheader("Variáveis")
    variables = st.sidebar.multiselect(
        "Selecione as variáveis para análise:",
        options=["TRWET", "Temperatura", "Umidade", "Precipitação"],
        default=["TRWET"]
    )
    
    # Opções avançadas
    with st.sidebar.expander("⚙️ Opções Avançadas"):
        smooth_data = st.checkbox("Suavizar dados", value=False)
        window_size = st.slider("Tamanho da janela", 3, 30, 7) if smooth_data else None
        show_trend = st.checkbox("Mostrar tendência", value=True)
        correlation_method = st.selectbox(
            "Método de correlação",
            options=["pearson", "spearman"],
            index=0
        )
    
    return {
        "station": station,
        "start_date": date_range[0] if isinstance(date_range, tuple) else date_range,
        "end_date": date_range[1] if isinstance(date_range, tuple) and len(date_range) > 1 else datetime.now(),
        "variables": variables,
        "smooth_data": smooth_data,
        "window_size": window_size,
        "show_trend": show_trend,
        "correlation_method": correlation_method,
    }


def sidebar_about():
    """Exibe informações sobre a aplicação na sidebar."""
    st.sidebar.divider()
    st.sidebar.header("ℹ️ Sobre")
    st.sidebar.info(
        """
        **GNSS Data Analyzer**
        
        Aplicação para análise de dados GNSS e troposfera.
        
        - 📊 Visualização de séries temporais
        - 📈 Análise de correlação
        - 🔍 Decomposição temporal
        - 📉 Estatísticas descritivas
        
        Desenvolvido para análise de dados de estações GNSS do Brasil.
        """
    )


def apply_theme(theme_name: str):
    """
    Aplica o tema selecionado à aplicação.
    
    Args:
        theme_name (str): Nome do tema ('light' ou 'dark')
    """
    theme = get_theme(theme_name)
    css = apply_theme_css(theme)
    st.markdown(css, unsafe_allow_html=True)
