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
    "saresp_sul1": "https://docs.google.com/spreadsheets/d/1mMU5WVwGLQhSf_AwKBXJVaSyMOsqplZqaUeBLAQf-iM/edit"
}

# Função para transformar link do Google Sheets em link de exportação CSV
def transformar_url_google_sheets(link):
    try:
        if "/d/" in link:
            file_id = link.split("/d/")[1].split("/")[0]
            return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
        else:
            st.error("❌ Link inválido do Google Sheets.")
            return None
    except Exception as e:
        st.error(f"Erro ao processar URL: {e}")
        return None

# Função para carregar dados do Google Sheets com cache
@st.cache_data(ttl=3600)  # Cache por 1 hora
def carregar_dados(url, nome_planilha):
    if not url:
        st.error(f"URL não fornecida para {nome_planilha}")
        return pd.DataFrame()
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(pd.compat.StringIO(response.content.decode('utf-8')))
        st.success(f"✅ {nome_planilha} carregada com {len(df)} registros")
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar {nome_planilha}: {e}")
        return pd.DataFrame()

# Transformar URLs
urls_transformadas = {
    nome: transformar_url_google_sheets(url) 
    for nome, url in SHEET_URLS.items()
}

# Carregar todos os dados
with st.spinner('Carregando dados das planilhas...'):
    dados = {
        "simulado": carregar_dados(urls_transformadas["simulado"], "Simulado 9º ano"),
        "raca_jundiai": carregar_dados(urls_transformadas["raca_jundiai"], "Raça Jundiaí"),
        "raca_sul1": carregar_dados(urls_transformadas["raca_sul1"], "Raça Sul 1"),
        "saresp_jundiai": carregar_dados(urls_transformadas["saresp_jundiai"], "SARESP Jundiaí"),
        "saresp_sul1": carregar_dados(urls_transformadas["saresp_sul1"], "SARESP Sul 1")
    }

# Verificar se todos os dados foram carregados
if any(df.empty for df in dados.values()):
    st.error("Algumas planilhas não foram carregadas corretamente. Verifique os logs acima.")
    st.stop()

# Função para padronizar colunas
def padronizar_colunas(df, nome_df):
    if df.empty:
        return df
        
    # Converter para maiúsculas e remover espaços
    df.columns = df.columns.str.upper().str.strip()
    
    # Mapeamento de colunas alternativas
    column_mapping = {
        'ESCOLAS': 'ESCOLA',
        'NOME DA ESCOLA': 'ESCOLA',
        'D.E.': 'DE',
        'DIRETORIA DE ENSINO': 'DE',
        'CÓDIGO DA ESCOLA': 'COD_ESCOLA'
    }
    
    df.rename(columns=column_mapping, inplace=True)
    
    # Verificar colunas essenciais
    colunas_necessarias = {'ESCOLA', 'DE'}
    colunas_faltando = colunas_necessarias - set(df.columns)
    
    if colunas_faltando:
        st.warning(f"Aviso: {nome_df} está faltando colunas: {', '.join(colunas_faltando)}")
    
    return df

# Aplicar padronização
dados_padronizados = {
    nome: padronizar_colunas(df, nome) 
    for nome, df in dados.items()
}

# Concatenar dados de mesma categoria
try:
    raca_total = pd.concat([dados_padronizados["raca_jundiai"], dados_padronizados["raca_sul1"]], ignore_index=True)
    saresp_total = pd.concat([dados_padronizados["saresp_jundiai"], dados_padronizados["saresp_sul1"]], ignore_index=True)
except Exception as e:
    st.error(f"Erro ao concatenar dados: {e}")
    st.stop()

# Verificar colunas necessárias para merge
colunas_merge = ['ESCOLA', 'DE']
for df_nome, df in [('Simulado', dados_padronizados["simulado"]), 
                    ('Raça', raca_total), 
                    ('SARESP', saresp_total)]:
    if not all(col in df.columns for col in colunas_merge):
        st.error(f"❌ {df_nome} não tem todas as colunas necessárias para o merge: {colunas_merge}")
        st.stop()

# Realizar o merge dos dados
try:
    base_completa = pd.merge(
        dados_padronizados["simulado"],
        saresp_total,
        on=colunas_merge,
        how='inner',
        suffixes=('_SIM', '_SARESP')
    )
    
    base_completa = pd.merge(
        base_completa,
        raca_total,
        on=colunas_merge,
        how='left'
    )
    
    st.success("✅ Bases unidas com sucesso!")
except Exception as e:
    st.error(f"Erro ao unir as bases: {e}")
    st.stop()

# Mostrar dados brutos
if st.checkbox("Mostrar dados brutos"):
    st.subheader("Dados Completos")
    st.dataframe(base_completa)

# Análise de Correlação
st.header("📈 Análise de Correlação")

# Encontrar colunas de notas
colunas_notas_sim = [col for col in base_completa.columns if 'SIM' in col]
colunas_notas_saresp = [col for col in base_completa.columns if 'SARESP' in col]

if not colunas_notas_sim or not colunas_notas_saresp:
    st.error("Não foram encontradas colunas de notas (com sufixo SIM ou SARESP)")
    st.stop()

col_simulado = st.selectbox("Selecione a coluna do Simulado", colunas_notas_sim)
col_saresp = st.selectbox("Selecione a coluna do SARESP", colunas_notas_saresp)

# Gráfico de dispersão
if 'RAÇA' in base_completa.columns:
    st.subheader("Correlação por Raça")
    
    chart = alt.Chart(base_completa).mark_circle(size=60).encode(
        x=alt.X(col_saresp, title="Nota SARESP", scale=alt.Scale(zero=False)),
        y=alt.X(col_simulado, title="Nota Simulado", scale=alt.Scale(zero=False)),
        color=alt.Color('RAÇA', legend=alt.Legend(title="Raça")),
        tooltip=['ESCOLA', 'DE', 'RAÇA', col_simulado, col_saresp]
    ).properties(
        width=800,
        height=500,
        title=f"Correlação: {col_simulado} vs {col_saresp}"
    ).interactive()
    
    st.altair_chart(chart)
    
    # Cálculo de correlação por raça
    st.subheader("Estatísticas por Raça")
    correlacao_raca = base_completa.groupby('RAÇA')[[col_simulado, col_saresp]].corr().iloc[0::2,1]
    st.write(correlacao_raca)
else:
    st.warning("Coluna 'RAÇA' não encontrada. Mostrando análise sem distinção por raça.")
    
    chart = alt.Chart(base_completa).mark_circle(size=60).encode(
        x=alt.X(col_saresp, title="Nota SARESP"),
        y=alt.X(col_simulado, title="Nota Simulado"),
        tooltip=['ESCOLA', 'DE', col_simulado, col_saresp]
    ).properties(
        width=800,
        height=500
    ).interactive()
    
    st.altair_chart(chart)

# Correlação geral
correlacao_geral = base_completa[[col_simulado, col_saresp]].corr().iloc[0,1]
st.metric("Correlação Geral", value=f"{correlacao_geral:.2f}")

# Mostrar dados faltantes
st.subheader("Verificação de Dados")
st.write("Registros com valores faltantes:")
st.write(base_completa.isnull().sum())
