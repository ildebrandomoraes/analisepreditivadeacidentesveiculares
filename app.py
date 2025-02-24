import os
import pandas as pd
from flask import Flask, render_template, request
import folium
from folium.plugins import MarkerCluster
from datetime import datetime

app = Flask(__name__)

# Função para carregar os dados do CSV
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), 'accidents_2017_to_2023_portugues.csv')
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    

    return df

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

if __name__ == '__main__':
    app.run(debug=True)