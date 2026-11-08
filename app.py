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

# Validación segura del rango de atención
val_at = st.session_state.get('widget_rango_atencion')
if val_at and isinstance(val_at, (list, tuple)) and len(val_at) == 2:
    f_ini, f_fin = val_at
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha_Atencion'].dt.date >= f_ini) & 
        (df_filtrado['Fecha_Atencion'].dt.date <= f_fin)
    ]

# Validación segura del rango de radicación
val_rad = st.session_state.get('widget_rango_radicacion')
if val_rad and isinstance(val_rad, (list, tuple)) and len(val_rad) == 2:
    r_ini, r_fin = val_rad
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
val_bruto_filtrado = df['Valor_Glosa_Dev'].sum() 
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
    st.metric("Recuento de Facturas", f"${recuento_facturas:,}")

st.markdown("---")

# ==========================================
# --- 2. GRÁFICOS PRINCIPALES (ANILLO TIPOLOGÍA Y % FRECUENCIA CÓDIGO GLOSA - TOP 10) ---
# ==========================================
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("### Valor Depurado Real por Tipología (Anillo)")
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
    st.markdown("### % Frecuencia de Glosa por Código (Top 10)")
    # Replicando exactamente la medida DAX con ALL('Sheet1') -> denominador fijo de df_base
    df_frec_glosa = df_filtrado.groupby('Codigo_Glosa_Dev').size().reset_index(name='Conteo')
    total_conteo_absoluto = len(df_base)
    df_frec_glosa['Porcentaje'] = (df_frec_glosa['Conteo'] / total_conteo_absoluto * 100) if total_conteo_absoluto > 0 else 0
    df_frec_glosa = df_frec_glosa.sort_values(by='Porcentaje', ascending=False).head(10)
    
    fig_frec = px.pie(
        df_frec_glosa,
        names='Codigo_Glosa_Dev',
        values='Porcentaje',
        hole=0.5,
        labels={'Codigo_Glosa_Dev': 'Código de Glosa', 'Porcentaje': '% Frecuencia'}
    )
    fig_frec.update_traces(textposition='inside', textinfo='percent+label')
    fig_frec.update_layout(margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_frec, use_container_width=True)

st.markdown("---")

# ==========================================
# --- 3. TOP 10 CAUSALES Y TENDENCIA TEMPORAL ---
# ==========================================
col_g3, col_g4 = st.columns(2)

with col_g3:
    st.markdown("### Top 10 Causales Estandarizadas")
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

with col_g4:
    st.markdown("### Tendencia de Glosas en el Tiempo")
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

st.markdown("---")

# ==========================================
# --- 4. TOP 10 SERVICIOS Y MATRIZ DE SEMAFORIZACIÓN ---
# ==========================================
col_g5, col_g6 = st.columns(2)

with col_g5:
    st.markdown("### Top 10 Servicios con Mayor Afectación")
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

with col_g6:
    st.markdown("### Matriz de Semaforización de Riesgo Financiero")
    st.markdown("Clasificación por valor acumulado (🔴 Alto > $233M, 🟡 Medio $10M-$233M, 🟢 Bajo < $10M).")
    
    df_semaforo = df_filtrado.groupby('Causal_Estandarizada')['Valor_Glosa_Dev'].sum().reset_index()

    if not df_semaforo.empty and df_semaforo['Valor_Glosa_Dev'].sum() > 0:
        res_riesgo = df_semaforo['Valor_Glosa_Dev'].apply(asignar_riesgo_y_color)
        df_semaforo['Nivel de Riesgo'] = [r[0] for r in res_riesgo]
        df_semaforo['Semaforo'] = [r[1] for r in res_riesgo]
        
        suma_total_glosas = df_semaforo['Valor_Glosa_Dev'].sum()
        
        df_semaforo = df_semaforo.sort_values(by='Valor_Glosa_Dev', ascending=False)
        df_semaforo['Valor_Glosa_Dev'] = df_semaforo['Valor_Glosa_Dev'].map('${:,.0f}'.format)
        
        fila_total = pd.DataFrame({
            'Semaforo': ['📊'],
            'Causal_Estandarizada': ['**TOTAL GENERAL**'],
            'Nivel de Riesgo': ['-'],
            'Valor_Glosa_Dev': [f'${suma_total_glosas:,.0f}']
        })
        df_semaforo_final = pd.concat([df_semaforo, fila_total], ignore_index=True)

        st.dataframe(
            df_semaforo_final[['Semaforo', 'Causal_Estandarizada', 'Nivel de Riesgo', 'Valor_Glosa_Dev']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay registros disponibles con los filtros seleccionados.")
