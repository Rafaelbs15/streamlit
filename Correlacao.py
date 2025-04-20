import streamlit as st
import pandas as pd
import altair as alt
import requests
from urllib.parse import urlparse

st.set_page_config(page_title="Análise SARESP", layout="wide")
st.title("📊 Análise de Correlação - SARESP, Simulado e Raça")

# Configuração das URLs das planilhas (substitua com seus links reais)
SHEET_URLS = {
    "simulado": "https://docs.google.com/spreadsheets/d/1WdYDSdSnoZYGrqOZQ6et0ATZ6I_cn68sy40TDvU-7us/edit",
    "raca_jundiai": "https://docs.google.com/spreadsheets/d/1ukOdMgipTZKbeutiX2dypD_CU1y0PZMzqg6nBIYM--k/edit",
    "raca_sul1": "https://docs.google.com/spreadsheets/d/1r4Dnkqnw6eSYFzTbgM5gCPdDfMP3iglQn1Atkd_9V1c/edit",
    "saresp_jundiai": "https://docs.google.com/spreadsheets/d/1rVWqlFSdWczK0SYZ4ecSdloJJ4BNllgy7m0K5q9G31Q/edit",
    "saresp_sul1": "https://docs.google.com/spreadsheets/d/1mMU5WVwGLQhSf_AwKBXJVaSyMOsqplZqaUeBLAQf-iM/edit",
    "simulado_sul1": "https://docs.google.com/spreadsheets/d/1iuHE5IHQUVaIuo2Z5x5wqJGT2VRJostnVrH40mvHfL4/edit?usp=drive_link",
    "simulado_sul2": "https://docs.google.com/spreadsheets/d/1A0L4YwrVFt77Up049RSdZ9Toe9FD-oXkjERkdppFy0g/edit?usp=drive_link"
}

def carregar_sheet(id_planilha):
    url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
    return pd.read_csv(url_csv)

# ID da planilha do simulado (sem /edit no final!)
simulado_id_9anoJundiai = "1WdYDSdSnoZYGrqOZQ6et0ATZ6I_cn68sy40TDvU-7us"
raca_jundiai = "1ukOdMgipTZKbeutiX2dypD_CU1y0PZMzqg6nBIYM--k"
raca_sul1 = "1r4Dnkqnw6eSYFzTbgM5gCPdDfMP3iglQn1Atkd_9V1c"
saresp_jundiai = "1rVWqlFSdWczK0SYZ4ecSdloJJ4BNllgy7m0K5q9G31Q"
saresp_sul1 = "1mMU5WVwGLQhSf_AwKBXJVaSyMOsqplZqaUeBLAQf-iM"
simulado_id_5anoSul1 ="1iuHE5IHQUVaIuo2Z5x5wqJGT2VRJostnVrH40mvHfL4"
simulado_id_5anoSul2 = "1A0L4YwrVFt77Up049RSdZ9Toe9FD-oXkjERkdppFy0g"


# Carrega
df_simulado = carregar_sheet(simulado_id_9anoJundiai)
df_raca_jundiai = carregar_sheet(raca_jundiai)
df_raca_sul1 = carregar_sheet(raca_sul1)
df_saresp_jundiai = carregar_sheet(saresp_jundiai)
df_saresp_sul1 = carregar_sheet(saresp_sul1)
df_simulado_5anoSul1 = carregar_sheet(simulado_id_5anoSul1)
df_simulado_5anoSul2 = carregar_sheet(simulado_id_5anoSul2)

if st.checkbox("Mostrar amostras dos dados"):
    st.write(df_simulado_5anoSul1.head())
    st.write(df_saresp_sul1.head())
    st.write(df_raca_jundiai.head())
    st.write(df_saresp_jundiai.head())

def carregar_sheet(id_planilha):
    url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
    return pd.read_csv(url_csv)

# ID da planilha do simulado (sem /edit no final!)
simulado_id_9anoJundiai = "1WdYDSdSnoZYGrqOZQ6et0ATZ6I_cn68sy40TDvU-7us"
raca_jundiai = "1ukOdMgipTZKbeutiX2dypD_CU1y0PZMzqg6nBIYM--k"
raca_sul1 = "1r4Dnkqnw6eSYFzTbgM5gCPdDfMP3iglQn1Atkd_9V1c"
saresp_jundiai = "1rVWqlFSdWczK0SYZ4ecSdloJJ4BNllgy7m0K5q9G31Q"
saresp_sul1 = "1mMU5WVwGLQhSf_AwKBXJVaSyMOsqplZqaUeBLAQf-iM"
simulado_id_5anoSul1 ="1iuHE5IHQUVaIuo2Z5x5wqJGT2VRJostnVrH40mvHfL4"
simulado_id_5anoSul2 = "1A0L4YwrVFt77Up049RSdZ9Toe9FD-oXkjERkdppFy0g"


