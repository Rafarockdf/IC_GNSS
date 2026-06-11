"""
Página de Decomposição de Série Temporal.
Analisa componentes de trend, sazonalidade e resíduos.
"""

import streamlit as st
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ESTACOES, STREAMLIT_CONFIG
from components.sidebar import sidebar_filters, sidebar_about, sidebar_theme_selector, apply_theme
from components.charts import plot_decomposition
from utils.data_loader import load_troposphere_data
from utils.analysis import decompose_series, smooth_data


def render_decomposition():
    """Renderiza a página de decomposição."""
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Aplicar tema selecionado
    theme_name = sidebar_theme_selector()
    apply_theme(theme_name)
    
    st.title("🔍 Decomposição de Série Temporal")
    st.markdown("---")
    
    # Filtros
    filters = sidebar_filters()
    
    try:
        # Carregar dados
        with st.spinner("📥 Carregando dados..."):
            data = load_troposphere_data(
                station=filters['station'],
                start_date=filters['start_date'].strftime('%Y-%m-%d'),
                end_date=filters['end_date'].strftime('%Y-%m-%d')
            )
        
        if data.empty:
            st.warning("⚠️ Nenhum dado disponível para o período selecionado")
            return
        
        # Opções de decomposição
        st.subheader("Configurações de Decomposição")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            column = st.selectbox(
                "Selecione a coluna para decompor",
                data.select_dtypes(include=[np.number]).columns.tolist()
            )
        
        with col2:
            period = st.slider(
                "Período de sazonalidade",
                min_value=7,
                max_value=365,
                value=30,
                step=1
            )
        
        with col3:
            model = st.selectbox(
                "Tipo de modelo",
                ["additive", "multiplicative"]
            )
        
        st.markdown("---")
        
        # Realizar decomposição
        if st.button("🔍 Executar Decomposição", use_container_width=True):
            with st.spinner("Decompondendo série temporal..."):
                decomposition = decompose_series(
                    data,
                    column=column,
                    period=period,
                    model=model
                )
            
            if decomposition:
                # Plotar decomposição
                plot_decomposition(decomposition)
                
                # Estatísticas dos componentes
                st.subheader("📊 Estatísticas dos Componentes")
                
                col1, col2, col3, col4 = st.columns(4)
                
                components = {
                    "Original": decomposition['observed'],
                    "Tendência": decomposition['trend'],
                    "Sazonalidade": decomposition['seasonal'],
                    "Resíduos": decomposition['residual']
                }
                
                cols = [col1, col2, col3, col4]
                
                for idx, (name, component) in enumerate(components.items()):
                    with cols[idx]:
                        st.write(f"**{name}**")
                        st.metric("Média", f"{component.mean():.2f}")
                        st.metric("Desvio Padrão", f"{component.std():.2f}")
                        st.metric("Min", f"{component.min():.2f}")
                        st.metric("Max", f"{component.max():.2f}")
            else:
                st.error("❌ Não foi possível executar a decomposição. Verifique se há dados suficientes.")
        
        # Exibir dados
        st.subheader("📄 Dados Utilizados")
        
        with st.expander("Ver dados brutos"):
            st.dataframe(data.head(20), use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Erro na análise: {e}")
    
    sidebar_about()


if __name__ == "__main__":
    render_decomposition()
