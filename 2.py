import streamlit as st
import pydeck as pdk
import networkx as nx
import pandas as pd
import json

# Fungsi untuk memuat data dari file JSON
def load_province_data(filename="province_data.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"File {filename} tidak ditemukan.")
        return {}

# Memuat data koneksi dari file JSON
province_data = load_province_data()

# Fungsi untuk membuat graph dari data kota dan koneksi antar kota
def create_network_graph(province_name):
    # Cek apakah provinsi ada dalam dataset
    if province_name not in province_data:
        st.error(f"Provinsi '{province_name}' tidak ditemukan dalam dataset.")
        return None

    # Membuat graph untuk kota-kota dan koneksinya
    G = nx.Graph()

    # Menambahkan node kota dan hubungan antar kota
    for city, data in province_data[province_name].items():
        lat, lon = data["coords"]
        G.add_node(city, pos=(lat, lon))  # Menambahkan kota sebagai node
        
        # Menambahkan koneksi antar kota (edges)
        for connected_city in data["connections"]:
            G.add_edge(city, connected_city)

    return G

# Fungsi untuk membuat peta dengan pydeck
def create_deck_map(province_name):
    # Membuat graph untuk kota-kota
    G = create_network_graph(province_name)
    
    if not G:
        return
    
    # Menyusun data untuk koordinat node dan edges
    node_data = []
    edge_data = []

    for city, data in province_data[province_name].items():
        lat, lon = data["coords"]
        node_data.append([city, lat, lon])

        # Menyusun data edges (koneksi antar kota)
        for connected_city in data["connections"]:
            connected_lat, connected_lon = province_data[province_name][connected_city]["coords"]
            edge_data.append([lat, lon, connected_lat, connected_lon])

    # Mengkonversi data ke dalam format pandas DataFrame untuk pydeck
    node_df = pd.DataFrame(node_data, columns=["city", "lat", "lon"])
    edge_df = pd.DataFrame(edge_data, columns=["lat1", "lon1", "lat2", "lon2"])

    # Koordinat untuk provinsi Jawa Barat (Bandung sebagai titik pusat)
    lat_center = -6.9175
    lon_center = 107.6191

    # Membuat visualisasi dengan pydeck
    deck = pdk.Deck(
        layers=[
            # Layer untuk menampilkan node (kota)
            pdk.Layer(
                "ScatterplotLayer",
                node_df,
                get_position=["lon", "lat"],
                get_radius=2000,  # Radius titik kota diperkecil
                get_fill_color=[0, 255, 255, 140],  # Warna titik kota
                pickable=True,
                auto_highlight=True,
            ),
            # Layer untuk menampilkan edges (koneksi antar kota)
            pdk.Layer(
                "LineLayer",
                edge_df,
                get_source_position=["lon1", "lat1"],
                get_target_position=["lon2", "lat2"],
                get_color=[255, 0, 0, 255],  # Warna garis koneksi
                get_width=2,  # Ketebalan garis
            ),
        ],
        initial_view_state=pdk.ViewState(
            latitude=lat_center,
            longitude=lon_center,
            zoom=8,  # Zoom level lebih tinggi untuk fokus pada provinsi
            pitch=0,
        ),
        map_style="mapbox://styles/mapbox/streets-v11",  # Gaya peta berwarna dari Mapbox
    )

    return deck

# Streamlit UI
st.title("Peta Koneksi Kota di Provinsi Jawa Barat")

# Input nama provinsi
province_name = st.selectbox("Pilih Provinsi", ["West Java"])

# Menampilkan peta jika provinsi dipilih
if province_name:
    deck = create_deck_map(province_name)
    if deck:
        st.pydeck_chart(deck)
