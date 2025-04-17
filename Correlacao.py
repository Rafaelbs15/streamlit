import streamlit as st
import pandas as pd
import altair as alt
import requests
from urllib.parse import urlparse

st.set_page_config(page_title="Análise SARESP", layout="wide")
st.title("📊 Análise de Correlação SARESP, Simulado e Raça")

# Função para carregar Google Sheets como CSV
def carregar_sheet(id_planilha):
    url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
    return pd.read_csv(url_csv)

# IDs das planilhas
planilhas = {
    "simulado": "1WdYDSdSnoZYGrqOZQ6et0ATZ6I_cn68sy40TDvU-7us",
    "raca_jundiai": "1ukOdMgipTZKbeutiX2dypD_CU1y0PZMzqg6nBIYM--k",
    "raca_sul1": "1r4Dnkqnw6eSYFzTbgM5gCPdDfMP3iglQn1Atkd_9V1c",
    "saresp_jundiai": "1rVWqlFSdWczK0SYZ4ecSdloJJ4BNllgy7m0K5q9G31Q",
    "saresp_sul1": "1mMU5WVwGLQhSf_AwKBXJVaSyMOsqplZqaUeBLAQf-iM",
    "simulado_sul1": "1iuHE5IHQUVaIuo2Z5x5wqJGT2VRJostnVrH40mvHfL4",
    "simulado_sul2": "1A0L4YwrVFt77Up049RSdZ9Toe9FD-oXkjERkdppFy0g"
}

# Carregamento das bases
df_simulado = carregar_sheet(planilhas["simulado"])
df_raca_jundiai = carregar_sheet(planilhas["raca_jundiai"])
df_raca_sul1 = carregar_sheet(planilhas["raca_sul1"])
df_saresp_jundiai = carregar_sheet(planilhas["saresp_jundiai"])
df_saresp_sul1 = carregar_sheet(planilhas["saresp_sul1"])
df_simulado_5anoSul1 = carregar_sheet(planilhas["simulado_sul1"])
df_simulado_5anoSul2 = carregar_sheet(planilhas["simulado_sul2"])

# Checkbox para amostras
debug = st.checkbox("Mostrar amostras dos dados")
if debug:
    st.write(df_simulado.head())
    st.write(df_saresp_jundiai.head())
    st.write(df_saresp_sul1.head())

# Filtrar respostas corretas e calcular % acertos
df_simulado_filtrado = df_simulado[df_simulado['Resposta'] == 'Correto']
total_questoes = df_simulado.groupby(['DE', 'SERIE_ANO', 'ESCOLA', 'Disciplina'])['Resposta'].count().reset_index(name='Total_Respostas')
acertos = df_simulado_filtrado.groupby(['DE', 'SERIE_ANO', 'ESCOLA', 'Disciplina'])['Resposta'].count().reset_index(name='Acertos')
df_simulado_percentual = pd.merge(acertos, total_questoes, on=['DE', 'SERIE_ANO', 'ESCOLA', 'Disciplina'])
df_simulado_percentual['% Acerto'] = (df_simulado_percentual['Acertos'] / df_simulado_percentual['Total_Respostas']) * 100

# Pivot para comparar com SARESP
df_simulado_pivot = df_simulado_percentual.pivot(index=['DE', 'ESCOLA', 'SERIE_ANO'], columns='Disciplina', values='% Acerto').reset_index()
df_simulado_pivot.rename(columns={'LP': 'Simulado_LP', 'MAT': 'Simulado_MAT'}, inplace=True)

# Filtros de SARESP para 9º ano
df_saresp_jundiai_9ano = df_saresp_jundiai[df_saresp_jundiai['SERIE_ANO'] == '9 Ano']
df_saresp_sul1_9ano = df_saresp_sul1[df_saresp_sul1['SERIE_ANO'] == '9 Ano']

# Merge com simulado (Jundiaí)
df_merge = pd.merge(
    df_saresp_jundiai_9ano,
    df_simulado_pivot[df_simulado_pivot['DE'] == 'JUNDIAI'],
    on='ESCOLA', how='inner'
)

# Gráficos de distribuição LP/MAT
for disciplina in ['LP', 'MAT']:
    hist = alt.Chart(df_simulado_percentual[df_simulado_percentual['Disciplina'] == disciplina]).mark_bar().encode(
        alt.X('% Acerto', bin=alt.Bin(maxbins=20)),
        y='count()',
        tooltip=['% Acerto']
    ).properties(
        title=f'Distribuição de % de acertos - {disciplina} (Simulado)'
    )
    st.altair_chart(hist, use_container_width=True)

# Correlação LP
correlacao_lp = alt.Chart(df_merge).mark_circle(size=60).encode(
    x='LP',
    y='Simulado_LP',
    tooltip=['ESCOLA', 'LP', 'Simulado_LP']
).properties(
    title='Correlação LP - SARESP vs Simulado (Jundiaí)'
)
st.altair_chart(correlacao_lp, use_container_width=True)

# Histogramas do SARESP
for disciplina in ['LP', 'MAT']:
    hist = alt.Chart(df_saresp_jundiai_9ano).mark_bar().encode(
        alt.X(disciplina, bin=alt.Bin(maxbins=20)),
        y='count()',
        tooltip=[disciplina]
    ).properties(
        title=f'Distribuição das médias em {disciplina} - SARESP (Jundiaí)'
    )
    st.altair_chart(hist, use_container_width=True)

# Média por DE, Série e Disciplina
media_por_de_serie = df_simulado_percentual.groupby(['DE', 'SERIE_ANO', 'Disciplina'])['% Acerto'].mean().reset_index()

# Gráfico de barras com texto
chart = alt.Chart(media_por_de_serie).mark_bar().encode(
    x=alt.X('DE:N', title='Diretoria de Ensino'),
    y=alt.Y('% Acerto:Q', title='% de Acerto'),
    color='Disciplina:N',
    column=alt.Column('SERIE_ANO:N', title='Série'),
    tooltip=['DE', 'SERIE_ANO', 'Disciplina', '% Acerto']
).properties(
    title='Média de % de acerto por DE, Série e Disciplina (Simulado)'
).configure_axis(
    labelAngle=0
)

text = alt.Chart(media_por_de_serie).mark_text(
    align='center',
    baseline='bottom',
    dy=-2
).encode(
    x='DE:N',
    y='% Acerto:Q',
    detail='Disciplina:N',
    column='SERIE_ANO:N',
    text=alt.Text('% Acerto:Q', format='.1f')
)

st.altair_chart(chart + text, use_container_width=True)