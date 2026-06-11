"""
Página de Análise de Correlação.
Analisa a correlação entre variáveis.
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
from components.charts import plot_correlation_matrix
from utils.data_loader import load_troposphere_data, load_inmet_data
from utils.analysis import correlate_data


def render_correlation_analysis():
    """Renderiza a página de análise de correlação."""
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Aplicar tema selecionado
    theme_name = sidebar_theme_selector()
    apply_theme(theme_name)
    
    st.title("📈 Análise de Correlação")
    st.markdown("---")
    
    # Filtros
    filters = sidebar_filters()
    
    try:
        # Carregar dados
        with st.spinner("📥 Carregando dados..."):
            trop_data = load_troposphere_data(
                station=filters['station'],
                start_date=filters['start_date'].strftime('%Y-%m-%d'),
                end_date=filters['end_date'].strftime('%Y-%m-%d')
            )
            
            inmet_data = load_inmet_data(
                start_date=filters['start_date'].strftime('%Y-%m-%d'),
                end_date=filters['end_date'].strftime('%Y-%m-%d')
            )
        
        if trop_data.empty and inmet_data.empty:
            st.warning("⚠️ Nenhum dado disponível para o período selecionado")
            return
        
        # Abas para diferentes análises
        tab1, tab2, tab3 = st.tabs([
            "🔗 Correlação Geral",
            "📊 Matriz de Correlação",
            "🎯 Correlação Específica"
        ])
        
        with tab1:
            st.subheader("Correlação entre Troposfera e INMET")
            
            col1, col2 = st.columns(2)
            
            with col1:
                method = st.selectbox(
                    "Método de correlação",
                    ["pearson", "spearman"],
                    key="corr_method"
                )
            
            with col2:
                st.info(f"Método selecionado: **{method}**")
            
            if not trop_data.empty and not inmet_data.empty:
                # Tentar correlacionar colunas numéricas
                trop_numeric = trop_data.select_dtypes(include=[np.number]).columns.tolist()
                inmet_numeric = inmet_data.select_dtypes(include=[np.number]).columns.tolist()
                
                if trop_numeric and inmet_numeric:
                    results = []
                    
                    for trop_col in trop_numeric[:5]:  # Limitar a 5 colunas
                        for inmet_col in inmet_numeric[:5]:
                            # Alinhar índices se necessário
                            common_index = trop_data.index.intersection(inmet_data.index)
                            if len(common_index) > 1:
                                corr, pvalue = correlate_data(
                                    pd.DataFrame({
                                        'col1': trop_data.loc[common_index, trop_col],
                                        'col2': inmet_data.loc[common_index, inmet_col]
                                    }),
                                    'col1', 'col2',
                                    method=method
                                )
                                
                                if not np.isnan(corr):
                                    results.append({
                                        'Troposfera': trop_col,
                                        'INMET': inmet_col,
                                        'Correlação': corr,
                                        'P-value': pvalue
                                    })
                    
                    if results:
                        results_df = pd.DataFrame(results)
                        results_df = results_df.sort_values('Correlação', ascending=False)
                        st.dataframe(results_df, use_container_width=True)
                    else:
                        st.info("Nenhuma correlação calculada")
                else:
                    st.warning("⚠️ Dados insuficientes para correlação")
            else:
                st.warning("⚠️ Dados de troposfera ou INMET não disponíveis")
        
        with tab2:
            st.subheader("Matriz de Correlação - Troposfera")
            
            if not trop_data.empty:
                numeric_cols = trop_data.select_dtypes(include=[np.number]).columns.tolist()
                
                if numeric_cols:
                    plot_correlation_matrix(trop_data, numeric_cols[:8])
                else:
                    st.warning("⚠️ Nenhuma coluna numérica encontrada")
            else:
                st.warning("⚠️ Dados de troposfera não disponíveis")
        
        with tab3:
            st.subheader("Correlação Específica")
            
            col1, col2 = st.columns(2)
            
            numeric_cols = trop_data.select_dtypes(include=[np.number]).columns.tolist() if not trop_data.empty else []
            
            with col1:
                col1_name = st.selectbox(
                    "Selecione primeira coluna",
                    numeric_cols,
                    key="col1_select"
                )
            
            with col2:
                col2_name = st.selectbox(
                    "Selecione segunda coluna",
                    numeric_cols,
                    key="col2_select"
                )
            
            if col1_name and col2_name and not trop_data.empty:
                corr, pvalue = correlate_data(
                    trop_data,
                    col1_name,
                    col2_name,
                    method=filters['correlation_method']
                )
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Correlação", f"{corr:.4f}")
                
                with col2:
                    st.metric("P-value", f"{pvalue:.6f}")
                
                with col3:
                    if pvalue < 0.05:
                        st.success("✅ Significativo (p < 0.05)")
                    else:
                        st.warning("⚠️ Não significativo (p ≥ 0.05)")
    
    except Exception as e:
        st.error(f"❌ Erro na análise: {e}")
    
    sidebar_about()


if __name__ == "__main__":
    render_correlation_analysis()
