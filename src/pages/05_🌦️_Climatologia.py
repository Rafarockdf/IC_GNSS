"""
Página de Climatologia.
Anomalias (Z-score) de TRWET nas resoluções diária, semanal e mensal,
com seleção de ano específico e de defasagem (lag) para a correlação
com a precipitação (INMET) — baseado na análise do notebook
EstudoGNSS/codigo.ipynb.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ESTACOES, STREAMLIT_CONFIG
from components.sidebar import sidebar_about, sidebar_theme_selector, apply_theme
from utils.data_loader import load_troposphere_data, load_precipitation_daily
from utils.climatology import (
    RESOLUCOES,
    LAG_MAXIMO,
    build_series,
    compute_climatology,
    climatology_profile,
    merge_with_precipitation,
    correlation_summary,
    lag_correlation,
    composite_analysis,
    confusion_matrix_signs,
    heatmap_matrix,
    period_labels,
)


def render_climatologia():
    st.set_page_config(**STREAMLIT_CONFIG)

    theme_name = sidebar_theme_selector()
    apply_theme(theme_name)

    st.title("🌦️ Climatologia e Anomalias (Z-score)")
    st.markdown("---")

    # ------------------------------------------------------------------
    # Sidebar - controles específicos desta página
    # ------------------------------------------------------------------
    st.sidebar.header("⚙️ Parâmetros da Climatologia")

    station = st.sidebar.selectbox(
        "Estação:",
        options=list(ESTACOES.keys()),
        format_func=lambda x: f"{x} - {ESTACOES[x]}",
        key="clima_station",
    )

    resolucao = st.sidebar.radio(
        "Resolução climatológica:",
        options=RESOLUCOES,
        index=2,
        key="clima_resolucao",
    )

    metodo = st.sidebar.selectbox(
        "Método de correlação:",
        options=["spearman", "pearson"],
        key="clima_metodo",
    )

    st.markdown(
        "Carregando dados de troposfera (GNSS) e precipitação (INMET). "
        "A primeira execução processa os arquivos brutos `.trop` e monta um "
        "cache local — as próximas execuções são instantâneas."
    )

    with st.spinner("📥 Carregando dados de troposfera..."):
        trop_data, trop_daily, _ = load_troposphere_data(station=station)

    if trop_data.empty:
        st.warning(
            f"⚠️ Nenhum dado de troposfera encontrado para a estação **{station}** "
            f"em `database/dados_gnss/{station}`."
        )
        sidebar_about()
        return

    anos_disponiveis = sorted(trop_daily.index.year.unique().tolist())
    ano_opcoes = ["Todos os anos"] + [str(a) for a in anos_disponiveis]
    ano_selecionado = st.sidebar.selectbox("Ano específico:", options=ano_opcoes, key="clima_ano")

    lag_max_ui = LAG_MAXIMO[resolucao]
    lag = st.sidebar.slider(
        f"Lag ({resolucao.lower()}) — precipitação em relação ao ZWD:",
        min_value=0,
        max_value=lag_max_ui,
        value=0,
        key="clima_lag",
    )

    # ------------------------------------------------------------------
    # Séries e climatologia
    # ------------------------------------------------------------------
    serie = build_series(trop_daily, resolucao)
    anomaly_df = compute_climatology(serie, resolucao)
    perfil = climatology_profile(anomaly_df)

    if ano_selecionado != "Todos os anos":
        ano_int = int(ano_selecionado)
        anomaly_view = anomaly_df[anomaly_df["ano"] == ano_int]
    else:
        anomaly_view = anomaly_df

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Estação", station)
    with col2:
        st.metric("Resolução", resolucao)
    with col3:
        st.metric("Registros na resolução", len(anomaly_df))

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([
        "📆 Perfil Climatológico",
        "📊 Anomalias (Z-score)",
        "🌧️ Correlação com Precipitação",
    ])

    # ------------------------------------------------------------------
    # Tab 1: Perfil climatológico
    # ------------------------------------------------------------------
    with tab1:
        st.subheader(f"Perfil Climatológico — {resolucao}")
        st.caption("Média histórica ± desvio-padrão de TRWET por período do ano (dia/semana/mês).")

        fig, ax = plt.subplots(figsize=(13, 5))
        x = perfil.index.to_numpy()
        labels_x = period_labels(resolucao, x)

        ax.plot(labels_x, perfil["media"], color="steelblue", label="Média climatológica", linewidth=2)
        ax.fill_between(
            labels_x,
            perfil["media"] - perfil["desvio_padrao"],
            perfil["media"] + perfil["desvio_padrao"],
            color="steelblue",
            alpha=0.2,
            label="± 1 desvio-padrão",
        )

        if ano_selecionado != "Todos os anos":
            ano_int = int(ano_selecionado)
            serie_ano = anomaly_df[anomaly_df["ano"] == ano_int].set_index("periodo")["valor"]
            serie_ano = serie_ano.reindex(perfil.index)
            ax.plot(labels_x, serie_ano.values, color="darkorange", marker="o", markersize=3,
                     linewidth=1.5, label=f"Ano {ano_int}")

        ax.set_xlabel(resolucao)
        ax.set_ylabel("TRWET (mm)")
        ax.set_title(f"Climatologia de TRWET ({resolucao}) - {station}")
        ax.legend()
        ax.grid(True, alpha=0.3)
        if resolucao != "Mensal":
            step = max(1, len(labels_x) // 30)
            ax.set_xticks(range(0, len(labels_x), step))
            ax.set_xticklabels([labels_x[i] for i in range(0, len(labels_x), step)], rotation=90)
        plt.tight_layout()
        st.pyplot(fig)

        with st.expander("📋 Tabela do perfil climatológico"):
            tabela = perfil.copy()
            tabela.index = period_labels(resolucao, tabela.index)
            st.dataframe(tabela, use_container_width=True)

    # ------------------------------------------------------------------
    # Tab 2: Anomalias
    # ------------------------------------------------------------------
    with tab2:
        st.subheader(f"Anomalia Padronizada (Z-score) — {resolucao}")

        if anomaly_view.empty:
            st.info("Sem dados para o ano selecionado.")
        else:
            fig, ax = plt.subplots(figsize=(15, 5))
            cores = ["red" if v < 0 else "blue" for v in anomaly_view["zscore"].fillna(0)]
            eixo_x = anomaly_view.index.strftime(
                "%d/%m/%Y" if resolucao != "Mensal" else "%m/%Y"
            )
            ax.bar(eixo_x, anomaly_view["zscore"], color=cores, width=0.7, edgecolor="black", alpha=0.75)
            ax.axhline(0, color="black", linewidth=1.2)
            ax.set_title(f"Anomalia Padronizada de TRWET (Z-score) - {station} - {resolucao}")
            ax.set_xlabel("Período")
            ax.set_ylabel("Desvios-padrão (Z)")
            ax.grid(axis="y", linestyle="--", alpha=0.4)
            ax.xaxis.set_major_locator(plt.MaxNLocator(25))
            plt.xticks(rotation=90)
            plt.tight_layout()
            st.pyplot(fig)

        if ano_selecionado == "Todos os anos" and resolucao in ("Mensal", "Semanal"):
            st.markdown(f"**Heatmap Ano x {resolucao}**")
            pivot = heatmap_matrix(anomaly_df, resolucao)
            pivot.columns = period_labels(resolucao, pivot.columns)

            fig2, ax2 = plt.subplots(figsize=(max(10, pivot.shape[1] * 0.6), max(6, pivot.shape[0] * 0.35)))
            sns.heatmap(
                pivot,
                cmap="RdBu",
                center=0,
                annot=(resolucao == "Mensal"),
                fmt=".1f",
                linewidths=0.5,
                ax=ax2,
            )
            ax2.set_title(f"Heatmap de Anomalias (Z-score TRWET) - {station}")
            ax2.set_xlabel(resolucao)
            ax2.set_ylabel("Ano")
            plt.tight_layout()
            st.pyplot(fig2)
        elif ano_selecionado == "Todos os anos":
            st.caption(
                "O heatmap Ano x Período fica muito denso na resolução diária "
                "(366 colunas); selecione Mensal ou Semanal para visualizá-lo."
            )

    # ------------------------------------------------------------------
    # Tab 3: Correlação com precipitação
    # ------------------------------------------------------------------
    with tab3:
        st.subheader("Correlação entre Anomalias de ZWD e Precipitação")

        with st.spinner("📥 Carregando dados de precipitação (INMET)..."):
            prec_daily = load_precipitation_daily()

        if prec_daily.empty:
            st.warning(
                "⚠️ Nenhum arquivo de precipitação do INMET foi encontrado em "
                "`database/dados_inmet` ou `EstudoGNSS`. Adicione um export do "
                "portal INMET (`;` separado) para habilitar esta análise."
            )
        else:
            merged = merge_with_precipitation(anomaly_df, prec_daily, resolucao)

            if ano_selecionado != "Todos os anos":
                merged = merged[merged["ano"] == int(ano_selecionado)]

            if merged.empty or len(merged) < 3:
                st.warning(
                    f"⚠️ Apenas {len(merged)} período(s) em comum entre GNSS e INMET "
                    f"nesta resolução/ano — dados insuficientes para uma correlação robusta. "
                    f"Cobertura de precipitação: {prec_daily.index.min().date()} a {prec_daily.index.max().date()}."
                )
            else:
                resumo = correlation_summary(merged)
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Períodos em comum (n)", resumo["n"])
                with c2:
                    st.metric("Pearson R", f"{resumo['pearson_r']:.3f}", f"p={resumo['pearson_p']:.4f}")
                with c3:
                    st.metric("Spearman R", f"{resumo['spearman_r']:.3f}", f"p={resumo['spearman_p']:.4f}")

                fig3, ax3 = plt.subplots(figsize=(7, 5.5))
                sns.regplot(
                    x=merged["zscore_zwd"], y=merged["zscore_prec"],
                    scatter_kws={"alpha": 0.6, "color": "blue"}, line_kws={"color": "red"}, ax=ax3,
                )
                ax3.axhline(0, color="black", linestyle="--", alpha=0.5)
                ax3.axvline(0, color="black", linestyle="--", alpha=0.5)
                ax3.set_title(f"Anomalias ZWD x Precipitação (R = {resumo['pearson_r']:.2f})")
                ax3.set_xlabel("Anomalia Padronizada do ZWD")
                ax3.set_ylabel("Anomalia Padronizada da Precipitação")
                ax3.grid(True, alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig3)

                st.markdown(f"**Correlação com defasagem (lag = 0 a {lag_max_ui} {resolucao.lower()})**")
                lag_df = lag_correlation(merged, max_lag=lag_max_ui, method=metodo)

                fig4, ax4 = plt.subplots(figsize=(9, 4))
                cores_lag = ["teal" if l != lag else "darkorange" for l in lag_df["lag"]]
                ax4.bar(lag_df["lag"], lag_df["r"], color=cores_lag, edgecolor="black", alpha=0.85)
                ax4.set_title(f"Correlação ({metodo}) com Defasagem — lag selecionado destacado")
                ax4.set_xlabel(f"Defasagem ({resolucao.lower()})")
                ax4.set_ylabel("Coeficiente de Correlação (R)")
                ax4.set_xticks(lag_df["lag"])
                ax4.grid(axis="y", linestyle="--", alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig4)

                linha_lag = lag_df[lag_df["lag"] == lag].iloc[0]
                st.info(
                    f"No lag selecionado ({lag} {resolucao.lower()}): "
                    f"R = {linha_lag['r']:.3f} (p = {linha_lag['p']:.4f}, n = {int(linha_lag['n'])})"
                    if not np.isnan(linha_lag["r"])
                    else f"Sem dados suficientes para o lag = {lag}."
                )

                st.markdown("**Composite Analysis** — precipitação por classe de anomalia do ZWD")
                st.dataframe(composite_analysis(merged), use_container_width=True)

                st.markdown("**Matriz de Confusão de Sinais**")
                conf_mes, total, concordancia, pct = confusion_matrix_signs(merged)

                cc1, cc2 = st.columns([1, 1])
                with cc1:
                    fig5, ax5 = plt.subplots(figsize=(5, 4.5))
                    sns.heatmap(
                        conf_mes, annot=True, fmt="d", cmap="Blues", linewidths=1.5,
                        cbar=True, square=True, annot_kws={"size": 13, "weight": "bold"}, ax=ax5,
                    )
                    ax5.set_xlabel("Z-score Precipitação (INMET)")
                    ax5.set_ylabel("Z-score ZWD (GNSS)")
                    plt.tight_layout()
                    st.pyplot(fig5)
                with cc2:
                    st.metric("Total de períodos analisados", total)
                    st.metric("Sinais concordantes", concordancia)
                    st.metric("Taxa de concordância", f"{pct:.1f}%")

    sidebar_about()


if __name__ == "__main__":
    render_climatologia()