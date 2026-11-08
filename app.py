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
except Exception as e:
    st.error(f"Error al cargar el archivo de datos: {e}")
    st.stop()

# --- CÁLCULOS BASE ---
valor_bruto_total = df['Valor_Glosa_Dev'].sum()
df_depurado_global = df[df['item_repetido'] == False]
valor_depurado_total = df_depurado_global['Valor_Glosa_Dev'].sum()

# Base de datos depurada estricta
df_base = df[df['item_repetido'] == False].copy()

min_f_at = df_base['Fecha_Atencion'].min().date()
max_f_at = df_base['Fecha_Atencion'].max().date()
min_f_rad = df_base['Fecha_Hora_Radicacion'].min().date()
max_f_rad = df_base['Fecha_Hora_Radicacion'].max().date()

# ==========================================
# --- GESTIÓN DE ACCIONES DE RESETEO ---
# ==========================================
if st.session_state.get('trigger_reset_global', False):
    st.session_state.tipologia_sel = "Todas"
    st.session_state.causal_sel = "Todas"
    st.session_state.riesgo_sel = "Todos"
    st.session_state.servicios_sel = []
    st.session_state.widget_rango_atencion = (min_f_at, max_f_at)
    st.session_state.widget_rango_radicacion = (min_f_rad, max_f_rad)
    st.session_state.trigger_reset_global = False

if st.session_state.get('trigger_reset_at', False):
    st.session_state.widget_rango_atencion = (min_f_at, max_f_at)
    st.session_state.trigger_reset_at = False

if st.session_state.get('trigger_reset_rad', False):
    st.session_state.widget_rango_radicacion = (min_f_rad, max_f_rad)
    st.session_state.trigger_reset_rad = False


# ==========================================
# --- TÍTULO PRINCIPAL (GRANDE Y CENTRADO) ---
# ==========================================
st.markdown('<div class="main-title">📊
