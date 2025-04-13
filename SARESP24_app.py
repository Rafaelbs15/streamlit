# -*- coding: utf-8 -*-
"""SARESP24_app

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1cj8I-3WeVmA67HJOB_zUAE04_4-9SpGy
"""

import streamlit as st
import pandas as pd
import numpy as np
from pandas_profiling import ProfileReport
import streamlit.components.v1 as components
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Análise exploratória SARESP",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

@st.cache_data
def generate_profile_report(dataframe):
    return ProfileReport(dataframe, explorative=True)

def show_correlation_plot(df):
    st.header("Gráfico de Correlação")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    selected_cols = st.multiselect(
        "Selecione duas ou mais variáveis numéricas:",
        numeric_cols,
        default=numeric_cols[:2] if len(numeric_cols) >= 2 else None
    )
    if selected_cols and len(selected_cols) >= 2:
        corr = df[selected_cols].corr()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
        st.pyplot(fig)
    else:
        st.info("Selecione pelo menos duas variáveis numéricas.")

st.title("Análise exploratória e correlações - Simulado SARESP e SARESP 2024")

st.sidebar.header("Instruções")
st.sidebar.markdown("""
1. Faça upload de um arquivo `.csv`
2. Veja os dados
3. Gere relatório EDA
4. Veja correlação entre variáveis
""")

st.sidebar.header("Upload de Arquivo CSV")
uploaded_file = st.sidebar.file_uploader("Escolha o arquivo", type="csv")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.header("📊 Dados carregados")
    st.write(df)

    st.header("📋 Relatório de Análise Exploratória")
    profile_report = generate_profile_report(df)
    components.html(profile_report.to_html(), height=1000, scrolling=True)

    show_correlation_plot(df)

else:
    st.sidebar.info("Aguardando upload do arquivo.")
    if st.sidebar.button("Usar exemplo"):
        @st.cache_data
        def load_example_data():
            return pd.DataFrame(np.random.rand(100, 5), columns=['A', 'B', 'C', 'D', 'E'])

        df = load_example_data()
        st.header("📊 Exemplo de dados")
        st.write(df)

        st.header("📋 Relatório de Análise Exploratória")
        profile_report = generate_profile_report(df)
        components.html(profile_report.to_html(), height=1000, scrolling=True)

        show_correlation_plot(df)