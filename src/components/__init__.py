"""Pacote de componentes reutilizáveis."""

from .sidebar import sidebar_filters, sidebar_theme_selector, sidebar_about, apply_theme
from .charts import plot_time_series, plot_correlation_matrix, plot_decomposition, plot_distribution

__all__ = [
    "sidebar_filters",
    "sidebar_theme_selector",
    "sidebar_about",
    "apply_theme",
    "plot_time_series",
    "plot_correlation_matrix",
    "plot_decomposition",
    "plot_distribution",
]
