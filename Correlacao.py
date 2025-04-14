import streamlit as st
import pandas as pd
import altair as alt
from scipy.stats import linregress
import numpy as np
import requests

st.set_page_config(page_title="Dashboard SARESP", page_icon=":bar_chart:", layout="wide")
st.title("Dashboard de Análise do SARESP")

# Função para transformar URL do Google Drive
def transformar_url_google_drive(link):
    file_id = link.split('/d/')[1].split('/')[0]
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# Links
url_simulado = transformar_url_google_drive("https://drive.google.com/file/d/1EMEZAK_VRjUpqWFx00MlSiC3_3_rWUpA/view?usp=drive_link")
url_raca_jundiai = transformar_url_google_drive("https://drive.google.com/file/d/1eNdo3xHRjUJ6i5EOHdARqQM2NIuusode/view?usp=drive_link")
url_raca_sul1 = transformar_url_google_drive("https://drive.google.com/file/d/1iez8-jFuHRcuPEU0XdYGT3AGTu-kDl_6/view?usp=drive_link")
url_saresp_sul1 = transformar_url_google_drive("https://drive.google.com/file/d/1xuMPPGO2bOo443GQbsoVuJEolojULRvk/view?usp=drive_link")
url_saresp_jundiai = transformar_url_google_drive("https://drive.google.com/file/d/1EViJbfPdR51-SgbWvVKfUIQ1m9ltfYkf/view?usp=drive_link")

# Função para baixar e carregar CSV
def carregar_dados(url):
    r = requests.get(url)
    with open("temp.csv", "wb") as f:
        f.write(r.content)
    return pd.read_csv("temp.csv")

# Carrega bases
simulado_df = carregar_dados(url_simulado)
raca_df = pd.concat([carregar_dados(url_raca_jundiai), carregar_dados(url_raca_sul1)], ignore_index=True)
saresp_df = pd.concat([carregar_dados(url_saresp_sul1), carregar_dados(url_saresp_jundiai)], ignore_index=True)

# Padroniza nomes de colunas
# SARESP
saresp_df.rename(columns={
    'ESCOLA': 'Escola',
    'DE': 'DE',
    'MEDIA': 'SARESP'  # ou ajuste conforme o nome da nota média
}, inplace=True)

# Raça
raca_df.rename(columns={
    'Escola': 'Escola',
    'DE': 'DE',
    'Raça': 'Raca'
}, inplace=True)

# Junta Raça + SARESP
raca_saresp_df = pd.merge(raca_df, saresp_df, on=['Escola', 'DE'], how='inner')

# Calcula média por raça
if 'Raca' in raca_saresp_df.columns and 'SARESP' in raca_saresp_df.columns:
    media_por_raca = raca_saresp_df.groupby('Raca')['SARESP'].mean().reset_index()

    # Gráfico de barras
    st.altair_chart(
        alt.Chart(media_por_raca).mark_bar().encode(
            x='Raca:N',
            y='SARESP:Q',
            tooltip=['Raca', 'SARESP']
        ).properties(title="Média do SARESP por Raça"),
        use_container_width=True
    )

    # Boxplot
    st.altair_chart(
        alt.Chart(raca_saresp_df).mark_boxplot().encode(
            x='Raca:N',
            y='SARESP:Q',
            color='Raca:N'
        ).properties(title="Distribuição das Notas por Raça"),
        use_container_width=True
    )
else:
    st.error("Colunas 'Raca' ou 'SARESP' não encontradas.")


