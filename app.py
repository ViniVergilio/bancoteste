import streamlit as st
import mysql.connector
import requests
import pandas as pd

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
    st.dataframe(df)

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

        


    st.subheader("📊 Indicadores Básicos - IBGE (API)")

    indicadores = [
        {
                "titulo": "População total (2021)",
                "url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021/variaveis/9324?localidades=N6[3523909]",
                "chave": "2021",
                "prefixo": "",
                "sufixo": " pessoas"
        },
        {
                "titulo": "Renda média domiciliar (2022)",
                "url": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/2022/variaveis/93?localidades=N6[3523909]",
                "chave": "2022",
                "prefixo": "R$ ",
                "sufixo": ""
        },
        {
                "titulo": "Escolarização 6 a 14 anos (%)",
                "url": "https://servicodados.ibge.gov.br/api/v3/agregados/6460/periodos/2022/variaveis/385?localidades=N6[3523909]",
                "chave": "2022",
                "prefixo": "",
                "sufixo": "%"
        },
        {
                "titulo": "Alfabetização 15+ anos (%)",
                "url": "https://servicodados.ibge.gov.br/api/v3/agregados/6460/periodos/2022/variaveis/384?localidades=N6[3523909]",
                "chave": "2022",
                "prefixo": "",
                "sufixo": "%"
        },
        {
                "titulo": "Domicílios com água encanada (2010)",
                "url": "https://servicodados.ibge.gov.br/api/v3/agregados/6083/periodos/2010/variaveis/83?localidades=N6[3523909]",
                "chave": "2010",
                "prefixo": "",
                "sufixo": "%"
        },
        {
                "titulo": "Domicílios permanentes (2010)",
                "url": "https://servicodados.ibge.gov.br/api/v3/agregados/6083/periodos/2010/variaveis/80?localidades=N6[3523909]",
                "chave": "2010",
                "prefixo": "",
                "sufixo": " domicílios"
        }
        ]

        # Exibir em linhas de 3 colunas
    for i in range(0, len(indicadores), 3):
            cols = st.columns(3)
            for j, item in enumerate(indicadores[i:i+3]):
                try:
                    resposta = requests.get(item["url"])
                    data = resposta.json()
                    valor = list(data[0]['resultados'][0]['series'][0]['serie'].values())[0]
                    cols[j].metric(label=item["titulo"], value=f"{item['prefixo']}{valor}{item['sufixo']}")
                except Exception as e:
                    cols[j].error(f"Erro em {item['titulo']}")



except Exception as e:
    st.error(f"Erro: {e}")
