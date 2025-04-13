import streamlit as st
import pandas as pd
import altair as alt
import time  

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
            # Simulando tempo de carregamento
            time.sleep(1)  
            
            # Ler os datasets carregados
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
page = st.sidebar.selectbox("Escolha a página", [ "Análise Geral", "Fatores Influenciadores"])

# Filtro dinâmico
if 'merged_df' in locals():
    final_grade_filter = st.sidebar.slider("Selecione o intervalo de notas finais", 
                                           min_value=int(merged_df['FinalGrade'].min()), 
                                           max_value=int(merged_df['FinalGrade'].max()), 
                                           value=(int(merged_df['FinalGrade'].min()), int(merged_df['FinalGrade'].max())))

    # Filtrar os dados
    filtered_df = merged_df[(merged_df['FinalGrade'] >= final_grade_filter[0]) & 
                            (merged_df['FinalGrade'] <= final_grade_filter[1])]

    # Página 1: Análise Geral
    if page == "Análise Geral":
         # Valor total: média das notas finais com duas casas decimais
        media_notas = filtered_df['FinalGrade'].mean()
        
        # Estilizando a média das notas finais
        st.markdown(
            f"<h2 style='color: #4CAF50; font-size: 40px;'>Média das Notas Finais: <span style='color: #0000FF;'>{media_notas:.2f}</span></h2>",
            unsafe_allow_html=True
        )

        # Organizar gráficos em colunas
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
            # Gráfico de pizza para Distribuição da Qualidade do Ensino
            st.subheader("Distribuição da Qualidade do Ensino")
            teacher_quality_counts = filtered_df['Teacher_Quality'].value_counts().reset_index()
            teacher_quality_counts.columns = ['Teacher_Quality', 'Count']  # Renomear as colunas

            # Criar gráfico de pizza
            teacher_quality_pie_chart = alt.Chart(teacher_quality_counts).mark_arc().encode(
                theta='Count:Q',           # Usar a contagem como valor
                color='Teacher_Quality:N', # Usar a qualidade do ensino como cor
                tooltip=['Teacher_Quality', 'Count']  # Tooltip para mostrar informações adicionais
            ).properties(title='Qualidade do Ensino')

            st.altair_chart(teacher_quality_pie_chart, use_container_width=True)

            # Remover duplicatas com base no nome e na nota final para evitar repetição de alunos
            filtered_df = filtered_df.drop_duplicates(subset=['Name', 'FinalGrade'])

    # Top 5 alunos com as maiores notas finais
        st.subheader("Top 5 Alunos com as Maiores Notas Finais")
        top5_students = filtered_df.nlargest(5, 'FinalGrade')[['Name', 'FinalGrade', 'StudyHoursPerWeek', 'ExtracurricularActivities']]

# Exibir a tabela
        st.table(top5_students)


    # Página 2: Fatores Influenciadores
    elif page == "Fatores Influenciadores":
        st.title("Análise dos Fatores Influenciadores")

        # Organizar gráficos em colunas
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

    
