import streamlit as st
import pandas as pd
import altair as alt
from scipy.stats import linregress
import numpy as np

st.set_page_config(page_title="DashBoard SARESP", 
                   page_icon=":bar_chart:",
                   layout="wide"
                   )

st.title("Dashboard de Análise do SARESP")

# Carregar os dados diretamente do arquivo
@st.cache_data
def carregar_dados():
    return pd.read_csv("dados_saresp.csv")  # <-- troque esse nome conforme necessário

saresp_df = carregar_dados()

# Sidebar para navegação
st.sidebar.title("Navegação")
page = st.sidebar.selectbox("Escolha a página", ["Análise Geral", "Comparativo Simulado x SARESP"])

if page == "Análise Geral":
    st.header("Análise Geral por Raça")

    if 'Race' in saresp_df.columns and 'SARESP' in saresp_df.columns:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Média das Notas por Raça")
            media_por_raca = saresp_df.groupby('Race')['SARESP'].mean().reset_index()

            bar_chart_race = alt.Chart(media_por_raca).mark_bar().encode(
                x=alt.X('Race:N', title='Raça'),
                y=alt.Y('SARESP:Q', title='Nota Média SARESP'),
                tooltip=['Race', 'SARESP']
            ).properties(title="Notas Médias por Raça")

            st.altair_chart(bar_chart_race, use_container_width=True)

        with col2:
            st.subheader("Distribuição de Notas por Raça")
            boxplot_race = alt.Chart(saresp_df).mark_boxplot().encode(
                x='Race:N',
                y='SARESP:Q',
                color='Race:N'
            ).properties(title="Boxplot das Notas por Raça")

            st.altair_chart(boxplot_race, use_container_width=True)

        st.markdown("""
        **Interpretação:**
        Os gráficos acima mostram como as médias e a distribuição das notas do SARESP variam entre os diferentes grupos raciais. O gráfico de barras mostra a média das notas, enquanto o boxplot permite identificar dispersão, mediana e possíveis outliers.
        """)
    else:
        st.warning("As colunas 'Race' e 'SARESP' precisam estar presentes no dataset.")

elif page == "Comparativo Simulado x SARESP":
    st.title("Comparativo entre Nota do Simulado e Nota do SARESP")

    if 'Simulado' in saresp_df.columns and 'SARESP' in saresp_df.columns:
        st.subheader("Dispersão entre Nota do Simulado e Nota do SARESP com Linha de Regressão")

        x = saresp_df['Simulado']
        y = saresp_df['SARESP']
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        r_squared = r_value ** 2

        regression_line = pd.DataFrame({
            'Simulado': np.linspace(x.min(), x.max(), 100)
        })
        regression_line['SARESP_Pred'] = slope * regression_line['Simulado'] + intercept

        scatter = alt.Chart(saresp_df).mark_circle(size=60).encode(
            x='Simulado',
            y='SARESP',
            tooltip=['Simulado', 'SARESP']
        )

        line = alt.Chart(regression_line).mark_line(color='red').encode(
            x='Simulado',
            y='SARESP_Pred'
        )

        st.altair_chart((scatter + line).interactive(), use_container_width=True)

        st.markdown(f"""
        **Coeficiente de Correlação (r):** {r_value:.2f}  
        **Coeficiente de Determinação (R²):** {r_squared:.2f}  
        **Equação da Regressão:** SARESP = {slope:.2f} * Simulado + {intercept:.2f}
        """)

        st.info("**Interpretação:**\n"
                f"O valor de R² indica que aproximadamente **{r_squared*100:.1f}%** da variação nas notas do SARESP "
                "pode ser explicada pelas notas do Simulado por meio de uma regressão linear simples.")

        st.subheader("Distribuição das Notas")
        col1, col2 = st.columns(2)

        with col1:
            hist_simulado = alt.Chart(saresp_df).mark_bar().encode(
                alt.X("Simulado", bin=True),
                y='count()'
            ).properties(title="Distribuição - Simulado")
            st.altair_chart(hist_simulado, use_container_width=True)

        with col2:
            hist_saresp = alt.Chart(saresp_df).mark_bar().encode(
                alt.X("SARESP", bin=True),
                y='count()'
            ).properties(title="Distribuição - SARESP")
            st.altair_chart(hist_saresp, use_container_width=True)

    else:
        st.warning("As colunas 'Simulado' e 'SARESP' não foram encontradas nos dados.")
