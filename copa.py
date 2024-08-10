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
        #tabela.at[time_casa, 'Saldo'] += (pontos_casa - pontos_visitante)
        #tabela.at[time_visitante, 'Saldo'] += (pontos_visitante - pontos_casa)

        tabela.at[time_casa, 'Saldo'] = round(tabela.at[time_casa, 'Saldo'] + (pontos_casa - pontos_visitante), 2)
        tabela.at[time_visitante, 'Saldo'] = round(tabela.at[time_visitante, 'Saldo'] + (pontos_visitante - pontos_casa), 2)

def df_to_html(df):
    html = '<div style="width: 80%; margin-left: 0%; padding: 10px;">'  # Ajustar a largura e margem esquerda
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
    resultados_filtrados_a = resultados_filtrados[resultados_filtrados['Grupo'] ==  "A"]
    confrontos_filtrados_a = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "A"]

    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_a = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_a, resultados_filtrados_a, confrontos_filtrados_a)

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

    
    html_table_b = df_to_html(tabela_b)
    st.markdown(html_table_b, unsafe_allow_html=True)
    
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
            

   
with tab3:
    resultados_c = resultados[resultados['Grupo'] == "C"]
    confrontos_c = confrontos[confrontos['Grupo'] ==  "C"]
    resultados_filtrados_c = resultados_filtrados[resultados_filtrados['Grupo'] ==  "C"]
    confrontos_filtrados_c = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "C"]

    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_c = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_c, resultados_filtrados_c, confrontos_filtrados_c)

    # Ordenar a tabela por pontos e saldo de pontos
    tabela_c = tabela_c.sort_values(by=['Pontos', 'Saldo'], ascending=False)
    tabela_c[''] = [f"{i+1}º" for i in range(len(tabela_c))]
    tabela_c = tabela_c[['', 'Pontos', 'Saldo']]

    tabela_c.reset_index(inplace=True)
    tabela_c.rename(columns={'index': 'Time'}, inplace=True)
    tabela_c = tabela_c[['', 'Time', 'Pontos', 'Saldo']]

    
    html_table_c = df_to_html(tabela_c)
    st.markdown(html_table_c, unsafe_allow_html=True)
    
    st.markdown('## **Confrontos**')

    # Obter rodadas únicas
    rodadas = confrontos_c['Rodada'].unique()
    resultados_c = resultados_c.replace({None: ''})

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
        jogos = confrontos_c[confrontos_c['Rodada'] == rodada]
        for _, jogo in jogos.iterrows():
            time_casa = jogo['Time A'].strip()
            time_visitante = jogo['Time B'].strip()
            
          
            
            # Obter os resultados_b dos times para a rodada
            pontos_casa = resultados_c.loc[resultados_c['Time'].str.strip() == time_casa, rodada].values[0]
            pontos_visitante = resultados_c.loc[resultados_c['Time'].str.strip() == time_visitante, rodada].values[0]


            st.markdown(f"""
                <div class="confronto">
                    <div><b>{time_casa}</b></div>
                    <div>{str(pontos_casa)}</div>
                    <div>X</div>
                    <div>{str(pontos_visitante)}</div>
                    <div><b>{time_visitante}</b></div>
                </div>
                """, unsafe_allow_html=True)
            

with tab4:
    resultados_d = resultados[resultados['Grupo'] == "D"]
    confrontos_d = confrontos[confrontos['Grupo'] ==  "D"]
    resultados_filtrados_d = resultados_filtrados[resultados_filtrados['Grupo'] ==  "D"]
    confrontos_filtrados_d = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "D"]

    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_d = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_d, resultados_filtrados_d, confrontos_filtrados_d)

    # Ordenar a tabela por pontos e saldo de pontos
    tabela_d = tabela_d.sort_values(by=['Pontos', 'Saldo'], ascending=False)
    tabela_d[''] = [f"{i+1}º" for i in range(len(tabela_d))]
    tabela_d = tabela_d[['', 'Pontos', 'Saldo']]

    tabela_d.reset_index(inplace=True)
    tabela_d.rename(columns={'index': 'Time'}, inplace=True)
    tabela_d = tabela_d[['', 'Time', 'Pontos', 'Saldo']]

    
    html_table_d = df_to_html(tabela_d)
    st.markdown(html_table_d, unsafe_allow_html=True)
    
    st.markdown('## **Confrontos**')

    # Obter rodadas únicas
    rodadas = confrontos_d['Rodada'].unique()
    resultados_d = resultados_d.replace({None: ''})

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
        jogos = confrontos_d[confrontos_d['Rodada'] == rodada]
        for _, jogo in jogos.iterrows():
            time_casa = jogo['Time A'].strip()
            time_visitante = jogo['Time B'].strip()
            
          
            
            # Obter os resultados_b dos times para a rodada
            pontos_casa = resultados_d.loc[resultados_d['Time'].str.strip() == time_casa, rodada].values[0]
            pontos_visitante = resultados_d.loc[resultados_d['Time'].str.strip() == time_visitante, rodada].values[0]


            st.markdown(f"""
                <div class="confronto">
                    <div><b>{time_casa}</b></div>
                    <div>{str(pontos_casa)}</div>
                    <div>X</div>
                    <div>{str(pontos_visitante)}</div>
                    <div><b>{time_visitante}</b></div>
                </div>
                """, unsafe_allow_html=True)
            
