import streamlit as st
import pandas as pd
import altair as alt
from scipy.stats import linregress
import numpy as np
import gdown

st.set_page_config(page_title="Dashboard SARESP",
                   page_icon=":bar_chart:",
                   layout="wide")

st.title("Dashboard de Análise do SARESP")

# -----------------------
# DEFINIR A FUNÇÃO AQUI 👇
# -----------------------
def transformar_url_google_drive(link):
    file_id = link.split('/d/')[1].split('/')[0]
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# -----------------------
# AGORA SIM USAR A FUNÇÃO 👇
# -----------------------
url_simulado = transformar_url_google_drive("https://drive.google.com/file/d/1EMEZAK_VRjUpqWFx00MlSiC3_3_rWUpA/view?usp=drive_link")
url_raca_jundiai = transformar_url_google_drive("https://drive.google.com/file/d/1eNdo3xHRjUJ6i5EOHdARqQM2NIuusode/view?usp=drive_link")
url_raca_sul1 = transformar_url_google_drive("https://drive.google.com/file/d/1iez8-jFuHRcuPEU0XdYGT3AGTu-kDl_6/view?usp=drive_link")
url_saresp_sul1 = transformar_url_google_drive("https://drive.google.com/file/d/1xuMPPGO2bOo443GQbsoVuJEolojULRvk/view?usp=drive_link")
url_saresp_jundiai = transformar_url_google_drive("https://drive.google.com/file/d/1EViJbfPdR51-SgbWvVKfUIQ1m9ltfYkf/view?usp=drive_link")

# -----------------------
# Função para baixar e carregar dados do Google Drive
# -----------------------
def carregar_dados(url):
    file_name = url.split("=")[-1]  # nome do arquivo a ser salvo
    gdown.download(url, file_name, quiet=False)
    
    # Verificar se é CSV ou Excel
    if file_name.endswith('.csv'):
        return pd.read_csv(file_name)
    else:
        return pd.read_excel(file_name)

# -----------------------
# Carregar os dados
# -----------------------
simulado_df = carregar_dados(url_simulado)
raca_jundiai_df = carregar_dados(url_raca_jundiai)
raca_sul1_df = carregar_dados(url_raca_sul1)
saresp_sul1_df = carregar_dados(url_saresp_sul1)
saresp_jundiai_df = carregar_dados(url_saresp_jundiai)

# Exemplo: combinar SARESP de Sul1 e Jundiaí
saresp_df = pd.concat([saresp_sul1_df, saresp_jundiai_df], ignore_index=True)

# Também pode juntar raças ou simulado com SARESP depois

# Verificar se colunas existem
if 'Race' in saresp_df.columns and 'SARESP' in saresp_df.columns:
    media_por_raca = saresp_df.groupby('Race')['SARESP'].mean().reset_index()

    # Gráfico de barras
    alt.Chart(media_por_raca).mark_bar().encode(
        x='Race:N',
        y='SARESP:Q',
        tooltip=['Race', 'SARESP']
    ).properties(title="Média do SARESP por Raça").display()

    # Boxplot
    alt.Chart(saresp_df).mark_boxplot().encode(
        x='Race:N',
        y='SARESP:Q',
        color='Race:N'
    ).properties(title="Distribuição das Notas por Raça").display()
else:
    print("Colunas 'Race' ou 'SARESP' não encontradas.")

# Juntar simulado com saresp se necessário
# Exemplo: assumindo que possuem coluna em comum tipo 'Escola'
# df_comparado = pd.merge(simulado_df, saresp_df, on='Escola')

# Caso já esteja combinado:
df_comparado = simulado_df.copy()  # ajustar conforme sua base

if 'Simulado' in df_comparado.columns and 'SARESP' in df_comparado.columns:
    # Regressão linear
    x = df_comparado['Simulado']
    y = df_comparado['SARESP']
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    r_squared = r_value ** 2

    regression_line = pd.DataFrame({
        'Simulado': np.linspace(x.min(), x.max(), 100)
    })
    regression_line['SARESP_Pred'] = slope * regression_line['Simulado'] + intercept

    # Scatter + linha
    scatter = alt.Chart(df_comparado).mark_circle(size=60).encode(
        x='Simulado',
        y='SARESP',
        tooltip=['Simulado', 'SARESP']
    )

    line = alt.Chart(regression_line).mark_line(color='red').encode(
        x='Simulado',
        y='SARESP_Pred'
    )

    (scatter + line).interactive().properties(title="Regressão Simulado x SARESP").display()

    print(f"R² = {r_squared:.2f} | Equação: SARESP = {slope:.2f} * Simulado + {intercept:.2f}")
else:
    print("Colunas 'Simulado' ou 'SARESP' não encontradas.")
