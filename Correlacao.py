import streamlit as st
import pandas as pd
import altair as alt
import requests

st.set_page_config(page_title="Análise SARESP", layout="wide")
st.title("📊 Análise de Correlação - SARESP, Simulado e Raça")

# Função para transformar link do Google Sheets em link de exportação CSV
def transformar_url_google_sheets(link):
    if "/d/" in link:
        file_id = link.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
    else:
        st.error("❌ Link inválido do Google Sheets.")
        return ""

# Função para carregar dados do Google Sheets
def carregar_dados(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(pd.compat.StringIO(response.content.decode('utf-8')))
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

# Coloque os links aqui:
url_simulado = transformar_url_google_sheets("https://docs.google.com/spreadsheets/d/1EMEZAK_VRjUpqWFx00MlSiC3_3_rWUpA/view?usp=drive_link")
url_raca_jundiai = transformar_url_google_sheets("https://docs.google.com/spreadsheets/d/1eNdo3xHRjUJ6i5EOHdARqQM2NIuusode/view?usp=drive_link")
url_raca_sul1 = transformar_url_google_sheets("https://docs.google.com/spreadsheets/d/1iez8-jFuHRcuPEU0XdYGT3AGTu-kDl_6/view?usp=drive_link")
url_saresp_jundiai = transformar_url_google_sheets("https://docs.google.com/spreadsheets/d/1EViJbfPdR51-SgbWvVKfUIQ1m9ltfYkf/view?usp=drive_link")
url_saresp_sul1 = transformar_url_google_sheets("https://docs.google.com/spreadsheets/d/1xuMPPGO2bOo443GQbsoVuJEolojULRvk/view?usp=drive_link")

# Carregando os dados
simulado = carregar_dados(url_simulado)
raca_jundiai = carregar_dados(url_raca_jundiai)
raca_sul1 = carregar_dados(url_raca_sul1)
saresp_jundiai = carregar_dados(url_saresp_jundiai)
saresp_sul1 = carregar_dados(url_saresp_sul1)

# Padronizando nomes de colunas
def padronizar_colunas(df):
    df.columns = [col.strip().upper() for col in df.columns]
    df.rename(columns={'ESCOLAS': 'ESCOLA', 'Escola': 'ESCOLA'}, inplace=True)
    return df

simulado = padronizar_colunas(simulado)
raca_jundiai = padronizar_colunas(raca_jundiai)
raca_sul1 = padronizar_colunas(raca_sul1)
saresp_jundiai = padronizar_colunas(saresp_jundiai)
saresp_sul1 = padronizar_colunas(saresp_sul1)

# Concatenando
raca = pd.concat([raca_jundiai, raca_sul1], ignore_index=True)
saresp = pd.concat([saresp_jundiai, saresp_sul1], ignore_index=True)

# Verifica se colunas necessárias existem
for df_nome, df in [('Simulado', simulado), ('Raça', raca), ('SARESP', saresp)]:
    if not {'ESCOLA', 'DE'}.issubset(df.columns):
        st.error(f"❌ As colunas 'ESCOLA' e 'DE' não estão na base {df_nome}")
        st.stop()

# Merge entre bases
base = pd.merge(simulado, saresp, on=["ESCOLA", "DE"], suffixes=('_SIM', '_SARESP'))
base = pd.merge(base, raca, on=["ESCOLA", "DE"])

# Seleção de colunas para análise
col_simulado = [col for col in base.columns if 'SIM' in col][0]
col_saresp = [col for col in base.columns if 'SARESP' in col][0]

# Gráfico de dispersão por raça
if 'RAÇA' in base.columns:
    chart = alt.Chart(base).mark_circle(size=80).encode(
        x=alt.X(f"{col_saresp}:Q", title="Nota SARESP"),
        y=alt.Y(f"{col_simulado}:Q", title="Nota Simulado"),
        color=alt.Color("RAÇA:N"),
        tooltip=["ESCOLA", "DE", "RAÇA", col_simulado, col_saresp]
    ).properties(
        title="Correlação entre Simulado e SARESP por Raça",
        width=800,
        height=500
    ).interactive()
    
    st.altair_chart(chart)
else:
    st.warning("Coluna 'RAÇA' não encontrada na base combinada.")
