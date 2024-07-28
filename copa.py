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
    layout="wide"
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

def df_to_html(df):
    html = '<div style="width: 60%; margin-left: 0%; padding: 10px;">'  # Ajustar a largura e margem esquerda
    html += '<table style="width: 100%; border-collapse: collapse;">'
    html += '<thead>'
    html += '<tr>'
    for col in df.columns:
        html += f'<th style="border: 1px solid black; padding: 8px;">{col}</th>'
    html += '</tr>' 
    html += '</thead>'
    html += '<tbody>'
    for i, row in df.iterrows():
        if i < 2:
            bg_color = '#d4edda'  # Verde claro para as duas primeiras linhas
        else:
            bg_color = '#ffffff'  # Branco para as demais linhas
        html += f'<tr style="background-color: {bg_color};">'
        for val in row:
            html += f'<td style="border: 1px solid black; padding: 8px;">{val}</td>'
        html += '</tr>'
    html += '</tbody>'
    html += '</table>'
    html += '</div>'
    return html

with tab1:
    resultados_a = resultados[resultados['Grupo'] == "A"]
    confrontos_a = confrontos[confrontos['Grupo'] ==  "A"]
    resultados_filtrados_b = resultados_filtrados[resultados_filtrados['Grupo'] ==  "A"]
    confrontos_filtrados_a = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "A"]

    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_a = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_a, resultados_filtrados_b, confrontos_filtrados_a)

    # Ordenar a tabela por pontos e saldo de pontos
    tabela_a = tabela_a.sort_values(by=['Pontos', 'Saldo'], ascending=False)
    tabela_a[''] = [f"{i+1}º" for i in range(len(tabela_a))]
    tabela_a = tabela_a[['', 'Pontos', 'Saldo']]

    tabela_a.reset_index(inplace=True)
    tabela_a.rename(columns={'index': 'Time'}, inplace=True)
    tabela_a = tabela_a[['', 'Time', 'Pontos', 'Saldo']]

    
    html_table_a = df_to_html(tabela_a)
    st.markdown(html_table_a, unsafe_allow_html=True)
    
    st.markdown('## **Confrontos**')

    # Obter rodadas únicas
    rodadas = confrontos_a['Rodada'].unique()
    resultados_a = resultados_a.replace({None: ''})

    st.markdown("""
                <style>
                .confronto {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px;
                    border-bottom: 1px solid #ccc;
                }
                .confronto div {
                    flex: 1;
                    text-align: center;
                }
                .confronto div:nth-child(1), .confronto div:nth-child(5) {
                    flex: 2;
                }
                @media (max-width: 768px) {
                    .confronto {
                        flex-direction: column;
                    }
                    .confronto div {
                        text-align: left;
                    }
                }
                </style>
                """, unsafe_allow_html=True)
    

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


            st.markdown(f"""
                <div class="confronto">
                    <div><b>{time_casa}</b></div>
                    <div>{str(pontos_casa)}</div>
                    <div>X</div>
                    <div>{str(pontos_visitante)}</div>
                    <div><b>{time_visitante}</b></div>
                </div>
                """, unsafe_allow_html=True)


with tab2:
    resultados_b = resultados[resultados['Grupo'] == "B"]
    confrontos_b = confrontos[confrontos['Grupo'] ==  "B"]
    resultados_filtrados_b = resultados_filtrados[resultados_filtrados['Grupo'] ==  "B"]
    confrontos_filtrados_b = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "B"]

    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_b = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_b, resultados_filtrados_b, confrontos_filtrados_b)

    # Ordenar a tabela por pontos e saldo de pontos
    tabela_b = tabela_b.sort_values(by=['Pontos', 'Saldo'], ascending=False)
    tabela_b[''] = [f"{i+1}º" for i in range(len(tabela_b))]
    tabela_b = tabela_b[['', 'Pontos', 'Saldo']]

    tabela_b.reset_index(inplace=True)
    tabela_b.rename(columns={'index': 'Time'}, inplace=True)
    tabela_b = tabela_b[['', 'Time', 'Pontos', 'Saldo']]

    
    html_table_a = df_to_html(tabela_b)
    st.markdown(html_table_a, unsafe_allow_html=True)
    
    st.markdown('## **Confrontos**')

    # Obter rodadas únicas
    rodadas = confrontos_b['Rodada'].unique()
    resultados_b = resultados_b.replace({None: ''})

    st.markdown("""
                <style>
                .confronto {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px;
                    border-bottom: 1px solid #ccc;
                }
                .confronto div {
                    flex: 1;
                    text-align: center;
                }
                .confronto div:nth-child(1), .confronto div:nth-child(5) {
                    flex: 2;
                }
                @media (max-width: 768px) {
                    .confronto {
                        flex-direction: column;
                    }
                    .confronto div {
                        text-align: left;
                    }
                }
                </style>
                """, unsafe_allow_html=True)
    

    for rodada in rodadas:
        st.markdown("---") 
        st.subheader(f'**{rodada}**')

        
         # Linha de separação
        jogos = confrontos_b[confrontos_b['Rodada'] == rodada]
        for _, jogo in jogos.iterrows():
            time_casa = jogo['Time A'].strip()
            time_visitante = jogo['Time B'].strip()
            
          
            
            # Obter os resultados_b dos times para a rodada
            pontos_casa = resultados_b.loc[resultados_b['Time'].str.strip() == time_casa, rodada].values[0]
            pontos_visitante = resultados_b.loc[resultados_b['Time'].str.strip() == time_visitante, rodada].values[0]


            st.markdown(f"""
                <div class="confronto">
                    <div><b>{time_casa}</b></div>
                    <div>{str(pontos_casa)}</div>
                    <div>X</div>
                    <div>{str(pontos_visitante)}</div>
                    <div><b>{time_visitante}</b></div>
                </div>
                """, unsafe_allow_html=True)
