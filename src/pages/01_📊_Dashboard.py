"""
Página principal do Dashboard.
Exibe overview dos dados e estatísticas gerais.
"""

import streamlit as st
import sys
from pathlib import Path

# Configurar path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ESTACOES, STREAMLIT_CONFIG
from components.sidebar import sidebar_filters, sidebar_about, sidebar_theme_selector, apply_theme
from components.charts import plot_time_series, plot_distribution
from utils.data_loader import load_troposphere_data, load_inmet_data
from utils.analysis import calculate_statistics


def render_overview():
    """Renderiza a página de overview."""
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Aplicar tema selecionado
    theme_name = sidebar_theme_selector()
    apply_theme(theme_name)
    
    st.title("📊 Dashboard - GNSS Data Analyzer")
    st.markdown("---")
    
    # Obter filtros da sidebar
    filters = sidebar_filters()
    
    # Exibir informações da estação selecionada
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"📍 **Estação**: {filters['station']}")
    
    with col2:
        st.info(f"📅 **Período**: {filters['start_date'].strftime('%d/%m/%Y')} a {filters['end_date'].strftime('%d/%m/%Y')}")
    
    with col3:
        st.info(f"📈 **Variáveis**: {len(filters['variables'])} selecionadas")
    
    st.markdown("---")
    
    # Carregar dados
    st.subheader("Carregando dados...")
    
    try:
        # Carrega dados de troposfera
        with st.spinner("📥 Carregando dados de troposfera..."):
            trop_data, trop_data_day, trop_data_month = load_troposphere_data(
                station=filters['station'],
                start_date=filters['start_date'].strftime('%Y-%m-%d'),
                end_date=filters['end_date'].strftime('%Y-%m-%d')
            )
        
        # Carrega dados INMET
        with st.spinner("📥 Carregando dados INMET..."):
            inmet_data = load_inmet_data(
                start_date=filters['start_date'].strftime('%Y-%m-%d'),
                end_date=filters['end_date'].strftime('%Y-%m-%d')
            )
        
        # Exibir status dos dados
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Registros de Troposfera",
                value=len(trop_data) if not trop_data.empty else 0,
                delta="Dados GNSS"
            )
        
        with col2:
            st.metric(
                label="Registros INMET",
                value=len(inmet_data) if not inmet_data.empty else 0,
                delta="Dados Meteorológicos"
            )
        
        # Abas para diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Série Temporal",
            "📊 Distribuição",
            "📋 Estatísticas",
            "📄 Preview dos Dados"
        ])
        
        with tab1:
            st.subheader("Série Temporal")
            if not trop_data_day.empty:
                plot_time_series(
                    trop_data_day,
                    #date_column="data" if "data" in trop_data_day.columns else trop_data_day.columns[0],
                    #value_column="TRWET" if "TRWET" in trop_data_day.columns else trop_data_day.columns[1],
                    title="Troposfera Zenith Wet (TRWET)"
                )
            else:
                st.warning("⚠️ Nenhum dado de troposfera disponível para o período selecionado")
        
        with tab2:
            st.subheader("Distribuição de Dados")
            if not trop_data.empty and "TRWET" in trop_data.columns:
                plot_distribution(trop_data, "TRWET")
            else:
                st.warning("⚠️ Dados insuficientes para gerar gráfico de distribuição")
        
        with tab3:
            st.subheader("Estatísticas Descritivas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Dados de Troposfera (TRWET)**")
                if not trop_data.empty and "TRWET" in trop_data.columns:
                    stats = calculate_statistics(trop_data, "TRWET")
                    for key, value in stats.items():
                        st.metric(key.upper(), f"{value:.2f}" if isinstance(value, (int, float)) else value)
                else:
                    st.info("Nenhum dado disponível")
            
            with col2:
                st.write("**Dados INMET**")
                if not inmet_data.empty:
                    st.dataframe(inmet_data.describe(), use_container_width=True)
                else:
                    st.info("Nenhum dado disponível")
        
        with tab4:
            st.subheader("Preview dos Dados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Troposfera**")
                if not trop_data.empty:
                    st.dataframe(trop_data.head(10), use_container_width=True)
                else:
                    st.info("Nenhum dado disponível")
            
            with col2:
                st.write("**INMET**")
                if not inmet_data.empty:
                    st.dataframe(inmet_data.head(10), use_container_width=True)
                else:
                    st.info("Nenhum dado disponível")
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
    
    # Sidebar about
    sidebar_about()


if __name__ == "__main__":
    render_overview()
