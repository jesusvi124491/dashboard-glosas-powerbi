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
st.markdown('<div class="main-title">Tablero Gerencial: Analitica de Glosas</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-banner">S.O. Servicios Medicos Oftalmologicos (Bogota)</div>', unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# --- PANEL DE FILTROS INTERACTIVOS ---
# ==========================================
st.markdown("### Filtros Interactivos del Tablero")

# Fila 1 de filtros
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    tipologias_disp = ["Todas"] + list(df_base['tipologia'].unique())
    tipologia_sel = st.selectbox("Filtrar por Tipología", tipologias_disp, key='tipologia_sel')

with col_f2:
    causales_disp = ["Todas"] + list(df_base['Causal_Estandarizada'].unique())
    causal_sel = st.selectbox("Filtrar por Causal Estandarizada", causales_disp, key='causal_sel')

with col_f3:
    riesgo_disp = ["Todos", "Alto (Rojo)", "Medio (Amarillo)", "Bajo (Verde)"]
    riesgo_sel = st.selectbox("Filtrar por Nivel de Riesgo (Semaforo)", riesgo_disp, key='riesgo_sel')

# Fila 2 de filtros (Servicios y Fechas)
col_f4, col_f5, col_f6 = st.columns(3)

with col_f4:
    servicios_disp = list(df_base['Nombre del servicio '].unique())
    servicios_sel = st.multiselect("Filtrar Servicios Especificos", options=servicios_disp, key='servicios_sel')

with col_f5:
    st.markdown("Rango de Fecha de Atencion")
    sub_fa1, sub_fa2 = st.columns([4, 1])
    with sub_fa1:
        rango_atencion = st.date_input(
            "Atencion",
            value=st.session_state.get('widget_rango_atencion', (min_f_at, max_f_at)),
            min_value=min_f_at,
            max_value=max_f_at,
            key='widget_rango_atencion',
            label_visibility="collapsed"
        )
    with sub_fa2:
        if st.button("🔄", key="btn_reset_at", help="Restablecer Fecha de Atencion"):
            st.session_state.trigger_reset_at = True
            st.rerun()

with col_f6:
    st.markdown("Rango de Fecha de Radicacion")
    sub_fr1, sub_fr2 = st.columns([4, 1])
    with sub_fr1:
        rango_radicacion = st.date_input(
            "Radicacion",
            value=st.session_state.get('widget_rango_radicacion', (min_f_rad, max_f_rad)),
            min_value=min_f_rad,
            max_value=max_f_rad,
            key='widget_rango_radicacion',
            label_visibility="collapsed"
        )
    with sub_fr2:
        if st.button("🔄", key="btn_reset_rad", help="Restablecer Fecha de Radicacion"):
            st.session_state.trigger_reset_rad = True
            st.rerun()

# Botón de Restablecimiento Global centrado justo después del último filtro
st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([3, 4, 3])
with col_btn2:
    if st.button("Restablecer Todos los Filtros (Global)", use_container_width=True):
        st.session_state.trigger_reset_global = True
        st.rerun()

st.markdown("---")

# ==========================================
# --- APLICAR FILTROS EN CASCADA A TODO EL DATASET ---
# ==========================================
df_filtrado = df_base.copy()

if st.session_state.get('tipologia_sel', 'Todas') != "Todas":
    df_filtrado = df_filtrado[df_filtrado['tipologia'] == st.session_state.tipologia_sel]

if st.session_state.get('causal_sel', 'Todas') != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Causal_Estandarizada'] == st.session_state.causal_sel]

if st.session_state.get('servicios_sel', []):
    df_filtrado = df_filtrado[df_filtrado['Nombre del servicio '].isin(st.session_state.servicios_sel)]

if 'widget_rango_atencion' in st.session_state and len(st.session_state.widget_rango_atencion) == 2:
    f_ini, f_fin = st.session_state.widget_rango_atencion
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha_Atencion'].dt.date >= f_ini) & 
        (df_filtrado['Fecha_Atencion'].dt.date <= f_fin)
    ]

if 'widget_rango_radicacion' in st.session_state and len(st.session_state.widget_rango_radicacion) == 2:
    r_ini, r_fin = st.session_state.widget_
