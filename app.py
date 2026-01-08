import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Configuración de pantalla
st.set_page_config(page_title="Service Manager 98 - Cbba", layout="wide")
geolocator = Nominatim(user_agent="mantenimiento_cbba_v3")

# --- CSS WINDOWS 98 (Más grande y legible) ---
st.markdown("""
    <style>
    .stApp { background-color: #008080; }
    html, body, [class*="st-"] { font-size: 22px !important; color: black; }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #c0c0c0 !important;
        border: 3px solid; border-color: #ffffff #404040 #404040 #ffffff !important;
        padding: 20px !important;
    }
    .win-title {
        background: linear-gradient(90deg, #000080, #1084d0);
        color: white; padding: 10px; font-weight: bold; border: 2px solid #c0c0c0;
    }
    .stButton>button {
        height: 70px; background-color: #c0c0c0 !important; font-weight: bold !important;
        border: 3px solid; border-color: #ffffff #000000 #000000 #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="win-title">Explorador_de_Direcciones_Cbba.exe</div>', unsafe_allow_html=True)

# Memoria del programa
if 'clientes' not in st.session_state:
    st.session_state.clientes = []
if 'temp_coords' not in st.session_state:
    st.session_state.temp_coords = None

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 💾 REGISTRO RÁPIDO")
    nombre_cliente = st.text_input("1. Nombre del Cliente:")
    
    if st.session_state.temp_coords:
        st.success(f"📍 Ubicación capturada: {st.session_state.temp_coords['calle']}")
        
        if st.button("💾 GUARDAR CLIENTE Y DIRECCIÓN"):
            st.session_state.clientes.append({
                "Cliente": nombre_cliente,
                "Dirección": st.session_state.temp_coords['calle'],
                "lat": st.session_state.temp_coords['lat'],
                "lon": st.session_state.temp_coords['lon']
            })
            st.session_state.temp_coords = None # Limpiar para el siguiente
            st.rerun()
    else:
        st.warning("👈 Haz clic en el mapa para marcar la casa del cliente.")

with col2:
    st.markdown("### 🗺️ MAPA INTERACTIVO DE COCHABAMBA")
    
    # Crear mapa base
    m = folium.Map(location=[-17.3935, -66.1570], zoom_start=14)
    
    # Dibujar los clientes ya guardados con una señalización (Marcador)
    for c in st.session_state.clientes:
        folium.Marker(
            [c['lat'], c['lon']], 
            popup=f"<b>Cliente:</b> {c['Cliente']}<br><b>Calle:</b> {c['Dirección']}",
            tooltip=c['Cliente'],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # Mostrar mapa y capturar clic
    mapa_interactivo = st_folium(m, width="100%", height=600)

    # Lógica de captura automática por clic
    if mapa_interactivo.get("last_clicked"):
        lat = mapa_interactivo["last_clicked"]["lat"]
        lon = mapa_interactivo["last_clicked"]["lng"]
        
        # Averiguar la calle automáticamente (Geocoding Inverso)
        try:
            location = geolocator.reverse(f"{lat}, {lon}")
            calle = location.address.split(',')[0] if location else "Calle desconocida"
        except:
            calle = "Punto en el mapa"
            
        st.session_state.temp_coords = {"lat": lat, "lon": lon, "calle": calle}
        st.rerun()

# Lista de Clientes guardados
if st.session_state.clientes:
    st.markdown("### 📋 DIRECTORIO DE MANTENIMIENTO")
    df = pd.DataFrame(st.session_state.clientes)
    st.table(df[["Cliente", "Dirección"]])