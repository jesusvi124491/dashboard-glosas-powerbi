import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Análisis de Glosas - S.O. Servicios Médicos",
    page_icon="👁️",
    layout="wide"
)

# Estilo visual general y título principal grande
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .main-title {
        text-align: center;
        font-size: 32px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 10px;
        margin-bottom: 25px;
    }
    .subtitle-banner {
        text-align: center;
        font-size: 18px;
        font-weight: 600;
        color: #475569;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Carga de datos con caché
@st.cache_data
def cargar_datos():
    df = pd.read_excel("dataset_analisis_powerbi_FINAL_V6.xlsx")
    df['Fecha_Hora_Radicacion'] = pd.to_datetime(df['Fecha_Hora_Radicacion'])
    df['Fecha_Atencion'] = pd.to_datetime(df['Fecha_Atencion'])
    return df

try:
    df = cargar_datos()
except
