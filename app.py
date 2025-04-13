import streamlit as st
import pandas as pd
import altair as alt
import time  
from scipy.stats import linregress
import numpy as np

st.set_page_config(page_title="DashBoard Performance estudantes", 
                   page_icon=":bar_chart:",
                   layout="wide"
                   )

st.title("Dashboard de Desempenho dos Estudantes")

# Carregar os arquivos CSV
uploaded_file1 = st.file_uploader("Carregar o primeiro dataset (student_performance.csv)", type="csv")
uploaded_file2 = st.file_uploader("Carregar o segundo dataset (StudentPerformanceFactors.csv)", type="csv")

# Verificar se os arquivos foram carregados
if uploaded_file1 is not None and uploaded_file2 is not None:
    with st.spinner("Carregando dados..."):  # Exibir a barra de progresso
        try:
            time.sleep(1)  
            student_performance_df = pd.read_csv(uploaded_file1)
            performance_factors_df = pd.read_csv(uploaded_file2)
            st.success("Arquivos carregados com sucesso!")

            # Mesclar os datasets com base em colunas comuns
            merged_df = pd.merge(student_performance_df, performance_factors_df, on='Gender', how='inner')

        except Exception as e:
            st.error(f"Erro ao processar os arquivos: {e}")

else:
    st.warning("Por favor, carregue ambos os datasets para continuar.")

# Sidebar para navegação
st.sidebar.title("Navegação")
page = st.sidebar.selectbox("Escolha a página", ["Análise Geral", "Fatores Influenciadores", "Comparativo Simulado x SARESP"])

# Filtro dinâmico
if 'merged_df' in locals():
    final_grade_filter = st.sidebar.slider("Selecione o intervalo de notas finais", 
                                           min_value=int(merged_df['FinalGrade'].min()), 
                                           max_value=int(merged_df['FinalGrade'].max()), 
                                           value=(int(merged_df['FinalGrade'].min()), int(merged_df['FinalGrade'].max())))

    filtered_df = merged_df[(merged_df['FinalGrade'] >= final_grade_filter[0]) & 
                            (merged_df['FinalGrade'] <= final_grade_filter[1])]

    if page == "Análise Geral":
        media_notas = filtered_df['FinalGrade'].mean()

        st.markdown(
            f"<h2 style='color: #4CAF50; font-size: 40px;'>Média das Notas Finais: <span style='color: #0000FF;'>{media_notas:.2f}</span></h2>",
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Horas de Estudo por Semana vs Notas Finais")
            scatter_chart = alt.Chart(filtered_df).mark_circle(size=60).encode(
                x='StudyHoursPerWeek',
                y='FinalGrade',
                tooltip=['Name', 'StudyHoursPerWeek', 'FinalGrade']
            ).interactive()
            st.altair_chart(scatter_chart, use_container_width=True)

        with col2:
            st.subheader("Distribuição da Qualidade do Ensino")
            teacher_quality_counts = filtered_df['Teacher_Quality'].value_counts().reset_index()
            teacher_quality_counts.columns = ['Teacher_Quality', 'Count']

            teacher_quality_pie_chart = alt.Chart(teacher_quality_counts).mark_arc().encode(
                theta='Count:Q',
                color='Teacher_Quality:N',
                tooltip=['Teacher_Quality', 'Count']
            ).properties(title='Qualidade do Ensino')

            st.altair_chart(teacher_quality_pie_chart, use_container_width=True)

        filtered_df = filtered_df.drop_duplicates(subset=['Name', 'FinalGrade'])

        st.subheader("Top 5 Alunos com as Maiores Notas Finais")
        top5_students = filtered_df.nlargest(5, 'FinalGrade')[['Name', 'FinalGrade', 'StudyHoursPerWeek', 'ExtracurricularActivities']]
        st.table(top5_students)

    elif page == "Fatores Influenciadores":
        st.title("Análise dos Fatores Influenciadores")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Média das Notas Finais por Participação em Atividades Extracurriculares")
            bar_chart = alt.Chart(filtered_df).mark_bar().encode(
                x='ExtracurricularActivities',
                y='mean(FinalGrade)',
                color='ExtracurricularActivities',
                tooltip=['ExtracurricularActivities', 'mean(FinalGrade)']
            ).interactive()
            st.altair_chart(bar_chart, use_container_width=True)

        with col2:
            st.subheader("Média das Notas Finais por Gênero")
            gender_performance = filtered_df.groupby('Gender')['FinalGrade'].mean().reset_index()
            bar_chart_gender = alt.Chart(gender_performance).mark_bar().encode(
                x='Gender',
                y='FinalGrade',
                tooltip=['Gender', 'FinalGrade']
            ).interactive()
            st.altair_chart(bar_chart_gender, use_container_width=True)

    elif page == "Comparativo Simulado x SARESP":
        st.title("Comparativo entre Nota do Simulado e Nota do SARESP")

        if 'Simulado' in merged_df.columns and 'SARESP' in merged_df.columns:
            st.subheader("Dispersão entre Nota do Simulado e Nota do SARESP com Linha de Regressão")

            x = merged_df['Simulado']
            y = merged_df['SARESP']
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            r_squared = r_value ** 2

            regression_line = pd.DataFrame({
                'Simulado': np.linspace(x.min(), x.max(), 100)
            })
            regression_line['SARESP_Pred'] = slope * regression_line['Simulado'] + intercept

            scatter = alt.Chart(merged_df).mark_circle(size=60).encode(
                x='Simulado',
                y='SARESP',
                tooltip=['Name', 'Simulado', 'SARESP']
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
                hist_simulado = alt.Chart(merged_df).mark_bar().encode(
                    alt.X("Simulado", bin=True),
                    y='count()'
                ).properties(title="Distribuição - Simulado")
                st.altair_chart(hist_simulado, use_container_width=True)

            with col2:
                hist_saresp = alt.Chart(merged_df).mark_bar().encode(
                    alt.X("SARESP", bin=True),
                    y='count()'
                ).properties(title="Distribuição - SARESP")
                st.altair_chart(hist_saresp, use_container_width=True)

        else:
            st.warning("As colunas 'Simulado' e 'SARESP' não foram encontradas nos dados.")