# Carrega
df_simulado = carregar_sheet(simulado_id_9anoJundiai)
df_raca_jundiai = carregar_sheet(raca_jundiai)
df_raca_sul1 = carregar_sheet(raca_sul1)
df_saresp_jundiai = carregar_sheet(saresp_jundiai)
df_saresp_sul1 = carregar_sheet(saresp_sul1)
df_simulado_5anoSul1 = carregar_sheet(simulado_id_5anoSul1)
df_simulado_5anoSul2 = carregar_sheet(simulado_id_5anoSul2)


# Filtrar apenas respostas corretas
df_simulado_filtrado = df_simulado[df_simulado['Resposta'] == 'Correto']

# Contagem total de questões por escola e disciplina
total_questoes = df_simulado.groupby(['DE', 'SERIE_ANO', 'ESCOLA', 'Disciplina'])['Resposta'].count().reset_index(name='Total_Respostas')

# Contagem de acertos
acertos = df_simulado_filtrado.groupby(['DE', 'SERIE_ANO', 'ESCOLA', 'Disciplina'])['Resposta'].count().reset_index(name='Acertos')

# Merge e cálculo da porcentagem
df_simulado_percentual = pd.merge(acertos, total_questoes, on=['DE', 'SERIE_ANO', 'ESCOLA', 'Disciplina'])
df_simulado_percentual['% Acerto'] = (df_simulado_percentual['Acertos'] / df_simulado_percentual['Total_Respostas']) * 100

df_saresp_jundiai_9ano = df_saresp_jundiai[df_saresp_jundiai['SERIE_ANO'] == '9 Ano']
df_saresp_sul1_9ano = df_saresp_sul1[df_saresp_sul1['SERIE_ANO'] == '9 Ano']

# Preparar o simulado com pivot (LP e MAT em colunas)
df_simulado_pivot = df_simulado_percentual.pivot(index=['DE', 'ESCOLA', 'SERIE_ANO'], columns='Disciplina', values='% Acerto').reset_index()
df_simulado_pivot.columns.name = None  # remover nome do índice

# Renomear colunas pra bater com os nomes do SARESP
df_simulado_pivot.rename(columns={'LP': 'Simulado_LP', 'MAT': 'Simulado_MAT'}, inplace=True)

# Juntar com o SARESP (exemplo com Jundiaí)
df_merge = pd.merge(
    df_saresp_jundiai_9ano,
    df_simulado_pivot[df_simulado_pivot['DE'] == 'JUNDIAI'],
    left_on='ESCOLA',
    right_on='ESCOLA',
    how='inner'
)

import altair as alt

# Histograma de % de acerto - LP
lp_hist = alt.Chart(df_simulado_percentual[df_simulado_percentual['Disciplina'] == 'LP']).mark_bar().encode(
    alt.X('% Acerto', bin=alt.Bin(maxbins=20)),
    y='count()',
    tooltip=['% Acerto']
).properties(
    title='Distribuição de % de acertos - LP (Simulado)'
)

# Histograma de % de acerto - MAT
mat_hist = alt.Chart(df_simulado_percentual[df_simulado_percentual['Disciplina'] == 'MAT']).mark_bar().encode(
    alt.X('% Acerto', bin=alt.Bin(maxbins=20)),
    y='count()',
    tooltip=['% Acerto']
).properties(
    title='Distribuição de % de acertos - MAT (Simulado)'
)

st.altair_chart(lp_hist, use_container_width=True)
st.altair_chart(mat_hist, use_container_width=True)

import altair as alt

correlacao_lp = alt.Chart(df_merge).mark_circle(size=60).encode(
    x='LP',
    y='Simulado_LP',
    tooltip=['ESCOLA', 'LP', 'Simulado_LP']
).properties(
    title='Correlação LP - SARESP vs Simulado (Jundiaí)'
)

st.altair_chart(correlacao_lp, use_container_width=True)

# Histograma - SARESP LP
hist_lp_saresp = alt.Chart(df_saresp_jundiai_9ano).mark_bar().encode(
    alt.X('LP', bin=alt.Bin(maxbins=20)),
    y='count()',
    tooltip=['LP']
).properties(
    title='Distribuição das médias em LP - SARESP (Jundiaí)'
)

# Histograma - SARESP MAT
hist_mat_saresp = alt.Chart(df_saresp_jundiai_9ano).mark_bar().encode(
    alt.X('MAT', bin=alt.Bin(maxbins=20)),
    y='count()',
    tooltip=['MAT']
).properties(
    title='Distribuição das médias em MAT - SARESP (Jundiaí)'
)

st.altair_chart(hist_lp_saresp, use_container_width=True)
st.altair_chart(hist_mat_saresp, use_container_width=True)

# Média geral por DE e Disciplina
media_por_de = df_simulado_percentual.groupby(['DE', 'Disciplina'])['% Acerto'].mean().reset_index()

chart = alt.Chart(media_por_de).mark_bar().encode(
    x='DE:N',
    y='% Acerto:Q',
    color='Disciplina:N',
    tooltip=['DE', 'Disciplina', '% Acerto']
).properties(
    title='Média de % de acerto por DE e Disciplina (Simulado)'
)

st.altair_chart(chart, use_container_width=True)