"""
Módulo de gerenciamento de temas.
Define paletas de cores e estilos para a aplicação.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Theme:
    """Classe para representar um tema."""
    name: str
    primary: str
    secondary: str
    success: str
    danger: str
    warning: str
    info: str
    background: str
    secondary_background: str
    text_color: str
    text_secondary: str
    border_color: str
    
    def to_dict(self) -> Dict[str, str]:
        """Converte o tema para dicionário."""
        return {
            'primary': self.primary,
            'secondary': self.secondary,
            'success': self.success,
            'danger': self.danger,
            'warning': self.warning,
            'info': self.info,
            'background': self.background,
            'secondary_background': self.secondary_background,
            'text_color': self.text_color,
            'text_secondary': self.text_secondary,
            'border_color': self.border_color,
        }


# Tema Claro
LIGHT_THEME = Theme(
    name="Claro",
    primary="#1f77b4",
    secondary="#ff7f0e",
    success="#2ca02c",
    danger="#d62728",
    warning="#ff9896",
    info="#17becf",
    background="#ffffff",
    secondary_background="#f0f2f6",
    text_color="#262730",
    text_secondary="#666666",
    border_color="#e0e0e0",
)

# Tema Escuro
DARK_THEME = Theme(
    name="Escuro",
    primary="#1f77b4",
    secondary="#ff7f0e",
    success="#2ca02c",
    danger="#d62728",
    warning="#ff9896",
    info="#17becf",
    background="#0e1117",
    secondary_background="#1c2128",
    text_color="#e6edf3",
    text_secondary="#8b949e",
    border_color="#30363d",
)

# Dicionário de temas disponíveis
THEMES = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
}


def get_theme(theme_name: str) -> Theme:
    """
    Obtém um tema pelo nome.
    
    Args:
        theme_name (str): Nome do tema ('light' ou 'dark')
        
    Returns:
        Theme: Objeto do tema
    """
    return THEMES.get(theme_name, LIGHT_THEME)


def apply_theme_css(theme: Theme) -> str:
    """
    Gera CSS customizado baseado no tema.
    
    Args:
        theme (Theme): Objeto do tema
        
    Returns:
        str: CSS customizado
    """
    css = f"""
    <style>
        /* Variáveis CSS */
        :root {{
            --primary-color: {theme.primary};
            --secondary-color: {theme.secondary};
            --success-color: {theme.success};
            --danger-color: {theme.danger};
            --warning-color: {theme.warning};
            --info-color: {theme.info};
        }}
        
        /* Custom Classes para elementos específicos */
        .main-header {{
            color: {theme.text_color} !important;
        }}
        
        .info-box {{
            background-color: {theme.secondary_background};
            color: {theme.text_color};
            border: 1px solid {theme.border_color};
            border-radius: 8px;
            padding: 15px;
        }}
        
        /* Scrollbar customizado */
        ::-webkit-scrollbar {{
            width: 10px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {theme.secondary_background};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {theme.primary};
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {theme.secondary};
        }}
    </style>
    """
    return css
