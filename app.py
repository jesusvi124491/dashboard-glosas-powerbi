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

# Estilo visual general, título grande y barra lateral de 1000px
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
    /* Ancho de 1000px para la barra lateral flotante */
    [data-testid="stSidebar"] {
        min-width: 1000px !important;
        max-width: 1000px !important;
        z-index: 999999 !important;
        box-shadow: 5px 0px 30px rgba(0, 0, 0, 0.3);
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

# --- CÁLCULOS BASE EXACTOS ---
valor_bruto_total = df['Valor_Glosa_Dev'].sum()
df_base = df[df['item_repetido'] == False].copy()
valor_depurado_total = df_base['Valor_Glosa_Dev'].sum()

min_f_at = df_base['Fecha_Atencion'].min().date()
max_f_at = df_base['Fecha_Atencion'].max().date()
min_f_rad = df_base['Fecha_Hora_Radicacion'].min().date()
max_f_rad = df_base['Fecha_Hora_Radicacion'].max().date()

# ==========================================
# --- GESTIÓN SEGURA DE ESTADOS Y RESETEOS ---
# ==========================================
if 'trigger_reset_global' not in st.session_state:
    st.session_state.trigger_reset_global = False

if st.session_state.trigger_reset_global:
    for k in ['tipologia_sel', 'causal_sel', 'riesgo_sel', 'servicios_sel', 'widget_rango_atencion', 'widget_rango_radicacion']:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state.trigger_reset_global = False

# ==========================================
# --- TÍTULO PRINCIPAL (GRANDE Y CENTRADO) ---
# ==========================================
st.markdown('<div class="main-title">📊 Tablero Gerencial: Analítica de Glosas</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-banner">S.O. Servicios Médicos Oftalmológicos (Bogotá)</div>', unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# --- PANEL LATERAL DE FILTROS (1000PX) ---
# ==========================================
st.sidebar.header("🎛️ Filtros Interactivos")
st.sidebar.markdown("---")

# 1. Filtro por Tipología
tipologias_disp = ["Todas"] + list(df_base['tipologia'].unique())
tipologia_sel = st.sidebar.selectbox("📌 Filtrar por Tipología", tipologias_disp, key='tipologia_sel')

# 2. Filtro por Causal Estandarizada
causales_disp = ["Todas"] + list(df_base['Causal_Estandarizada'].unique())
causal_sel = st.sidebar.selectbox("⚠️ Filtrar por Causal Estandarizada", causales_disp, key='causal_sel')

# 3. Filtro por Nivel de Riesgo (Semáforo)
riesgo_disp = ["Todos", "Alto (Rojo)", "Medio (Amarillo)", "Bajo (Verde)"]
riesgo_sel = st.sidebar.selectbox("🚦 Filtrar por Nivel de Riesgo", riesgo_disp, key='riesgo_sel')

st.sidebar.markdown("---")

# 4. Filtro de Servicios Específicos
servicios_disp = list(df_base['Nombre del servicio '].unique())
servicios_sel = st.sidebar.multiselect("👁️ Filtrar Servicios Específicos", options=servicios_disp, key='servicios_sel')

st.sidebar.markdown("---")

# 5. Rango de Fecha de Atención
st.sidebar.markdown("📅 **Rango de Fecha de Atención**")
sub_fa1, sub_fa2 = st.sidebar.columns([4, 1])
with sub_fa1:
    rango_atencion = st.date_input(
        "Atención",
        value=st.session_state.get('widget_rango_atencion', (min_f_at, max_f_at)),
        min_value=min_f_at,
        max_value=max_f_at,
        key='widget_rango_atencion',
        label_visibility="collapsed"
    )
with sub_fa2:
    if st.button("🔄", key="btn_reset_at", help="Restablecer Atención"):
        if 'widget_rango_atencion' in st.session_state:
            del st.session_state['widget_rango_atencion']
        st.rerun()

st.sidebar.markdown("---")

# 6. Rango de Fecha de Radicación
st.sidebar.markdown("📈 **Rango de Fecha de Radicación**")
sub_fr1, sub_fr2 = st.sidebar.columns([4, 1])
with sub_fr1:
    rango_radicacion = st.date_input(
        "Radicación",
        value=st.session_state.get('widget_rango_radicacion', (min_f_rad, max_f_rad)),
        min_value=min_f_rad,
        max_value=max_f_rad,
        key='widget_rango_radicacion',
        label_visibility="collapsed"
    )
with sub_fr2:
    if st.button("🔄", key="btn_reset_rad", help="Restablecer Radicación"):
        if 'widget_rango_radicacion' in st.session_state:
            del st.session_state['widget_rango_radicacion']
        st.rerun()

st.sidebar.markdown("---")

# 7. Botón de Restablecimiento Global
if st.sidebar.button("🔄 Restablecer Todos los Filtros", use_container_width=True):
    st.session_state.trigger_reset_global = True
    st.rerun()


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
    r_ini, r_fin = st.session_state.widget_rango_radicacion
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha_Hora_Radicacion'].dt.date >= r_ini) & 
        (df_filtrado['Fecha_Hora_Radicacion'].dt.date <= r_fin)
    ]

def asignar_riesgo_y_color(valor):
    if valor > 233000000:
        return "Alto (Rojo)", "🔴"
    elif valor >= 10000000:
        return "Medio (Amarillo)", "🟡"
    else:
        return "Bajo (Verde)", "🟢"

if st.session_state.get('riesgo_sel', 'Todos') != "Todos":
    causales_riesgo = df_filtrado.groupby('Causal_Estandarizada')['Valor_Glosa_Dev'].sum().reset_index()
    causales_riesgo['Nivel'] = causales_riesgo['Valor_Glosa_Dev'].apply(lambda x: asignar_riesgo_y_color(x)[0])
    causales_validas = causales_riesgo[causales_riesgo['Nivel'] == st.session_state.riesgo_sel]['Causal_Estandarizada'].tolist()
    df_filtrado = df_filtrado[df_filtrado['Causal_Estandarizada'].isin(causales_validas)]


# ==========================================
# --- 1. TARJETAS DE MÉTRICAS (KPIs) ---
# ==========================================
val_depurado_filtrado = df_filtrado['Valor_Glosa_Dev'].sum()
impacto_depurado = (val_depurado_filtrado / valor_depurado_total * 100) if valor_depurado_total > 0 else 0
recuento_facturas = df_filtrado['Numero_Factura'].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Valor Bruto", f"${valor_bruto_total:,.0f}")
with col2:
    st.metric("Valor Depurado Real", f"${val_depurado_filtrado:,.0f}")
with col3:
    st.metric("% Impacto Depurado", f"{impacto_depurado:.2f}%")
with col4:
    st.metric("Recuento de Facturas", f"{recuento_facturas:,}")

st.markdown("---")

# ==========================================
# --- 2. GRÁFICOS PRINCIPALES (ANILLO Y TOP 10 CAUSALES) ---
# ==========================================
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("### 📌 Valor Depurado Real por Tipología (Anillo)")
    df_tipologia = df_filtrado.groupby('tipologia')['Valor_Glosa_Dev'].sum().reset_index()
    fig_tip = px.pie(
        df_tipologia, 
        names='tipologia', 
        values='Valor_Glosa_Dev', 
        hole=0.5,
        labels={'tipologia': 'Tipología', 'Valor_Glosa_Dev': 'Valor Depurado ($)'}
    )
    fig_tip.update_traces(textposition='inside', textinfo='percent+label')
    fig_tip.update_layout(margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_tip, use_container_width=True)

with col_g2:
    st.markdown("### ⚠️ Top 10 Causales Estandarizadas")
    df_causal = df_filtrado.groupby('Causal_Estandarizada')['Valor_Glosa_Dev'].sum().reset_index()
    df_causal = df_causal.sort_values(by='Valor_Glosa_Dev', ascending=False).head(10)
    fig_causal = px.bar(
        df_causal, 
        y='Causal_Estandarizada', 
        x='Valor_Glosa_Dev', 
        orientation='h',
        text_auto='.2s',
        labels={'Causal_Estandarizada': 'Causal Estandarizada', 'Valor_Glosa_Dev': 'Valor Depurado ($)'}
    )
    fig_causal.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_causal, use_container_width=True)

