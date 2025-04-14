import streamlit as st
import pandas as pd
import altair as alt
import requests
from urllib.parse import urlparse

st.set_page_config(page_title="Análise SARESP", layout="wide")
st.title("📊 Análise de Correlação - SARESP, Simulado e Raça")

# Função melhorada para transformar link do Google Sheets
def transformar_url_google_sheets(link):
    try:
        parsed = urlparse(link)
        if "docs.google.com" not in parsed.netloc:
            raise ValueError("Não é um link do Google Sheets")
            
        path_parts = parsed.path.split('/')
        if len(path_parts) < 4 or path_parts[3] != 'd':
            raise ValueError("Formato de link inválido")
            
        file_id = path_parts[4]
        return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid=0"
    except Exception as e:
        st.error(f"❌ Erro ao processar o link: {e}")
        return None

# Função melhorada para carregar dados
@st.cache_data(ttl=3600)  # Cache por 1 hora
def carregar_dados(url):
    if not url:
        return pd.DataFrame()
        
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(pd.compat.StringIO(response.content.decode('utf-8')))
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição: {e}")
    except pd.errors.EmptyDataError:
        st.error("O arquivo CSV está vazio")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
    return pd.DataFrame()

# URLs - considere mover para secrets ou config
urls = {
    "simulado": "https://docs.google.com/spreadsheets/d/1WdYDSdSnoZYGrqOZQ6et0ATZ6I_cn68sy40TDvU-7us/edit",
    "raca_jundiai": "https://docs.google.com/spreadsheets/d/1ukOdMgipTZKbeutiX2dypD_CU1y0PZMzqg6nBIYM--k/edit",
    "raca_sul1": "https://docs.google.com/spreadsheets/d/1r4Dnkqnw6eSYFzTbgM5gCPdDfMP3iglQn1Atkd_9V1c/edit",
    "saresp_jundiai": "https://docs.google.com/spreadsheets/d/1rVWqlFSdWczK0SYZ4ecSdloJJ4BNllgy7m0K5q9G31Q/edit",
    "saresp_sul1": "https://docs.google.com/spreadsheets/d/1mMU5WVwGLQhSf_AwKBXJVaSyMOsqplZqaUeBLAQf-iM/edit"
}

# Transformar URLs
transformed_urls = {k: transformar_url_google_sheets(v) for k, v in urls.items()}

# Barra de progresso
with st.spinner('Carregando dados...'):
    # Carregar dados
    data = {
        "simulado": carregar_dados(transformed_urls["simulado"]),
        "raca_jundiai": carregar_dados(transformed_urls["raca_jundiai"]),
        "raca_sul1": carregar_dados(transformed_urls["raca_sul1"]),
        "saresp_jundiai": carregar_dados(transformed_urls["saresp_jundiai"]),
        "saresp_sul1": carregar_dados(transformed_urls["saresp_sul1"])
    }

# Verificar se os dados foram carregados
if any(df.empty for df in data.values()):
    st.error("Alguns dados não foram carregados corretamente. Verifique os links.")
    st.stop()

# Padronizando colunas - versão mais robusta
def padronizar_colunas(df):
    if df.empty:
        return df
        
    # Converter para maiúsculas e remover espaços
    df.columns = df.columns.str.upper().str.strip()
    
    # Mapeamento de colunas alternativas
    column_mapping = {
        'ESCOLAS': 'ESCOLA',
        'NOME DA ESCOLA': 'ESCOLA',
        'D.E.': 'DE',
        'DIRETORIA DE ENSINO': 'DE'
    }
    
    df.rename(columns=column_mapping, inplace=True)
    return df

# Aplicar padronização
for key in data:
    data[key] = padronizar_colunas(data[key])

# Concatenar dados
try:
    raca = pd.concat([data["raca_jundiai"], data["raca_sul1"]], ignore_index=True)
    saresp = pd.concat([data["saresp_jundiai"], data["saresp_sul1"]], ignore_index=True)
except Exception as e:
    st.error(f"Erro ao concatenar dados: {e}")
    st.stop()

# Verificar colunas necessárias
required_columns = {'ESCOLA', 'DE'}
for df_name, df in [('Simulado', data["simulado"]), ('Raça', raca), ('SARESP', saresp)]:
    missing = required_columns - set(df.columns)
    if missing:
        st.error(f"❌ Colunas faltando na base {df_name}: {', '.join(missing)}")
        st.stop()

# Realizar merge
try:
    base = pd.merge(
        data["simulado"], 
        saresp, 
        on=["ESCOLA", "DE"], 
        how="inner",
        suffixes=('_SIM', '_SARESP')
    )
    base = pd.merge(
        base, 
        raca, 
        on=["ESCOLA", "DE"], 
        how="left"  # Usar left join para preservar todas as escolas do simulado
    )
except Exception as e:
    st.error(f"Erro ao unir os dados: {e}")
    st.stop()

# Identificar colunas de notas
nota_columns = {
    'simulado': [col for col in base.columns if 'SIM' in col],
    'saresp': [col for col in base.columns if 'SARESP' in col]
}

if not nota_columns['simulado'] or not nota_columns['saresp']:
    st.error("Não foi possível identificar colunas de notas (SIM/SARESP)")
    st.stop()

# Selecionar a primeira coluna de cada tipo (você pode modificar isso)
col_simulado = nota_columns['simulado'][0]
col_saresp = nota_columns['saresp'][0]

# Visualização
st.subheader("Dados Combinados")
st.dataframe(base.head())

# Gráficos
st.subheader("Análise de Correlação")

# Gráfico de dispersão
if 'RAÇA' in base.columns:
    chart = alt.Chart(base).mark_circle(size=80).encode(
        x=alt.X(f"{col_saresp}:Q", title="Nota SARESP", scale=alt.Scale(zero=False)),
        y=alt.Y(f"{col_simulado}:Q", title="Nota Simulado", scale=alt.Scale(zero=False)),
        color=alt.Color("RAÇA:N", legend=alt.Legend(title="Raça")),
        tooltip=["ESCOLA", "DE", "RAÇA", col_simulado, col_saresp]
    ).properties(
        width=800,
        height=500
    ).interactive()
    
    st.altair_chart(chart)
    
    # Estatísticas adicionais
    st.write("### Correlação por Raça")
    correlacao = base.groupby("RAÇA")[[col_simulado, col_saresp]].corr().iloc[0::2,1]
    st.write(correlacao)
else:
    st.warning("Coluna 'RAÇA' não encontrada. Mostrando gráfico sem distinção por raça.")
    chart = alt.Chart(base).mark_circle(size=80).encode(
        x=alt.X(f"{col_saresp}:Q", title="Nota SARESP"),
        y=alt.Y(f"{col_simulado}:Q", title="Nota Simulado"),
        tooltip=["ESCOLA", "DE", col_simulado, col_saresp]
    ).properties(
        width=800,
        height=500
    ).interactive()
    st.altair_chart(chart)

# Mostrar correlação geral
corr_geral = base[[col_simulado, col_saresp]].corr().iloc[0,1]
st.metric("Correlação Geral", value=f"{corr_geral:.2f}")
