"""
Módulo de análise climatológica.
Generaliza, para as resoluções diária, semanal e mensal, a análise de
climatologia/anomalias (Z-score), correlação com precipitação (com lag),
composite analysis e matriz de confusão de sinais originalmente feita
no notebook EstudoGNSS/codigo.ipynb.
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

RESOLUCOES = ["Diária", "Semanal", "Mensal"]

_RESAMPLE_RULE = {
    "Diária": "D",
    "Semanal": "W-SUN",
    "Mensal": "MS",
}

# Limites razoáveis de lag (na unidade da própria resolução) para a UI
LAG_MAXIMO = {
    "Diária": 30,
    "Semanal": 12,
    "Mensal": 12,
}


def build_series(daily_series: pd.Series, resolucao: str) -> pd.Series:
    """Agrega a série diária de TRWET para a resolução escolhida (média)."""
    rule = _RESAMPLE_RULE[resolucao]
    if resolucao == "Diária":
        return daily_series
    return daily_series.resample(rule).mean()


def _period_key(index: pd.DatetimeIndex, resolucao: str) -> np.ndarray:
    """Retorna o 'período do ano' (chave da climatologia) de cada timestamp."""
    if resolucao == "Mensal":
        return index.month.to_numpy()
    if resolucao == "Semanal":
        return index.isocalendar().week.to_numpy()
    return index.dayofyear.to_numpy()


def compute_climatology(series: pd.Series, resolucao: str) -> pd.DataFrame:
    """
    Calcula a climatologia (média/desvio-padrão por período do ano) e a
    anomalia padronizada (Z-score) de cada observação da série.

    Returns:
        DataFrame indexado por data com colunas:
        valor, periodo, ano, climatologia_media, climatologia_std, zscore
    """
    df = series.dropna().to_frame(name="valor")
    df["periodo"] = _period_key(df.index, resolucao)
    df["ano"] = df.index.year

    clima_media = df.groupby("periodo")["valor"].mean()
    clima_std = df.groupby("periodo")["valor"].std()

    df["climatologia_media"] = df["periodo"].map(clima_media)
    df["climatologia_std"] = df["periodo"].map(clima_std)
    df["zscore"] = (df["valor"] - df["climatologia_media"]) / df["climatologia_std"]

    return df


def climatology_profile(anomaly_df: pd.DataFrame) -> pd.DataFrame:
    """Perfil climatológico (média ± desvio-padrão) por período do ano."""
    perfil = anomaly_df.groupby("periodo")["valor"].agg(["mean", "std", "count"])
    perfil.columns = ["media", "desvio_padrao", "n_amostras"]
    return perfil.sort_index()


def merge_with_precipitation(
    zwd_anomaly: pd.DataFrame,
    prec_series: pd.Series,
    resolucao: str,
) -> pd.DataFrame:
    """
    Junta a anomalia de ZWD com a precipitação agregada na mesma resolução,
    recalculando o Z-score da precipitação (climatologia própria) e alinhando
    pelas mesmas chaves (ano, período).
    """
    if prec_series is None or prec_series.empty:
        return pd.DataFrame()

    rule = _RESAMPLE_RULE[resolucao]
    if resolucao == "Diária":
        prec_agg = prec_series
    else:
        prec_agg = prec_series.resample(rule).sum()

    prec_df = compute_climatology(prec_agg, resolucao)
    prec_df = prec_df.rename(columns={"valor": "precipitacao", "zscore": "zscore_prec"})

    zwd_df = zwd_anomaly.rename(columns={"valor": "TRWET", "zscore": "zscore_zwd"})

    merged = pd.merge(
        zwd_df.reset_index().rename(columns={"index": "data"}),
        prec_df.reset_index().rename(columns={"index": "data"})[["ano", "periodo", "precipitacao", "zscore_prec"]],
        on=["ano", "periodo"],
        how="inner",
    ).dropna(subset=["zscore_zwd", "zscore_prec"])

    date_col = merged.columns[0]
    merged = merged.set_index(date_col).sort_index()
    return merged


def correlation_summary(merged: pd.DataFrame) -> dict:
    """Pearson e Spearman entre as anomalias de ZWD e precipitação."""
    if merged.empty or len(merged) < 3:
        return {"pearson_r": np.nan, "pearson_p": np.nan, "spearman_r": np.nan, "spearman_p": np.nan, "n": len(merged)}

    r_p, p_p = pearsonr(merged["zscore_zwd"], merged["zscore_prec"])
    r_s, p_s = spearmanr(merged["zscore_zwd"], merged["zscore_prec"])
    return {"pearson_r": r_p, "pearson_p": p_p, "spearman_r": r_s, "spearman_p": p_s, "n": len(merged)}


def lag_correlation(merged: pd.DataFrame, max_lag: int, method: str = "spearman") -> pd.DataFrame:
    """
    Correlação entre a anomalia de ZWD e a precipitação com defasagem (lag),
    na unidade da resolução escolhida: ZWD no período t, precipitação em t+lag.
    """
    zwd = merged["zscore_zwd"]
    prec = merged["zscore_prec"]

    resultados = []
    for lag in range(max_lag + 1):
        if lag == 0:
            x, y = zwd, prec
        else:
            if lag >= len(zwd):
                resultados.append({"lag": lag, "r": np.nan, "p": np.nan, "n": 0})
                continue
            x, y = zwd.iloc[:-lag], prec.iloc[lag:]

        if len(x) < 3:
            resultados.append({"lag": lag, "r": np.nan, "p": np.nan, "n": len(x)})
            continue

        if method == "spearman":
            r, p = spearmanr(x.to_numpy(), y.to_numpy())
        else:
            r, p = pearsonr(x.to_numpy(), y.to_numpy())
        resultados.append({"lag": lag, "r": r, "p": p, "n": len(x)})

    return pd.DataFrame(resultados)


def composite_analysis(merged: pd.DataFrame) -> pd.DataFrame:
    """Média/probabilidade de precipitação positiva por classe de anomalia de ZWD."""
    bins = [-np.inf, -1, 0, 1, np.inf]
    labels = ["ZWD < -1", "-1 <= ZWD < 0", "0 <= ZWD < 1", "ZWD >= 1"]

    df = merged.copy()
    df["Classe_ZWD"] = pd.cut(df["zscore_zwd"], bins=bins, labels=labels)

    composite = df.groupby("Classe_ZWD", observed=False).agg(
        Media_PREC=("zscore_prec", "mean"),
        N_Casos=("zscore_prec", "count"),
        Prob_PREC_Pos=("zscore_prec", lambda x: (x > 0).sum() / len(x) * 100 if len(x) else np.nan),
    )
    return composite


def confusion_matrix_signs(merged: pd.DataFrame) -> Tuple[pd.DataFrame, int, int, float]:
    """Matriz de confusão de sinais (ZWD +/- vs Precipitação +/-)."""
    sinal_zwd = np.where(merged["zscore_zwd"] >= 0, "ZWD (+)", "ZWD (-)")
    sinal_prec = np.where(merged["zscore_prec"] >= 0, "PREC (+)", "PREC (-)")

    conf_matrix = pd.crosstab(sinal_zwd, sinal_prec)
    classes_y = ["ZWD (+)", "ZWD (-)"]
    classes_x = ["PREC (+)", "PREC (-)"]
    conf_matrix = conf_matrix.reindex(index=classes_y, columns=classes_x, fill_value=0)

    total = int(conf_matrix.values.sum())
    concordancia = int(np.trace(conf_matrix.values))
    pct = concordancia / total * 100 if total else 0.0

    return conf_matrix, total, concordancia, pct


def heatmap_matrix(anomaly_df: pd.DataFrame, resolucao: str) -> pd.DataFrame:
    """Matriz (ano x período) de Z-score para o heatmap de anomalias."""
    pivot = anomaly_df.pivot_table(index="ano", columns="periodo", values="zscore", aggfunc="mean")
    return pivot.sort_index()


def period_labels(resolucao: str, periods) -> list:
    """Rótulos amigáveis para o eixo de período (mês/semana/dia do ano)."""
    if resolucao == "Mensal":
        nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        return [nomes[int(p) - 1] if 1 <= int(p) <= 12 else str(p) for p in periods]
    if resolucao == "Semanal":
        return [f"Sem {int(p)}" for p in periods]
    return [f"Dia {int(p)}" for p in periods]