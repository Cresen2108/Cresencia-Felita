import streamlit as st
import pydeck as pdk
import networkx as nx
import pandas as pd
import json
import matplotlib.pyplot as plt

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
menu = st.sidebar.radio("Pilih Menu", ["Profil", "Kosongkan", "Peta Koneksi Kota"])

if menu == "Profil":
    st.title("Profil Anggota")
    profiles = [
        {"name": "Nadia Khaerani", "role": "Actuarial Science", "photo": "https://raw.githubusercontent.com/Cresen2108/Cresencia-Felita/839b5177184935c5bbc2ffb903edd21ca9726ebc/0983.png"},
        {"name": "Cresencia Felita Johan", "role": "Actuarial Science", "photo": "https://raw.githubusercontent.com/Cresen2108/Cresencia-Felita/839b5177184935c5bbc2ffb903edd21ca9726ebc/1441.png"},
        {"name": "Febris Sesilia Banglangi ", "role": "Actuarial Science", "photo": "https://raw.githubusercontent.com/Cresen2108/Cresencia-Felita/839b5177184935c5bbc2ffb903edd21ca9726ebc/1493.png"},
    ]

    for profile in profiles:
        st.image(profile["photo"], width=150)
        st.subheader(profile["name"])
        st.write(f"Peran: {profile['role']}")
        st.markdown("---")

elif menu == "Kosongkan":
    # Streamlit UI for graph visualization
    st.title("Visualisasi Graph")
    
    num_nodes = st.number_input("Masukkan jumlah node", min_value=1, value=5)
    num_edges = st.number_input("Masukkan jumlah edge", min_value=0, value=3)

    edges = []
    for i in range(num_edges):
        edge = st.text_input(f"Masukkan edge {i+1} (node1, node2)", "")
        if edge:
            edges.append(tuple(map(int, edge.split(','))))

    if st.button("Visualisasikan Graph"):
        def visualize_graph(num_nodes, edges):
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
