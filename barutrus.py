import streamlit as st
import pydeck as pdk
import networkx as nx
import pandas as pd
import json
import matplotlib.pyplot as plt
import requests
import random

# Fungsi untuk memuat data dari URL GitHub
def load_province_data_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Memastikan respons berhasil
        return response.json()  # Mengambil data JSON dan mengonversinya menjadi objek Python
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal memuat data dari URL: {e}")
        return {}


# URL file JSON di GitHub
json_url = "https://raw.githubusercontent.com/Cresen2108/Cresencia-Felita/refs/heads/main/province_data.json"

# Memuat data koneksi dari URL JSON
province_data = load_province_data_from_url(json_url)

# Fungsi untuk membuat graph dari data kota dan koneksi antar kota
def create_network_graph(province_name):
    if province_name not in province_data:
        st.error(f"Provinsi '{province_name}' tidak ditemukan dalam dataset.")
        return None

    G = nx.Graph()
    for city, data in province_data[province_name].items():
        lat, lon = data["coords"]
        G.add_node(city, pos=(lat, lon))
        for connected_city in data["connections"]:
            G.add_edge(city, connected_city)

    return G

# Fungsi untuk membuat peta dengan pydeck
def create_deck_map(province_name):
    G = create_network_graph(province_name)
    if not G:
        return

    node_data = []
    edge_data = []

    for city, data in province_data[province_name].items():
        lat, lon = data["coords"]
        node_data.append([city, lat, lon])

        for connected_city in data["connections"]:
            connected_lat, connected_lon = province_data[province_name][connected_city]["coords"]
            edge_data.append([lat, lon, connected_lat, connected_lon])

    node_df = pd.DataFrame(node_data, columns=["city", "lat", "lon"])
    edge_df = pd.DataFrame(edge_data, columns=["lat1", "lon1", "lat2", "lon2"])

    lat_center = -6.9175
    lon_center = 107.6191

    deck = pdk.Deck(
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                node_df,
                get_position=["lon", "lat"],
                get_radius=2000,
                get_fill_color=[0, 255, 255, 140],
                pickable=True,
                auto_highlight=True,
            ),
            pdk.Layer(
                "LineLayer",
                edge_df,
                get_source_position=["lon1", "lat1"],
                get_target_position=["lon2", "lat2"],
                get_color=[255, 0, 0, 255],
                get_width=2,
            ),
        ],
        initial_view_state=pdk.ViewState(
            latitude=lat_center,
            longitude=lon_center,
            zoom=8,
            pitch=0,
        ),
        map_style="mapbox://styles/mapbox/streets-v11",
    )
    return deck

# Streamlit UI
st.sidebar.title("Navigasi")
menu = st.sidebar.radio("Pilih Menu", ["Profil", "Graph", "Peta Koneksi Kota"])

if menu == "Profil":
    st.title("Profil Anggota")
    profiles = [
        {"name": "Nadia Khaerani", "role": "Actuarial Science", "photo": "https://raw.githubusercontent.com/Cresen2108/Cresencia-Felita/839b5177184935c5bbc2ffb903edd21ca9726ebc/0983.png"},
        {"name": "Cresencia Felita Johan", "role": "Actuarial Science", "photo": "https://raw.githubusercontent.com/Cresen2108/Cresencia-Felita/839b5177184935c5bbc2ffb903edd21ca9726ebc/1441.png"},
        {"name": "Febris Sesilia Banglangi", "role": "Actuarial Science", "photo": "https://raw.githubusercontent.com/Cresen2108/Cresencia-Felita/839b5177184935c5bbc2ffb903edd21ca9726ebc/1493.png"},
    ]

    for profile in profiles:
        st.image(profile["photo"], width=150)
        st.subheader(profile["name"])
        st.write(f"Peran: {profile['role']}")
        st.markdown("---")

elif menu == "Graph":
    # Streamlit UI for graph visualization
    st.title("Visualisasi Graph")

    num_nodes = st.number_input("Masukkan jumlah node", min_value=1, value=5)
    num_edges = st.number_input("Masukkan jumlah edge", min_value=0, value=3)

    def generate_random_edges(num_nodes, num_edges):
        """Generate random edges for the graph."""
        edges = set()
        while len(edges) < num_edges:
            edge = tuple(sorted(random.sample(range(num_nodes), 2)))
            edges.add(edge)
        return list(edges)

    if num_edges > (num_nodes * (num_nodes - 1)) // 2:
        st.warning("Jumlah edge terlalu banyak untuk jumlah node yang diberikan.")
    else:
        edges = generate_random_edges(num_nodes, num_edges)

        def visualize_graph(num_nodes, edges):
            """Visualize the graph with nodes and edges."""
            G = nx.Graph()

            for i in range(num_nodes):
                G.add_node(i)

            for edge in edges:
                G.add_edge(edge[0], edge[1])

            plt.figure(figsize=(8, 6))
            nx.draw(G, with_labels=True, node_size=700, node_color="lightblue", font_size=15)
            plt.title(f"Graph with {num_nodes} Nodes and {len(edges)} Edges")
            st.pyplot(plt)

        visualize_graph(num_nodes, edges)

elif menu == "Peta Koneksi Kota":
    st.title("Peta Koneksi Kota di Provinsi Jawa Barat")
    province_name = st.selectbox("Pilih Provinsi", ["West Java"])
    if province_name:
        deck = create_deck_map(province_name)
        if deck:
            st.pydeck_chart(deck)
