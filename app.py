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

# Estilo visual general
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
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

# ==========================================
# --- CUERPO PRINCIPAL (INTERACTIVIDAD CRUZADA) ---
# ==========================================
st.title("📊 Tablero Gerencial: Analítica de Glosas")
st.subheader("S.O. Servicios Médicos Oftalmológicos (Bogotá)")
st.markdown("---")

# Inicializar un DataFrame dinámico para acumular los filtros cruzados
df_filtrado = df_base.copy()

# -------------------------------------------------------------
# 1. FILTRO DE FECHA DE ATENCIÓN (Ubicar debajo de los KPIs - lo definimos arriba para filtrar todo)
# -------------------------------------------------------------
min_f_global = df_base['Fecha_Atencion'].min().date()
max_f_global = df_base['Fecha_Atencion'].max().date()

# Control de estado para el botón de reseteo del slider de atención
if 'slider_atencion' not in st.session_state:
    st.session_state.slider_atencion = (min_f_global, max_f_global)

def reset_atencion():
    st.session_state.slider_atencion = (min_f_global, max_f_global)

# -------------------------------------------------------------
# 2. TARJETAS DE MÉTRICAS (KPIs Interactivos)
# -------------------------------------------------------------
# Aplicar primeramente el filtro de fecha de atención para los KPIs
rango_atencion = st.session_state.slider_atencion
df_kpi = df_base[
    (df_base['Fecha_Atencion'].dt.date >= rango_atencion[0]) & 
    (df_base['Fecha_Atencion'].dt.date <= rango_atencion[1])
]

val_bruto_filtrado = df['Valor_Glosa_Dev'].sum() 
val_depurado_filtrado = df_kpi['Valor_Glosa_Dev'].sum()
impacto_depurado = (val_depurado_filtrado / valor_depurado_total * 100) if valor_depurado_total > 0 else 0
recuento_facturas = df_kpi['Numero_Factura'].nunique()

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

# Renderizar el filtro de Fecha de Atención debajo de los KPIs con su botón de limpiar
st.markdown("#### 📅 Filtro de Fecha de Atención")
col_f1, col_f2 = st.columns([6, 1])
with col_f1:
    st.slider(
        "Rango de Fechas de Atención",
        min_value=min_f_global,
        max_value=max_f_global,
        key="slider_atencion",
        label_visibility="collapsed"
    )
with col_f2:
    st.button("🔄 Restablecer", key="btn_reset_atencion", on_click=reset_atencion)

# Actualizar df_filtrado con la fecha de atención
df_filtrado = df_base[
    (df_base['Fecha_Atencion'].dt.date >= st.session_state.slider_atencion[0]) & 
    (df_base['Fecha_Atencion'].dt.date <= st.session_state.slider_atencion[1])
].copy()

st.markdown("---")

# -------------------------------------------------------------
# 3. GRÁFICOS PRINCIPALES (ANILLO CON TIPOLOGÍA & TOP 10 CAUSALES)
# -------------------------------------------------------------
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("### 📌 Valor Depurado Real por Tipología (Anillo)")
    
    # Filtro integrado de Tipología dentro de su gráfico
    tipologias_disp = ["Todas"] + list(df_filtrado['tipologia'].unique())
    tipologia_sel = st.selectbox("Seleccione Tipología", tipologias_disp, key="sel_tipologia_grafico")
    
    df_tip_base = df_filtrado.copy()
    if tipologia_sel != "Todas":
        df_tip_base = df_tip_base[df_tip_base['tipologia'] == tipologia_sel]
        df_filtrado = df_filtrado[df_filtrado['tipologia'] == tipologia_sel] # Interacción cruzada
        
    df_tipologia = df_tip_base.groupby('tipologia')['Valor_Glosa_Dev'].sum().reset_index()
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
    
    # Filtro integrado de Causales dentro de su gráfico
    lista_causales_disp = list(df_filtrado['Causal_Estandarizada'].unique())
    causales_tarjeta = st.multiselect(
        "Filtrar Causales en Gráfico",
        options=lista_causales_disp,
        default=[],
        key="ms_causales_tarjeta"
    )
    
    df_causal_base = df_filtrado.copy()
    if causales_tarjeta:
        df_causal_base = df_causal_base[df_causal_base['Causal_Estandarizada'].isin(causales_tarjeta)]
        df_filtrado = df_filtrado[df_filtrado['Causal_Estandarizada'].isin(causales_tarjeta)] # Interacción cruzada
        
    df_causal = df_causal_base.groupby('Causal_Estandarizada')['Valor_Glosa_Dev'].sum().reset_index()
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

