import streamlit as st
from streamlit_folium import st_folium
import folium
import osmnx as ox
import networkx as nx
from osmnx.distance import nearest_nodes
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, mapping
import numpy as np

st.set_page_config(page_title="안전 경로 추천기", layout="wide")
st.title("🧭 초보자용 안전 경로 추천기")

def create_map():
    m = folium.Map(location=[37.510, 127.030], zoom_start=13)
    m.add_child(folium.LatLngPopup())

    # 강남구 경계 폴리라인으로 표시 (GeoJson 대신)
    gdf_boundary = ox.geocode_to_gdf("Gangnam-gu, Seoul, South Korea")
    coords = mapping(gdf_boundary.geometry.iloc[0])["coordinates"][0]
    coords = [(lat, lon) for lon, lat in coords]

    folium.PolyLine(
        coords,
        color="red",
        weight=2,
        dash_array="5, 5",
        tooltip="강남구 경계"
    ).add_to(m)

    return m

@st.cache_resource
def load_graph_and_risks():
    place = "Gangnam-gu, Seoul, South Korea"
    G = ox.graph_from_place(place, network_type='drive')

    intersection_nodes = [node for node, deg in G.degree() if deg >= 3]
    intersections = []
    for node in intersection_nodes:
        x = G.nodes[node]['x']
        y = G.nodes[node]['y']
        intersections.append({'osmid': node, 'geometry': Point(x, y)})
    gdf = gpd.GeoDataFrame(intersections, crs="EPSG:4326")
    gdf = gdf[gdf.is_valid & ~gdf.is_empty & ~gdf.geometry.isna()]

    def calculate_risk(edges):
        score = 0
        for edge in edges:
            hwy = edge.get('highway', 'unclassified')
            lanes = edge.get('lanes')
            signal = edge.get('traffic_signal', 'no')
            if isinstance(hwy, list): hwy = hwy[0]
            if hwy is None: hwy = 'unclassified'
            highway_score = {'motorway': 3, 'trunk': 2.5, 'primary': 2, 'secondary': 1.5, 'tertiary': 1, 'residential': 0.5, 'unclassified': 1}.get(hwy, 1)
            score += highway_score
            try: lanes = float(lanes) if lanes else 1
            except: lanes = 1
            score += lanes * 0.5
            if str(signal).lower() == 'no': score += 2
        return score

    df_risk = pd.DataFrame([{'osmid': node, 'risk_score': calculate_risk([e[2] for e in G.edges(node, data=True)])} for node in gdf['osmid']])
    gdf_risk = gdf.merge(df_risk, on='osmid')
    gdf_risk = gdf_risk[~gdf_risk['risk_score'].isna() & np.isfinite(gdf_risk['risk_score'])]

    for u, v, key, data in G.edges(keys=True, data=True):
        length = data.get('length', 1)
        risk_u = gdf_risk.set_index('osmid').risk_score.get(u, 0)
        risk_v = gdf_risk.set_index('osmid').risk_score.get(v, 0)
        avg_risk = (risk_u + risk_v) / 2
        data['weight'] = length + avg_risk * 10

    return G

G = load_graph_and_risks()
m = create_map()

st.write("🟢 지도에서 출발지와 도착지를 순서대로 클릭하세요.")

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔄 클릭 초기화"):
        st.session_state.clicks = []
        st.rerun()

if "clicks" not in st.session_state:
    st.session_state.clicks = []

st_map = st_folium(m, height=600, width=1000)

if st_map.get("last_clicked"):
    latlng = st_map["last_clicked"]
    if len(st.session_state.clicks) < 2:
        st.session_state.clicks.append((latlng["lat"], latlng["lng"]))
        st.success(f"📍 위치 저장됨: {latlng['lat']:.5f}, {latlng['lng']:.5f}")

if len(st.session_state.clicks) == 1:
    st.info("🟢 출발지가 설정되었습니다. 도착지를 클릭하세요.")
elif len(st.session_state.clicks) == 2:
    st.success("📍 출발지와 도착지 모두 선택됨. 경로를 계산합니다...")

if len(st.session_state.clicks) == 2:
    orig_point, dest_point = st.session_state.clicks

    try:
        orig_node = nearest_nodes(G, X=orig_point[1], Y=orig_point[0])
        dest_node = nearest_nodes(G, X=dest_point[1], Y=dest_point[0])

        safe_route = nx.shortest_path(G, orig_node, dest_node, weight='weight')
        short_route = nx.shortest_path(G, orig_node, dest_node, weight='length')

        m_route = folium.Map(location=orig_point, zoom_start=14)

        folium.PolyLine([(G.nodes[n]['y'], G.nodes[n]['x']) for n in short_route], color='gray', weight=4, tooltip='Shortest').add_to(m_route)
        folium.PolyLine([(G.nodes[n]['y'], G.nodes[n]['x']) for n in safe_route], color='blue', weight=4, tooltip='Safe Route').add_to(m_route)

        folium.Marker(orig_point, icon=folium.Icon(color='green'), popup='출발지').add_to(m_route)
        folium.Marker(dest_point, icon=folium.Icon(color='red'), popup='도착지').add_to(m_route)

        st.markdown("---")
        st.success("📍 경로 탐색 완료! 아래 지도를 확인하세요.")
        st_folium(m_route, height=600, width=1000)

    except nx.NetworkXNoPath as e:
        st.error("❌ 출발지와 도착지 사이에 연결된 경로가 없습니다.")
        st.code(f"NetworkXNoPath: {e}")
    except Exception as e:
        st.error("🚨 알 수 없는 에러 발생")
        st.code(str(e))
