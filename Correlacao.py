import streamlit as st
import pandas as pd
import altair as alt
from scipy.stats import linregress
import numpy as np
import requests
import os

# Configuração da página do Streamlit
st.set_page_config(page_title="Dashboard SARESP", page_icon=":bar_chart:", layout="wide")
st.title("Dashboard de Análise do SARESP")

# Função para transformar o link do Google Drive para o formato correto de download
def transformar_url_google_drive(link):
    file_id = link.split('/d/')[1].split('/')[0]
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# URLs corrigidas
url_simulado = transformar_url_google_drive("https://drive.google.com/file/d/1EMEZAK_VRjUpqWFx00MlSiC3_3_rWUpA/view?usp=drive_link")
url_raca_jundiai = transformar_url_google_drive("https://drive.google.com/file/d/1eNdo3xHRjUJ6i5EOHdARqQM2NIuusode/view?usp=drive_link")
url_raca_sul1 = transformar_url_google_drive("https://drive.google.com/file/d/1iez8-jFuHRcuPEU0XdYGT3AGTu-kDl_6/view?usp=drive_link")
url_saresp_sul1 = transformar_url_google_drive("https://drive.google.com/file/d/1xuMPPGO2bOo443GQbsoVuJEolojULRvk/view?usp=drive_link")
url_saresp_jundiai = transformar_url_google_drive("https://drive.google.com/file/d/1EViJbfPdR51-SgbWvVKfUIQ1m9ltfYkf/view?usp=drive_link")

# Função para baixar e carregar os dados diretamente no pandas
def carregar_dados(url):
    # Baixar o arquivo
    file_name = "dados_temp.csv"  # Nome temporário para salvar o arquivo
    response = requests.get(url)
    
    # Verificar se o download foi bem-sucedido
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
    else:
        st.error(f"Falha ao baixar o arquivo, código de status: {response.status_code}")
        return None

    # Ler o arquivo CSV, tentando com diferentes configurações
    try:
        return pd.read_csv(file_name, encoding='utf-8')  # Tente com UTF-8
    except pd.errors.ParserError:
        try:
            return pd.read_csv(file_name, encoding='latin1')  # Tente com Latin-1
        except pd.errors.ParserError as e:
            st.error(f"Erro ao ler o CSV: {e}")
            return None

# Carregar os dados
simulado_df = carregar_dados(url_simulado)
raca_jundiai_df = carregar_dados(url_raca_jundiai)
raca_sul1_df = carregar_dados(url_raca_sul1)
saresp_sul1_df = carregar_dados(url_saresp_sul1)
saresp_jundiai_df = carregar_dados(url_saresp_jundiai)

# Verificar se os dados foram carregados com sucesso
if simulado_df is None or raca_jundiai_df is None or raca_sul1_df is None or saresp_sul1_df is None or saresp_jundiai_df is None:
    st.stop()  # Se algum arquivo não foi carregado, interrompe a execução

# Unir os dados de SARESP e Raça
saresp_df = pd.concat([saresp_sul1_df, saresp_jundiai_df], ignore_index=True)
raca_df = pd.concat([raca_jundiai_df, raca_sul1_df], ignore_index=True)

# Padronizando os nomes das colunas para "Escola" e "DE" em ambas as bases
raca_df = raca_df.rename(columns={'Escola': 'Escola'})  # Padronizar o nome da coluna 'Escola'
# Adicionar DE no raca_df (se não estiver lá), caso contrário, deve ser renomeado também
if 'DE' not in raca_df.columns:
    st.error("A coluna 'DE' não foi encontrada na base de Raça.")
    st.stop()

# Verificar as colunas presentes nas bases
st.write("Colunas do DataFrame SARESP:")
st.write(saresp_df.columns)

st.write("Colunas do DataFrame Raça:")
st.write(raca_df.columns)

# Certificar que temos 'Escola' e 'DE' nas duas bases
if 'Escola' in saresp_df.columns and 'DE' in saresp_df.columns and 'Escola' in raca_df.columns and 'DE' in raca_df.columns:
    # Calcular a média do SARESP por Escola e DE
    saresp_media_df = saresp_df.groupby(['Escola', 'DE'])['SARESP'].mean().reset_index()
    
    # Unir as bases de SARESP e Raça usando 'Escola' e 'DE' como chave
    merged_df = pd.merge(saresp_media_df, raca_df, on=['Escola', 'DE'], how='inner')

    # Mapeamento das categorias de Raça para valores numéricos
    merged_df['Raça_num'] = merged_df['Raça'].map({'Branca': 1, 'Preta': 2, 'Parda': 3})

    # Verificar as primeiras linhas do DataFrame combinado
    st.write("Primeiras linhas do DataFrame combinado:")
    st.write(merged_df.head())

    # Calcular correlação entre a média do SARESP e a Raça
    correlation = merged_df['SARESP'].corr(merged_df['Raça_num'])

    st.write(f"A correlação entre a média do SARESP e a Raça é: {correlation:.2f}")

    # Plotar um gráfico de dispersão com a linha de regressão
    scatter = alt.Chart(merged_df).mark_circle(size=60).encode(
        x='Raça_num:N',  # A coluna de Raça numérica
        y='SARESP:Q',
        tooltip=['Escola', 'DE', 'Raça', 'SARESP']
    )

    # Linha de regressão
    slope, intercept, r_value, p_value, std_err = linregress(merged_df['Raça_num'], merged_df['SARESP'])
    regression_line = pd.DataFrame({
        'Raça_num': np.linspace(merged_df['Raça_num'].min(), merged_df['Raça_num'].max(), 100)
    })
    regression_line['SARESP_Pred'] = slope * regression_line['Raça_num'] + intercept

    line = alt.Chart(regression_line).mark_line(color='red').encode(
        x='Raça_num',
        y='SARESP_Pred'
    )

    (scatter + line).interactive().properties(title="Regressão entre Raça e Média do SARESP").display()

else:
    st.write("As colunas 'Escola' e 'DE' não foram encontradas nas bases.")