st.markdown("---")

# ==========================================
# --- 3. EVOLUCIÓN TEMPORAL Y TOP 10 SERVICIOS ---
# ==========================================
col_g3, col_g4 = st.columns(2)

with col_g3:
    st.markdown("### 📈 Tendencia de Glosas en el Tiempo")
    if not df_filtrado.empty and 'Fecha_Hora_Radicacion' in df_filtrado.columns:
        df_temp = df_filtrado.copy()
        df_temp['Periodo'] = df_temp['Fecha_Hora_Radicacion'].dt.to_period('M').astype(str)
        df_temp_grouped = df_temp.groupby('Periodo')['Valor_Glosa_Dev'].sum().reset_index()
        
        fig_temp = px.line(
            df_temp_grouped, 
            x='Periodo', 
            y='Valor_Glosa_Dev',
            markers=True,
            labels={'Periodo': 'Mes de Radicación', 'Valor_Glosa_Dev': 'Valor Depurado ($)'}
        )
        fig_temp.update_layout(xaxis_tickangle=-45, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_temp, use_container_width=True)
    else:
        st.info("No hay datos suficientes para la tendencia temporal con los filtros actuales.")

with col_g4:
    st.markdown("### 👁️ Top 10 Servicios con Mayor Afectación")
    df_serv = df_filtrado.groupby('Nombre del servicio ')['Valor_Glosa_Dev'].sum().reset_index()
    df_serv = df_serv.sort_values(by='Valor_Glosa_Dev', ascending=False).head(10)
    
    fig_serv = px.bar(
        df_serv,
        x='Valor_Glosa_Dev',
        y='Nombre del servicio ',
        orientation='h',
        text_auto='.2s',
        labels={'Nombre del servicio ': 'Servicio', 'Valor_Glosa_Dev': 'Valor Depurado ($)'}
    )
    fig_serv.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_serv, use_container_width=True)

st.markdown("---")

# ==========================================
# --- 4. MATRIZ DE SEMAFORIZACIÓN DE RIESGO FINANCIERO ---
# ==========================================
st.markdown("### 🚦 Matriz de Semaforización de Riesgo Financiero por Causales de Glosa")
st.markdown("Clasificación de riesgo basada en el valor acumulado