with tab5:
    resultados_e = resultados[resultados['Grupo'] == "E"]
    confrontos_e = confrontos[confrontos['Grupo'] ==  "E"]
    resultados_filtrados_e = resultados_filtrados[resultados_filtrados['Grupo'] ==  "E"]
    confrontos_filtrados_e = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "E"]

    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_e = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_e, resultados_filtrados_e, confrontos_filtrados_e)

    # Ordenar a tabela por pontos e saldo de pontos
    tabela_e = tabela_e.sort_values(by=['Pontos', 'Saldo'], ascending=False)
    tabela_e[''] = [f"{i+1}º" for i in range(len(tabela_e))]
    tabela_e = tabela_e[['', 'Pontos', 'Saldo']]

    tabela_e.reset_index(inplace=True)
    tabela_e.rename(columns={'index': 'Time'}, inplace=True)
    tabela_e = tabela_e[['', 'Time', 'Pontos', 'Saldo']]

    
    html_table_e = df_to_html(tabela_e)
    st.markdown(html_table_e, unsafe_allow_html=True)
    
    st.markdown('## **Confrontos**')

    # Obter rodadas únicas
    rodadas = confrontos_e['Rodada'].unique()
    resultados_e = resultados_e.replace({None: ''})

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
        jogos = confrontos_e[confrontos_e['Rodada'] == rodada]
        for _, jogo in jogos.iterrows():
            time_casa = jogo['Time A'].strip()
            time_visitante = jogo['Time B'].strip()
            
          
            
            # Obter os resultados_b dos times para a rodada
            pontos_casa = resultados_e.loc[resultados_e['Time'].str.strip() == time_casa, rodada].values[0]
            pontos_visitante = resultados_e.loc[resultados_e['Time'].str.strip() == time_visitante, rodada].values[0]


            st.markdown(f"""
                <div class="confronto">
                    <div><b>{time_casa}</b></div>
                    <div>{str(pontos_casa)}</div>
                    <div>X</div>
                    <div>{str(pontos_visitante)}</div>
                    <div><b>{time_visitante}</b></div>
                </div>
                """, unsafe_allow_html=True)


with tab6:
    resultados_f = resultados[resultados['Grupo'] == "F"]
    confrontos_f = confrontos[confrontos['Grupo'] ==  "F"]
    resultados_filtrados_f = resultados_filtrados[resultados_filtrados['Grupo'] ==  "F"]
    confrontos_filtrados_f = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "F"]

    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_f = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_f, resultados_filtrados_f, confrontos_filtrados_f)

    # Ordenar a tabela por pontos e saldo de pontos
    tabela_f = tabela_f.sort_values(by=['Pontos', 'Saldo'], ascending=False)
    tabela_f[''] = [f"{i+1}º" for i in range(len(tabela_f))]
    tabela_f = tabela_f[['', 'Pontos', 'Saldo']]

    tabela_f.reset_index(inplace=True)
    tabela_f.rename(columns={'index': 'Time'}, inplace=True)
    tabela_f = tabela_f[['', 'Time', 'Pontos', 'Saldo']]

    
    html_table_f = df_to_html(tabela_f)
    st.markdown(html_table_f, unsafe_allow_html=True)
    
    st.markdown('## **Confrontos**')

    # Obter rodadas únicas
    rodadas = confrontos_f['Rodada'].unique()
    resultados_f = resultados_f.replace({None: ''})

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
        jogos = confrontos_f[confrontos_f['Rodada'] == rodada]
        for _, jogo in jogos.iterrows():
            time_casa = jogo['Time A'].strip()
            time_visitante = jogo['Time B'].strip()
            
          
            
            # Obter os resultados_b dos times para a rodada
            pontos_casa = resultados_f.loc[resultados_f['Time'].str.strip() == time_casa, rodada].values[0]
            pontos_visitante = resultados_f.loc[resultados_f['Time'].str.strip() == time_visitante, rodada].values[0]


            st.markdown(f"""
                <div class="confronto">
                    <div><b>{time_casa}</b></div>
                    <div>{str(pontos_casa)}</div>
                    <div>X</div>
                    <div>{str(pontos_visitante)}</div>
                    <div><b>{time_visitante}</b></div>
                </div>
                """, unsafe_allow_html=True)
   