# -------------------------------------------------------------
# 4. EVOLUCIÓN TEMPORAL & TOP 10 SERVICIOS
# -------------------------------------------------------------
col_g3, col_g4 = st.columns(2)

with col_g3:
    st.markdown("### 📈 Tendencia de Glosas en el Tiempo")
    if not df_filtrado.empty and 'Fecha_Hora_Radicacion' in df_filtrado.columns:
        min_rad = df_filtrado['Fecha_Hora_Radicacion'].min().date()
        max_rad = df_filtrado['Fecha_Hora_Radicacion'].max().date()
        
        if 'slider_rad' not in st.session_state:
            st.session_state.slider_rad = (min_rad, max_rad)
            
        def reset_rad():
            st.session_state.slider_rad = (min_rad, max_rad)
            
        col_r1, col_r2 = st.columns([6, 1])
        with col_r1:
            st.slider(
                "Rango de Radicación",
                min_value=min_rad,
                max_value=max_rad,
                key="slider_rad",
                label_visibility="collapsed"
            )
        with col_r2:
            st.button("🔄 Reset", key="btn_reset_rad", on_click=reset_rad)
            
        r_rad = st.session_state.slider_rad
        df_temp = df_filtrado[
            (df_filtrado['Fecha_Hora_Radicacion'].dt.date >= r_rad[0]) & 
            (df_filtrado['Fecha_Hora_Radicacion'].dt.date <= r_rad[1])
        ].copy()
        
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
        st.info("No hay datos suficientes para la tendencia temporal.")

with col_g4:
    st.markdown("### 👁️ Top 10 Servicios con Mayor Afectación")
    
    # Filtro integrado de Servicios dentro de su tarjeta
    lista_serv_disp = list(df_filtrado['Nombre del servicio '].unique())
    servicio_tarjeta = st.multiselect(
        "Filtrar Servicios en Gráfico",
        options=lista_serv_disp,
        default=[],
        key="ms_servicios_tarjeta"
    )
    
    df_serv_base = df_filtrado.copy()
    if servicio_tarjeta:
        df_serv_base = df_serv_base[df_serv_base['Nombre del servicio '].isin(servicio_tarjeta)]
        df_filtrado = df_filtrado[df_filtrado['Nombre del servicio '].isin(servicio_tarjeta)] # Interacción cruzada
        
    df_serv = df_serv_base.groupby('Nombre del servicio ')['Valor_Glosa_Dev'].sum().reset_index()
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

# -------------------------------------------------------------
# 5. MATRIZ DE SEMAFORIZACIÓN (CON FILTRO INTEGRADO Y TOTALES)
# -------------------------------------------------------------
st.markdown("### 🚦 Matriz de Semaforización de Riesgo Financiero por Causales de Glosa")
st.markdown("Clasificación de riesgo basada en el valor acumulado de glosas por causal (🔴 Alto > $233M, 🟡 Medio $10M - $233M, 🟢 Bajo < $10M).")

# Filtro de Semaforización integrado dentro de su tabla
filtro_riesgo_sel = st.selectbox(
    "Filtrar Matriz por Nivel de Riesgo",
    ["Todos", "Alto (Rojo)", "Medio (Amarillo)", "Bajo (Verde)"],
    key="sel_riesgo_matriz"
)

df_semaforo = df_filtrado.groupby('Causal_Estandarizada')['Valor_Glosa_Dev'].sum().reset_index()

def asignar_riesgo_y_color(valor):
    if valor > 233000000:
        return "Alto (Rojo)", "🔴"
    elif valor >= 10000000:
        return "Medio (Amarillo)", "🟡"
    else:
        return "Bajo (Verde)", "🟢"

if not df_semaforo.empty:
    res_riesgo = df_semaforo['Valor_Glosa_Dev'].apply(asignar_riesgo_y_color)
    df_semaforo['Nivel de Riesgo'] = [r[0] for r in res_riesgo]
    df_semaforo['Semaforo'] = [r[1] for r in res_riesgo]
    
    # Aplicar filtro integrado de nivel de riesgo
    if filtro_riesgo_sel != "Todos":
        df_semaforo = df_semaforo[df_semaforo['Nivel de Riesgo'] == filtro_riesgo_sel]
    
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
    st.info("No hay datos disponibles para la matriz con los filtros seleccionados.")
