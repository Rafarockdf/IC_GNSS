import streamlit as st
import plotly.express as px
import pandas as pd
import calendar
from datetime import datetime, timedelta
df = pd.read_csv(r"C:\Users\rafam\Desktop\IC_GNSS\EstudoGNSS\dados_troposfera_MGBH.csv")
df["data_completa"] = pd.to_datetime(df["data_completa"])
df["mes"] = df["data_completa"].dt.month_name()
df["date"] = df["data_completa"].dt.date
df_mensal = df.groupby(["mes"])["TROTOT"].mean().reset_index()

st.set_page_config(layout="wide", page_title="Dashboard TRWET", page_icon="🌧️")
st.title("🌧️ Dashboard TRWET – GNSS / TROP")
st.markdown("Visualização diária e mensal do **TRWET** a partir de arquivos `.trop`.")
st.markdown("---")

st.sidebar.title("⚙️ Controles")
anos_disponiveis = df["nm_ano"].unique().tolist()


anos_disponiveis.insert(0, "Todos")

opcao = st.sidebar.selectbox("Selecione o ano", anos_disponiveis)
d = st.sidebar.date_input("Selecione uma data","today","2009-01-01","2024-12-31")

d_date = pd.to_datetime(d)


st.write(d_date)
st.write(df["date"][0:2])
df = df[df["date"] == d_date.date()]



if opcao == "Todos":
    ano = anos_disponiveis
else:
    ano = int(opcao)


p='''
qtd_dias_arquivo = len(df)

total_esperado = 366 if calendar.isleap(ano) else 365

dias_faltantes = total_esperado - qtd_dias_arquivo
if dias_faltantes < 0:
    dias_faltantes = 0
'''
qtd_dias_arquivo = 0
dias_faltantes = 0
total_esperado = 0
col_graph_line = st.columns(1)
col5, col6, col7 = st.columns(3)
col1, col2 = st.columns(2)

with col5:
    st.write("Dias disponíveis: :green", qtd_dias_arquivo)
with col6:
    st.write("Dias ausentes:", dias_faltantes)
with col7:
    st.write("Total esperado:", total_esperado)

# ----------------- GRÁFICOS -----------------
with col_graph_line[0]:
    st.subheader(f"Média diária do TRWET - {ano if len(ano) == 1 else 'Todos os anos'}")
    fig_dia = px.line(df, x="data_completa", y="TROTOT")
    fig_dia.update_traces(
        mode="lines+markers",
        line=dict(width=2),
        marker=dict(size=4),
    )
    st.plotly_chart(fig_dia, use_container_width=True)



with col1:
    t='''
    st.subheader(f"Média diária do TRWET - {ano}")
    fig_dia = px.line(df, x="data_completa", y="TROTOT")
    fig_dia.update_traces(
        mode="lines+markers",
        line=dict(width=2),
        marker=dict(size=4),
    )
    st.plotly_chart(fig_dia, use_container_width=True)
    '''

with col2:
    st.subheader(f"Média mensal do TRWET - {ano if len(ano) == 1 else 'Todos os anos'}")
    
    r = '''
    #df_mensal["data_mes"] = pd.to_datetime(
    #    {"year": df["nm_ano"], "month": df["mes"], "day": 1}
    #)3'''
    fig_mes = px.bar(df_mensal, x="mes", y="TROTOT")
    st.plotly_chart(fig_mes, use_container_width=True)

st.subheader("Dados filtrados")
st.dataframe(df.head(500))