with tab7:
    resultados_g = resultados[resultados['Grupo'] == "G"]
    confrontos_g = confrontos[confrontos['Grupo'] ==  "G"]
    resultados_filtrados_g = resultados_filtrados[resultados_filtrados['Grupo'] ==  "G"]
    confrontos_filtrados_g = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "G"]

    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_g = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_g, resultados_filtrados_g, confrontos_filtrados_g)

    # Ordenar a tabela por pontos e saldo de pontos
    tabela_g = tabela_g.sort_values(by=['Pontos', 'Saldo'], ascending=False)
    tabela_g[''] = [f"{i+1}º" for i in range(len(tabela_g))]
    tabela_g = tabela_g[['', 'Pontos', 'Saldo']]

    tabela_g.reset_index(inplace=True)
    tabela_g.rename(columns={'index': 'Time'}, inplace=True)
    tabela_g = tabela_g[['', 'Time', 'Pontos', 'Saldo']]

    
    html_table_g = df_to_html(tabela_g)
    st.markdown(html_table_g, unsafe_allow_html=True)
    
    st.markdown('## **Confrontos**')

    # Obter rodadas únicas
    rodadas = confrontos_g['Rodada'].unique()
    resultados_g = resultados_g.replace({None: ''})

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
        jogos = confrontos_g[confrontos_g['Rodada'] == rodada]
        for _, jogo in jogos.iterrows():
            time_casa = jogo['Time A'].strip()
            time_visitante = jogo['Time B'].strip()
            
          
            
            # Obter os resultados_b dos times para a rodada
            pontos_casa = resultados_g.loc[resultados_g['Time'].str.strip() == time_casa, rodada].values[0]
            pontos_visitante = resultados_g.loc[resultados_g['Time'].str.strip() == time_visitante, rodada].values[0]


            st.markdown(f"""
                <div class="confronto">
                    <div><b>{time_casa}</b></div>
                    <div>{str(pontos_casa)}</div>
                    <div>X</div>
                    <div>{str(pontos_visitante)}</div>
                    <div><b>{time_visitante}</b></div>
                </div>
                """, unsafe_allow_html=True)
            

with tab8:
    resultados_h = resultados[resultados['Grupo'] == "H"]
    confrontos_h = confrontos[confrontos['Grupo'] ==  "H"]
    resultados_filtrados_h = resultados_filtrados[resultados_filtrados['Grupo'] ==  "H"]
    confrontos_filtrados_h = confrontos_filtrados[confrontos_filtrados['Grupo'] ==  "H"]

    st.markdown('## **Classificação**')
    # Criar uma tabela vazia com colunas 'Pontos' e 'Saldo'
    tabela_h = pd.DataFrame(columns=['Pontos', 'Saldo'])

    # Atualizar a tabela de classificação com os resultados das rodadas
    atualizar_tabela(tabela_h, resultados_filtrados_h, confrontos_filtrados_h)

    # Ordenar a tabela por pontos e saldo de pontos
    tabela_h = tabela_h.sort_values(by=['Pontos', 'Saldo'], ascending=False)
    tabela_h[''] = [f"{i+1}º" for i in range(len(tabela_h))]
    tabela_h = tabela_h[['', 'Pontos', 'Saldo']]

    tabela_h.reset_index(inplace=True)
    tabela_h.rename(columns={'index': 'Time'}, inplace=True)
    tabela_h = tabela_h[['', 'Time', 'Pontos', 'Saldo']]

    
    html_table_h = df_to_html(tabela_h)
    st.markdown(html_table_h, unsafe_allow_html=True)
    
    st.markdown('## **Confrontos**')

    # Obter rodadas únicas
    rodadas = confrontos_h['Rodada'].unique()
    resultados_h = resultados_h.replace({None: ''})

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
        jogos = confrontos_h[confrontos_h['Rodada'] == rodada]
        for _, jogo in jogos.iterrows():
            time_casa = jogo['Time A'].strip()
            time_visitante = jogo['Time B'].strip()
            
          
            
            # Obter os resultados_b dos times para a rodada
            pontos_casa = resultados_h.loc[resultados_h['Time'].str.strip() == time_casa, rodada].values[0]
            pontos_visitante = resultados_h.loc[resultados_h['Time'].str.strip() == time_visitante, rodada].values[0]


            st.markdown(f"""
                <div class="confronto">
                    <div><b>{time_casa}</b></div>
                    <div>{str(pontos_casa)}</div>
                    <div>X</div>
                    <div>{str(pontos_visitante)}</div>
                    <div><b>{time_visitante}</b></div>
                </div>
                """, unsafe_allow_html=True)