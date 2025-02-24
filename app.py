from flask import Flask, render_template, request
import folium
from folium.plugins import MarkerCluster
from datetime import datetime
import os
import pandas as pd
import plotly.graph_objects as go
import json

app = Flask(__name__)

# Função para carregar os dados do CSV
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), 'accidents_2017_to_2023_portugues.csv')
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

# Rota para a página principal
@app.route('/home')
def home():
    return render_template('home.html')

# Rota principal que renderiza o mapa
@app.route('/')
def index():
    # Carregar os dados
    df = load_data()

    # Criar o mapa centralizado na média das coordenadas
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    # Adicionar marcadores no mapa
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Data: {row['date'].strftime('%Y-%m-%d')}").add_to(marker_cluster)

    # Converter o mapa para HTML
    map_html = m._repr_html_()

    return render_template('index.html', map_html=map_html)

# Rota para filtrar por data e BR
@app.route('/filter', methods=['POST'])
def filter_data():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    br_filter = request.form.get('br_filter')  # Novo campo para filtrar por BR

    # Carregar dados
    df = load_data()

    # Aplicar filtro de data
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Aplicar filtro de BR (se fornecido)
    if br_filter:
        br_filter = float(br_filter)  # Converter para float
        df = df[df['br'] == br_filter]

    # Criar o mapa com os dados filtrados
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    # Adicionar marcadores no mapa
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Data: {row['date'].strftime('%Y-%m-%d')}").add_to(marker_cluster)

    map_html = m._repr_html_()

    return render_template('index.html', map_html=map_html)

# Rota para o gráfico de variação percentual
@app.route('/grafico')
def grafico():
    # Criando o DataFrame com os dados fornecidos
    data = {
        2017: {'Reta': 158, 'Curva': 57, 'Não Informado': 37, 'Rotatória': 30, 'Desvio Temporário': 16,
               'Interseção de vias': 13, 'Retorno Regulamentado': 3, 'Viaduto': 3, 'Ponte': 2, 'Túnel': 1},
        2018: {'Reta': 116, 'Curva': 48, 'Não Informado': 58, 'Rotatória': 10, 'Desvio Temporário': 24,
               'Interseção de vias': 11, 'Viaduto': 2, 'Retorno Regulamentado': 1, 'Túnel': 1},
        2019: {'Reta': 126, 'Curva': 42, 'Não Informado': 51, 'Rotatória': 9, 'Desvio Temporário': 14,
               'Interseção de vias': 9, 'Ponte': 4, 'Retorno Regulamentado': 2, 'Viaduto': 1},
        2020: {'Reta': 120, 'Curva': 46, 'Não Informado': 58, 'Rotatória': 13, 'Desvio Temporário': 13,
               'Interseção de vias': 8, 'Túnel': 2, 'Viaduto': 1},
        2021: {'Reta': 115, 'Curva': 51, 'Não Informado': 53, 'Rotatória': 15, 'Desvio Temporário': 17,
               'Interseção de vias': 5},
        2022: {'Reta': 215, 'Curva': 28, 'Não Informado': 90, 'Desvio Temporário': 30, 'Interseção de vias': 17,
               'Rotatória': 9, 'Viaduto': 6, 'Retorno Regulamentado': 3},
    }

    # Convertendo os dados em um DataFrame
    df = pd.DataFrame(data)

    # Calcular a variação percentual entre os anos (de 2017 até 2023)
    var_percentual = df.pct_change(axis='columns') * 100  # Variação percentual entre colunas (anos)

    # Plotando o gráfico
    fig = go.Figure()

    # Adicionando uma linha para cada tipo de tracado_via
    for tracado in var_percentual.index:
        fig.add_trace(go.Scatter(x=var_percentual.columns, y=var_percentual.loc[tracado],
                       mode='lines+markers', name=tracado))

    # Atualizando o layout do gráfico
    fig.update_layout(
        title="Variação Percentual de Tracado Via (2017-2023)",
        xaxis_title="Ano",
        yaxis_title="Variação Percentual (%)",
        template="plotly_dark",
        legend_title="Tracado Via"
    )

    # Converter o gráfico para JSON
    grafico_json = fig.to_json()

    # Renderizar a página do gráfico
    return render_template('grafico.html', grafico_json=grafico_json)

if __name__ == '__main__':
    app.run(debug=True)