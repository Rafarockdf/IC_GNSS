"""
Página de Configurações.
Permite ajustar preferências e visualizar informações do projeto.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import STREAMLIT_CONFIG, DATABASE_DIR, DADOS_DIR
from components.sidebar import sidebar_theme_selector, apply_theme
from utils.themes import get_theme


def render_settings():
    """Renderiza a página de configurações."""
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Aplicar tema selecionado
    theme_name = sidebar_theme_selector()
    apply_theme(theme_name)
    
    st.title("⚙️ Configurações")
    st.markdown("---")
    
    # Abas de configuração
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎨 Tema",
        "🔧 Preferências",
        "📁 Caminhos do Projeto",
        "ℹ️ Informações do Sistema"
    ])
    
    with tab1:
        st.subheader("Tema da Aplicação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **Tema Selecionado**
            
            Escolha um tema na barra lateral para personalizar a aparência da aplicação.
            """)
        
        with col2:
            # Mostrar informações do tema atual
            current_theme = get_theme(theme_name)
            theme_label = '☀️ Claro' if theme_name == 'light' else '🌙 Escuro'
            st.write(f"**Tema Ativo**: {theme_label}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**Cor Primária**")
                st.color_picker(
                    "Cor Primária",
                    value=current_theme.primary,
                    disabled=True,
                    key="primary_color"
                )
            
            with col_b:
                st.write("**Cor Secundária**")
                st.color_picker(
                    "Cor Secundária",
                    value=current_theme.secondary,
                    disabled=True,
                    key="secondary_color"
                )
            
            col_c, col_d = st.columns(2)
            with col_c:
                st.write("**Cor de Sucesso**")
                st.color_picker(
                    "Cor de Sucesso",
                    value=current_theme.success,
                    disabled=True,
                    key="success_color"
                )
            
            with col_d:
                st.write("**Cor de Perigo**")
                st.color_picker(
                    "Cor de Perigo",
                    value=current_theme.danger,
                    disabled=True,
                    key="danger_color"
                )
        
        st.markdown("---")
        
        # Preview do tema
        st.subheader("Preview")
        
        preview_col1, preview_col2, preview_col3 = st.columns(3)
        
        with preview_col1:
            st.success("✅ Sucesso")
        
        with preview_col2:
            st.warning("⚠️ Aviso")
        
        with preview_col3:
            st.error("❌ Erro")
    
    with tab2:
        st.subheader("Preferências do Usuário")
        
        # Tema
        theme = st.selectbox(
            "Tema da Aplicação",
            ["Claro", "Escuro", "Auto"],
            index=2
        )
        
        # Formato de data
        date_format = st.selectbox(
            "Formato de Data",
            ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"]
        )
        
        # Precisão de casas decimais
        decimals = st.slider(
            "Casas Decimais para Valores Numéricos",
            min_value=2,
            max_value=10,
            value=4
        )
        
        # Salvar preferências
        if st.button("💾 Salvar Preferências", use_container_width=True):
            st.success("✅ Preferências salvas com sucesso!")
    
    with tab2:
        st.subheader("Caminhos do Projeto")
        
        paths = {
            "📦 Diretório do Banco de Dados": str(DATABASE_DIR),
            "📊 Dados GNSS": str(DADOS_DIR),
            "📁 Diretório Base": str(Path(__file__).parent.parent.parent),
        }
        
        for name, path in paths.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.code(path, language="bash")
            with col2:
                # Verificar se caminho existe
                exists = Path(path).exists()
                if exists:
                    st.success("✅")
                else:
                    st.error("❌")
    
    with tab3:
        st.subheader("Caminhos do Projeto")
        
        paths = {
            "📦 Diretório do Banco de Dados": str(DATABASE_DIR),
            "📊 Dados GNSS": str(DADOS_DIR),
            "📁 Diretório Base": str(Path(__file__).parent.parent.parent),
        }
        
        for name, path in paths.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.code(path, language="bash")
            with col2:
                # Verificar se caminho existe
                exists = Path(path).exists()
                if exists:
                    st.success("✅")
                else:
                    st.error("❌")
    
    with tab4:
        st.subheader("ℹ️ Informações do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Ambiente Python**")
            st.code(sys.executable, language="bash")
            
            st.write("**Versão do Python**")
            st.code(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        with col2:
            st.write("**Versão do Streamlit**")
            try:
                import streamlit as st_check
                st.code(st_check.__version__)
            except:
                st.code("Desconhecida")
            
            st.write("**Diretório de Trabalho**")
            st.code(os.getcwd(), language="bash")
        
        st.divider()
        
        st.write("**Pacotes Instalados Principais**")
        packages = {
            "pandas": "pd",
            "numpy": "np",
            "matplotlib": "matplotlib",
            "seaborn": "sns",
            "scipy": "scipy",
            "statsmodels": "statsmodels",
        }
        
        cols = st.columns(3)
        for idx, (package, alias) in enumerate(packages.items()):
            try:
                __import__(package)
                cols[idx % 3].success(f"✅ {package}")
            except ImportError:
                cols[idx % 3].error(f"❌ {package}")
        
        st.divider()
        
        st.write("**Debug Mode**")
        debug_mode = st.checkbox("Ativar Modo Debug", value=False)
        
        if debug_mode:
            st.warning("⚠️ Modo debug ativado. Podem aparecer mensagens técnicas.")
            
            # Exibir variáveis de sessão
            st.write("**Variáveis de Sessão Streamlit**")
            st.code(str(dict(st.session_state)), language="python")
            
            # Opção para limpar cache
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("🗑️ Limpar Cache do Streamlit", use_container_width=True):
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.success("Cache limpo com sucesso!")
            
            with col_b:
                if st.button("🔄 Recarregar Aplicação", use_container_width=True):
                    st.rerun()


if __name__ == "__main__":
    render_settings()
