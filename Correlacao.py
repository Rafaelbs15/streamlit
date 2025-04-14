import streamlit as st
import pandas as pd
import altair as alt
import requests
from io import StringIO

st.set_page_config(page_title="Análise SARESP", layout="wide")
st.title("📊 Análise de Correlação - SARESP, Simulado e Raça")

# Função para transformar o link do Google Sheets em link de exportação CSV
def transformar_url_google_sheets(link):
    if "/d/" in link:
        file_id = link.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
    else:
        st.error("❌ Link inválido do Google Sheets.")
        return ""

# Função para carregar dados do Google Sheets (diretamente do conteúdo retornado)
def carregar_dados(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_string = response.content.decode('utf-8')
        return pd.read_csv(StringIO(csv_string))
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

# Links dos Google Sheets (atualize conforme os seus)
url_simulado = transformar_url_google_sheets("https://docs.google.com/spreadsheets/d/1WdYDSdSnoZYGrqOZQ6et0ATZ6I_cn68sy40TDvU-7us/edit?usp=sharing")
url_raca_jundiai = transformar_url_google_sheets("https://docs.google.com/spreadsheets/d/1ukOdMgipTZKbeutiX2dypD_CU1y0PZMzqg6nBIYM--k/edit?usp=drive_link")
url_raca_sul1 = transformar_url_google_sheets("https://docs.google.com/spreadsheets/d/1r4Dnkqnw6eSYFzTbgM5gCPdDfMP3iglQn1Atkd_9V1c/edit?usp=drive_link")
url_saresp_jundiai = transformar_url_google_sheets("https://docs.google.com/spreadsheets/d/1rVWqlFSdWczK0SYZ4ecSdloJJ4BNllgy7m0K5q9G31Q/edit?usp=drive_link")
url_saresp_sul1 = transformar_url_google_sheets("https://docs.google.com/spreadsheets/d/1mMU5WVwGLQhSf_AwKBXJVaSyMOsqplZqaUeBLAQf-iM/edit?usp=drive_link")

# Carregando os dados diretamente dos Google Sheets
simulado = carregar_dados(url_simulado)
raca_jundiai = carregar_dados(url_raca_jundiai)
raca_sul1 = carregar_dados(url_raca_sul1)
saresp_jundiai = carregar_dados(url_saresp_jundiai)
saresp_sul1 = carregar_dados(url_saresp_sul1)

# Função para padronizar os nomes de colunas: tudo maiúsculo, e renomeia variações para 'ESCOLA'
def padronizar_colunas(df):
    df.columns = [col.strip().upper() for col in df.columns]
    # Se o nome da coluna for 'ESCOLAS' ou 'Escola', converte para 'ESCOLA'
    df.rename(columns={'ESCOLAS': 'ESCOLA', 'ESCOLA ': 'ESCOLA'}, inplace=True)
    return df

simulado = padronizar_colunas(simulado)
raca_jundiai = padronizar_colunas(raca_jundiai)
raca_sul1 = padronizar_colunas(raca_sul1)
saresp_jundiai = padronizar_colunas(saresp_jundiai)
saresp_sul1 = padronizar_colunas(saresp_sul1)

# Concatenando as bases de RAÇA e SARESP
raca = pd.concat([raca_jundiai, raca_sul1], ignore_index=True)
saresp = pd.concat([saresp_jundiai, saresp_sul1], ignore_index=True)

# Verifica se as colunas "ESCOLA" e "DE" existem em todas as bases
for nome, df in [('Simulado', simulado), ('Raça', raca), ('SARESP', saresp)]:
    if not {'ESCOLA', 'DE'}.issubset(df.columns):
        st.error(f"❌ As colunas 'ESCOLA' e 'DE' não estão na base {nome}.")
        st.stop()

# Merge entre as bases
# Primeiro, une Simulado e SARESP (com sufixos para diferenciar as colunas numéricas)
base = pd.merge(simulado, saresp, on=["ESCOLA", "DE"], suffixes=('_SIM', '_SARESP'))
# Em seguida, une com a base de Raça (que deve ter coluna RAÇA)
base = pd.merge(base, raca, on=["ESCOLA", "DE"])

# Seleciona as colunas referentes às notas do Simulado e SARESP
# Aqui, pressupomos que as colunas que contém 'SIM' e 'SARESP' são de interesse
col_simulado = [col for col in base.columns if 'SIM' in col.upper()]
col_saresp = [col for col in base.columns if 'SARESP' in col.upper()]

if col_simulado and col_saresp:
    col_simulado = col_simulado[0]
    col_saresp = col_saresp[0]
else:
    st.error("❌ Não foram encontradas colunas para Simulado ou SARESP após o merge.")
    st.stop()

# Gráfico de dispersão por RAÇA, se existir a coluna "RAÇA"
if 'RAÇA' in base.columns:
    chart = alt.Chart(base).mark_circle(size=80).encode(
        x=alt.X(f"{col_saresp}:Q", title="Nota SARESP"),
        y=alt.Y(f"{col_simulado}:Q", title="Nota Simulado"),
        color=alt.Color("RAÇA:N"),
        tooltip=["ESCOLA", "DE", "RAÇA", col_simulado, col_saresp]
    ).properties(
        title="Correlação entre Simulado e SARESP por RAÇA",
        width=800,
        height=500
    ).interactive()
    
    st.altair_chart(chart)
else:
    st.warning("Coluna 'RAÇA' não encontrada na base combinada.")

