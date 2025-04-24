import streamlit as st
import mysql.connector
import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

st.markdown("""
<style>
span[data-baseweb="tag"] {
    background-color: #60a5fa !important; /* Azul claro */ !important;
    color: white !important;
    border-radius: 0.5rem !important;
}
span[data-baseweb="tag"] svg {
    stroke: white !important;
}
</style>
""", unsafe_allow_html=True)




# Configurações da conexão
config = {
    'host': 'bancoteste.c3gegommuogv.sa-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': '1210Informa',
    'database': 'bancoteste'
}



st.title("📊 Indicadores de Educação - Itu")

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            ate_1_ano AS 'Até 1 ano',
            de_1_a_3_anos AS '1 a 3 anos',
            de_4_a_7_anos AS '4 a 7 anos',
            de_8_a_10_anos AS '8 a 10 anos',
            de_11_a_14_anos AS '11 a 14 anos',
            mais_de_15_anos AS '15 anos ou mais',
            alfabetizados AS 'Alfabetizados',
            nao_alfabetizados AS 'Não Alfabetizados'
        FROM dados_itu
    """)
    
    dados = cursor.fetchall()
    colunas = [i[0] for i in cursor.description]
    df = pd.DataFrame(dados, columns=colunas)

    st.subheader("📍 Dados de Itu")
        
    opcao = st.selectbox(
        "Como deseja visualizar os dados?",
        ["Tabela", "Gráfico de barras", "Gráfico de pizza"]
    )

    if opcao == "Tabela":
        st.dataframe(df)

    elif opcao == "Gráfico de barras":
        dados_grafico = df.T.reset_index()
        dados_grafico.columns = ['Categoria', 'Valor']
        fig, ax = plt.subplots()
        ax.bar(dados_grafico['Categoria'], dados_grafico['Valor'], color='skyblue')
        ax.set_ylabel('Quantidade')
        ax.set_xlabel('Categoria')
        ax.set_title('Distribuição por Escolaridade')
        plt.xticks(rotation=45)

        st.pyplot(fig)
        
    elif opcao == "Gráfico de pizza":
        dados_grafico = df.T.reset_index()
        dados_grafico.columns = ['Categoria', 'Valor']
        st.write("Distribuição por categoria")
        st.pyplot(
            pd.Series(dados_grafico['Valor'].values, index=dados_grafico['Categoria']).plot.pie(autopct='%1.1f%%', figsize=(6, 6)).figure
        )










    st.subheader("👥 População estimada - IBGE (API)")

    url = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021/variaveis/9324?localidades=N6[3523909]"

    try:
        res = requests.get(url)
        data = res.json()

        municipio = data[0]['resultados'][0]['series'][0]['localidade']['nome']
        valor = data[0]['resultados'][0]['series'][0]['serie']['2021']

        st.metric(label=f"População de {municipio} (2021)", value=f"{int(valor):,}".replace(",", "."))


    except Exception as e:
        st.error(f"Erro ao consultar a API do IBGE: {e}")













    st.subheader("📊 Indicadores educacionais (Banco de Dados)")

    try:
        cursor.execute("SELECT * FROM dados_itu LIMIT 1")
        linha = cursor.fetchone()

        indicadores = {
            "Até 1 ano": linha[3],
            "1 a 3 anos": linha[4],
            "4 a 7 anos": linha[5],
            "8 a 10 anos": linha[6],
            "11 a 14 anos": linha[7],
            "15 anos ou mais": linha[8],
            "Alfabetizados": linha[9],
            "Não alfabetizados": linha[10],
        }

        tipo_visu = st.selectbox("Como deseja visualizar os dados educacionais?", [
            "Blocos separados", "Gráfico de barras", "Gráfico de pizza"
        ])

        categorias_escolhidas = st.multiselect(
        "Quais indicadores deseja visualizar?",
        list(indicadores.keys()),
        default=list(indicadores.keys())
        )

        categorias = categorias_escolhidas
        valores = [indicadores[k] for k in categorias_escolhidas]


        if tipo_visu == "Blocos separados":
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            colunas = [col1, col2, col3, col4, col5, col6]
            for i, (titulo, valor) in enumerate(indicadores.items()):
                if titulo in categorias:  # só mostra os selecionados
                    colunas[i % 6].metric(label=titulo, value=f"{valor:,}".replace(",", "."))


        elif tipo_visu == "Gráfico de barras":
            import matplotlib.pyplot as plt
            largura = st.slider("Largura do gráfico", 6, 16, 10)
            altura = st.slider("Altura do gráfico", 4, 10, 6)
            cor = st.color_picker("Escolha a cor das barras", "#60a5fa")

            col1, col2 = st.columns(2)

            with col1:
                largura = st.slider("Largura do gráfico", 6, 16, 10)

            with col2:
                altura = st.slider("Altura do gráfico", 4, 10, 6)

            cor = st.color_picker("Escolha a cor das barras", "#60a5fa")

            fig, ax = plt.subplots(figsize=(largura, altura))
            ax.bar(categorias, valores, color=cor)
            ax.set_title("Distribuição por categoria", fontsize=14)
            ax.set_ylabel("Quantidade", fontsize=12)
            plt.xticks(rotation=30, fontsize=10)
            plt.yticks(fontsize=10)

            st.pyplot(fig)



        elif tipo_visu == "Gráfico de pizza":
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            categorias = list(indicadores.keys())
            valores = list(indicadores.values())
            ax.pie(valores, labels=categorias, autopct='%1.1f%%', startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Erro ao exibir indicadores: {e}")










        
except Exception as e:
    st.error(f"Erro: {e}")
