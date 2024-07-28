#from turtle import width
from calendar import c
import streamlit as st
import pandas as pd
import os
from openpyxl import load_workbook
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import poisson
import requests
from io import StringIO

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("chave_api.json", scope)
client = gspread.authorize(creds)

st.set_page_config(
    page_title="Copa PB",
    layout="centered"
)

@st.cache_data(ttl=20)
def load_data(sheets_url):
    # Formatando a URL para exportação como CSV
    csv_url = sheets_url.split("/edit")[0] + "/export?format=csv&" + sheets_url.split("?")[1]
    return pd.read_csv(csv_url)

# Carregar os dados usando a URL do secrets.toml
confrontos = load_data(st.secrets["confrontos"])

@st.cache_data(ttl=20)
def load_data1(sheets_url):
    # Formatando a URL para exportação como CSV
    csv_url = sheets_url.split("/edit")[0] + "/export?format=csv&" + sheets_url.split("?")[1]
    return pd.read_csv(csv_url)

resultados = load_data1(st.secrets["resultados"])



st.title('Copa Planeta dos Boleiros')

tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8, =  st.tabs(['Grupo A','Grupo B','Grupo C','Grupo D','Grupo E','Grupo F','Grupo G','Grupo H'])


#filtrar dataframe para não pegar colunas onde as rodadas não sejam preenchidas
resultados_filtrados = resultados.dropna(axis=1, how='any')
rodadas_validas = resultados_filtrados.columns[2:]
confrontos_filtrados = confrontos[confrontos['Rodada'].isin(rodadas_validas)]



def atualizar_tabela(tabela, resultados, confrontos):
    for _, row in confrontos.iterrows():
        rodada = row['Rodada']
        time_casa = row['Time A'].strip()
        time_visitante = row['Time B'].strip()
        
        pontos_casa = resultados_filtrados.loc[resultados_filtrados['Time'].str.strip() == time_casa, rodada].values[0]
        pontos_visitante = resultados_filtrados.loc[resultados_filtrados['Time'].str.strip() == time_visitante, rodada].values[0]
        
        # Inicializar pontos e saldo de gols se não estiverem na tabela
        if time_casa not in tabela.index:
            tabela.loc[time_casa] = [0, 0]
        if time_visitante not in tabela.index:
            tabela.loc[time_visitante] = [0, 0]
        
        # Atualizar pontos
        if pontos_casa > pontos_visitante:
            tabela.at[time_casa, 'Pontos'] += 3  # Vitória
        elif pontos_casa < pontos_visitante:
            tabela.at[time_visitante, 'Pontos'] += 3  # Vitória
        else:
            tabela.at[time_casa, 'Pontos'] += 1  # Empate
            tabela.at[time_visitante, 'Pontos'] += 1  # Empate
        
        # Atualizar saldo de pontos
        tabela.at[time_casa, 'Saldo'] += (pontos_casa - pontos_visitante)
        tabela.at[time_visitante, 'Saldo'] += (pontos_visitante - pontos_casa)


with tab1:
    resultados_a = resultados[resultados['Grupo'] == "A"]
    confrontos_a = confrontos[confrontos['Grupo'] ==  "A"]
    resultados_filtrados_a = resultados_filtrados[resultados_filtrados['Grupo'] ==  "A"]
    confrontos_filtrados_a = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "A"]
    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_a = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_a, resultados_filtrados, confrontos_filtrados)

    # Ordenar a tabela por pontos e saldo de pontos
    tabela_a = tabela_a.sort_values(by=['Pontos', 'Saldo'], ascending=False)
    tabela_a
    
    st.markdown('## **Confrontos**')

    # Obter rodadas únicas
    rodadas = confrontos_a['Rodada'].unique()
    resultados_a = resultados_a.replace({None: ''})
    for rodada in rodadas:
        st.markdown("---") 
        st.subheader(f'**{rodada}**')

        
         # Linha de separação
        jogos = confrontos_a[confrontos_a['Rodada'] == rodada]
        for _, jogo in jogos.iterrows():
            time_casa = jogo['Time A'].strip()
            time_visitante = jogo['Time B'].strip()
            
          
            
            # Obter os resultados_a dos times para a rodada
            pontos_casa = resultados_a.loc[resultados_a['Time'].str.strip() == time_casa, rodada].values[0]
            pontos_visitante = resultados_a.loc[resultados_a['Time'].str.strip() == time_visitante, rodada].values[0]
            
            col1, col2, col3, col4, col5, col6, col7, col8,col9,col10 = st.columns(10)
            with col1:
                st.write(f"**{time_casa}**")
            with col2:
                st.write(str(pontos_casa))  # Converter pontos para string
            with col3:
                st.write('X')
            with col4:
                st.write(str(pontos_visitante))  # Converter pontos para string
            with col5:
                st.write(f"**{time_visitante}**")

with tab2:
    resultados_b = resultados[resultados['Grupo'] == "B"]
    confrontos_b = confrontos[confrontos['Grupo'] ==  "B"]
    resultados_filtrados_b = resultados_filtrados[resultados_filtrados['Grupo'] ==  "B"]
    confrontos_filtrados_b = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "B"]
    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_b = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_b, resultados_filtrados, confrontos_filtrados)

    # Ordenar a tabela por pontos e saldo de pontos
    tabela_b = tabela_b.sort_values(by=['Pontos', 'Saldo'], ascending=False)
    tabela_b
    
    st.markdown('## **Confrontos**')

    # Obter rodadas únicas
    rodadas = confrontos_b['Rodada'].unique()
    resultados_b = resultados_b.replace({None: ''})
    for rodada in rodadas:
        st.markdown("---") 
        st.subheader(f'**{rodada}**')

        
         # Linha de separação
        jogos = confrontos_b[confrontos_b['Rodada'] == rodada]
        for _, jogo in jogos.iterrows():
            time_casa = jogo['Time A'].strip()
            time_visitante = jogo['Time B'].strip()
            
          
            
            # Obter os resultados_a dos times para a rodada
            pontos_casa = resultados_b.loc[resultados_b['Time'].str.strip() == time_casa, rodada].values[0]
            pontos_visitante = resultados_b.loc[resultados_b['Time'].str.strip() == time_visitante, rodada].values[0]
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.write(f"**{time_casa}**")
            with col2:
                st.write(str(pontos_casa))  # Converter pontos para string
            with col3:
                st.write('X')
            with col4:
                st.write(str(pontos_visitante))  # Converter pontos para string
            with col5:
                st.write(f"**{time_visitante}**")