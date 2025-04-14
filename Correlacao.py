import streamlit as st
import pandas as pd
import altair as alt
from scipy.stats import linregress
import numpy as np
import requests
import os

st.set_page_config(page_title="Dashboard SARESP", page_icon=":bar_chart:", layout="wide")
st.title("Dashboard de Análise do SARESP")

def transformar_url_google_drive(link):
    file_id = link.split('/d/')[1].split('/')[0]
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# Novos links (exemplo — substitua se necessário)
url_simulado = transformar_url_google_drive("https://docs.google.com/spreadsheets/d/1WdYDSdSnoZYGrqOZQ6et0ATZ6I_cn68sy40TDvU-7us/edit?usp=sharing")
url_raca_jundiai = transformar_url_google_drive("https://docs.google.com/spreadsheets/d/1ukOdMgipTZKbeutiX2dypD_CU1y0PZMzqg6nBIYM--k/edit?usp=sharing")
url_raca_sul1 = transformar_url_google_drive("https://docs.google.com/spreadsheets/d/1r4Dnkqnw6eSYFzTbgM5gCPdDfMP3iglQn1Atkd_9V1c/edit?usp=sharing")
url_saresp_jundiai = transformar_url_google_drive("https://docs.google.com/spreadsheets/d/1rVWqlFSdWczK0SYZ4ecSdloJJ4BNllgy7m0K5q9G31Q/edit?usp=sharing")
url_saresp_sul1 = transformar_url_google_drive("https://docs.google.com/spreadsheets/d/1mMU5WVwGLQhSf_AwKBXJVaSyMOsqplZqaUeBLAQf-iM/edit?usp=sharing")

def carregar_dados(url):
    file_name = "dados_temp.csv"
    response = requests.get(url)
    with open(file_name, 'wb') as f:
        f.write(response.content)
    return pd.read_csv(file_name)

# Carrega e padroniza os dados
def padronizar_colunas(df, nome_escola_original, nome_de_original):
    df = df.rename(columns={nome_escola_original: 'Escola', nome_de_original: 'DE'})
    return df

# Carregar bases
simulado_df = carregar_dados(url_simulado)
simulado_df = padronizar_colunas(simulado_df, 'Escolas', 'DE')

raca_jundiai_df = carregar_dados(url_raca_jundiai)
raca_jundiai_df = padronizar_colunas(raca_jundiai_df, 'Escola', 'DE')

raca_sul1_df = carregar_dados(url_raca_sul1)
raca_sul1_df = padronizar_colunas(raca_sul1_df, 'Escola', 'DE')

saresp_jundiai_df = carregar_dados(url_saresp_jundiai)
saresp_jundiai_df = padronizar_colunas(saresp_jundiai_df, 'ESCOLA', 'DE')

saresp_sul1_df = carregar_dados(url_saresp_sul1)
saresp_sul1_df = padronizar_colunas(saresp_sul1_df, 'ESCOLA', 'DE')

# Concatenar e filtrar SARESP por 9º ano
saresp_df = pd.concat([saresp_jundiai_df, saresp_sul1_df], ignore_index=True)

# Ajuste conforme o nome real da coluna com o ano
if 'Ano' in saresp_df.columns:
    saresp_df = saresp_df[saresp_df['Ano'].astype(str).str.contains("9", case=False, na=False)]
else:
    st.error("A coluna 'Ano' não foi encontrada na base do SARESP. Verifique o nome exato.")

# Combinar base de raça
raca_df = pd.concat([raca_jundiai_df, raca_sul1_df], ignore_index=True)

# Juntar SARESP e Raça por Escola e DE
saresp_raca_df = pd.merge(saresp_df, raca_df, on=['Escola', 'DE'], how='inner')

# Verificação e visualizações
if 'Raça' in saresp_raca_df.columns and 'SARESP' in saresp_raca_df.columns:
    media_por_raca = saresp_raca_df.groupby('Raça')['SARESP'].mean().reset_index()

    st.altair_chart(
        alt.Chart(media_por_raca).mark_bar().encode(
            x='Raça:N',
            y='SARESP:Q',
            tooltip=['Raça', 'SARESP']
        ).properties(title="Média do SARESP por Raça"),
        use_container_width=True
    )
else:
    st.warning("Colunas 'Raça' ou 'SARESP' não encontradas após merge.")

# Juntar SARESP e Simulado para regressão
df_comparado = pd.merge(saresp_df, simulado_df, on=['Escola', 'DE'], how='inner')

if 'Simulado' in df_comparado.columns and 'SARESP' in df_comparado.columns:
    x = df_comparado['Simulado']
    y = df_comparado['SARESP']
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    r_squared = r_value ** 2

    regression_line = pd.DataFrame({
        'Simulado': np.linspace(x.min(), x.max(), 100)
    })
    regression_line['SARESP_Pred'] = slope * regression_line['Simulado'] + intercept

    scatter = alt.Chart(df_comparado).mark_circle(size=60).encode(
        x='Simulado',
        y='SARESP',
        tooltip=['Simulado', 'SARESP']
    )

    line = alt.Chart(regression_line).mark_line(color='red').encode(
        x='Simulado',
        y='SARESP_Pred'
    )

    st.altair_chart((scatter + line).interactive().properties(title="Regressão Simulado x SARESP"), use_container_width=True)
    st.write(f"R² = {r_squared:.2f} | Equação: SARESP = {slope:.2f} * Simulado + {intercept:.2f}")
else:
    st.warning("Colunas 'Simulado' ou 'SARESP' não encontradas após o merge.")

