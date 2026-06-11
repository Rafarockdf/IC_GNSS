"""
Aplicação principal Streamlit - GNSS Data Analyzer
Ponto de entrada para a aplicação.
"""

import streamlit as st
import sys
from pathlib import Path

# Configurar path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from config import STREAMLIT_CONFIG
from components.sidebar import sidebar_theme_selector, sidebar_about, apply_theme


def main():
    """Função principal da aplicação."""
    
    # Configurar página
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Aplicar tema selecionado
    theme_name = sidebar_theme_selector()
    apply_theme(theme_name)
    
    # CSS customizado
    st.markdown("""
    <style>
        .main-header {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .info-box {
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">📊 GNSS Data Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Introdução
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📍 Sobre o Projeto
        Aplicação para análise integrada de dados GNSS e meteorológicos
        de estações de posicionamento no Brasil.
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Funcionalidades
        - Visualização de séries temporais
        - Análise de correlação
        - Decomposição temporal
        - Estatísticas descritivas
        """)
    
    with col3:
        st.markdown("""
        ### 📊 Dados Disponíveis
        - **GNSS**: Troposfera Zenith Wet
        - **INMET**: Meteorologia
        - **Estações**: MGBH, MGMC
        """)
    
    st.markdown("---")
    
    # Seção de boas-vindas
    st.header("🚀 Comece por aqui")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        ✅ **Aplicação Pronta para Uso**
        
        A estrutura está totalmente configurada e pronta para análise de dados.
        Navegue pelos diferentes painéis no menu lateral para explorar os dados.
        """)
    
    with col2:
        st.info("""
        📚 **Documentação**
        
        - **Dashboard**: Visualize os dados e estatísticas gerais
        - **Correlação**: Analise correlações entre variáveis
        - **Decomposição**: Decomponha séries em componentes
        - **Configurações**: Ajuste as preferências da aplicação
        """)
    
    st.markdown("---")
    
    # Próximos passos
    st.header("📋 Próximos Passos")
    
    steps = """
    1. **Verificar dados**: Acesse o Dashboard para ver o status dos dados
    2. **Explorar correlações**: Use a página de Correlação para encontrar relações
    3. **Analisar tendências**: Use Decomposição para entender padrões temporais
    4. **Customizar**: Ajuste as configurações conforme necessário
    """
    
    st.markdown(steps)
    
    st.markdown("---")
    
    # Informações técnicas
    with st.expander("📊 Informações Técnicas"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Tecnologias Utilizadas**")
            st.markdown("""
            - Streamlit
            - Pandas
            - NumPy
            - Matplotlib
            - Seaborn
            - SciPy
            - Statsmodels
            """)
        
        with col2:
            st.write("**Estrutura do Projeto**")
            st.markdown("""
            ```
            src/
            ├── app.py
            ├── config.py
            ├── pages/
            ├── components/
            ├── utils/
            └── .streamlit/
            ```
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; margin-top: 40px;'>
        <p>GNSS Data Analyzer v1.0</p>
        <p>Desenvolvido para análise de dados GNSS e meteorológicos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar about
    sidebar_about()


if __name__ == "__main__":
    main()
