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

# --- CÁLCULOS BASE EQUIVALENTES A MEDIDAS DAX DE POWER BI ---
valor_bruto_total = df['Valor_Glosa_Dev'].sum()
df_depurado_global = df[df['item_repetido'] == False]
valor_depurado_total = df_depurado_global['Valor_Glosa_Dev'].sum()

# --- BARRA LATERAL (FILTROS GLOBALES) ---
st.sidebar.header("🔍 Filtros Globales")

# Selector de Tipo de Datos (Solo Depurado)
vista_datos = st.sidebar.radio(
    "Tipo de Datos",
    ["Depurado"]
)

df_base = df[df['item_repetido'] == False].copy()

# 1. Filtro por Tipología
tipologias = ["Todas"] + list(df_base['tipologia'].unique())
tipologia_sel = st.sidebar.selectbox("Seleccione Tipología", tipologias)

# 2. Filtro por Fecha de Atención (Rango de Fechas)
min_fecha = df_base['Fecha_Atencion'].min().date()
max_fecha = df_base['Fecha_Atencion'].max().date()

rango_fechas = st.sidebar.date_input(
    "Fecha de Atención",
    value=(min_fecha, max_fecha),
    min_value=min_fecha,
    max_value=max_fecha
)

# 3. Filtro por Causal Estandarizada
causales = ["Todas"] + list(df_base['Causal_Estandarizada'].unique())
causal_sel = st.sidebar.selectbox("Seleccione Causal Estandarizada", causales)

# --- APLICAR FILTROS GLOBALES ---
df_filtrado = df_base.copy()

if tipologia_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['tipologia'] == tipologia_sel]

if causal_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Causal_Estandarizada'] == causal_sel]

if len(rango_fechas) == 2:
    f_inicio, f_fin = rango_fechas
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha_Atencion'].dt.date >= f_inicio) & 
        (df_filtrado['Fecha_Atencion'].dt.date <= f_fin)
    ]

# --- CUERPO PRINCIPAL ---
st.title("📊 Tablero Gerencial: Analítica de Glosas")
st.subheader("S.O. Servicios Médicos Oftalmológicos (Bogotá)")
st.markdown("---")

# 1. TARJETAS DE MÉTRICAS (KPIs)
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
    st.metric("Recuento de Facturas", f"{recuento_facturas:,}")

st.markdown("---")

# 2. GRÁFICOS PRINCIPALES (ANILLO Y TOP 10 CAUSALES)
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

# 3. EVOLUCIÓN TEMPORAL (CON FILTRO ESPECÍFICO DE RANGO DE FECHAS) Y TOP 10 SERVICIOS
col_g3, col_g4 = st.columns(2)

with col_g3:
    st.markdown("### 📈 Tendencia de Glosas en el Tiempo")
    
    # Filtro específico de período para la tendencia temporal
    if not df_filtrado.empty and 'Fecha_Hora_Radicacion' in df_filtrado.columns:
        min_rad = df_filtrado['Fecha_Hora_Radicacion'].min().date()
        max_rad = df_filtrado['Fecha_Hora_Radicacion'].max().date()
        
        rango_rad = st.slider(
            "Filtrar Rango de Radicación",
            min_value=min_rad,
            max_value=max_rad,
            value=(min_rad, max_rad),
            key="slider_rad"
        )
        
        df_temp = df_filtrado[
            (df_filtrado['Fecha_Hora_Radicacion'].dt.date >= rango_rad[0]) & 
            (df_filtrado['Fecha_Hora_Radicacion'].dt.date <= rango_rad[1])
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
    
    # Filtro específico para seleccionar servicios dentro del top
    servicios_unicos = list(df_filtrado['Nombre del servicio '].unique())
    servicio_sel_filtro = st.multiselect(
        "Filtrar Servicios Específicos",
        options=servicios_unicos,
        default=[]
    )
    
    df_serv_base = df_filtrado.copy()
    if servicio_sel_filtro:
        df_serv_base = df_serv_base[df_serv_base['Nombre del servicio '].isin(servicio_sel_filtro)]
        
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

# 4. MATRIZ DE SEMAFORIZACIÓN DE RIESGO FINANCIERO POR CAUSALES (CON FILTRO DE RIESGO)
st.markdown("### 🚦 Matriz de Semaforización de Riesgo Financiero por Causales de Glosa")
st.markdown("Clasificación de riesgo basada en el valor acumulado de glosas por causal (🔴 Alto > $233M, 🟡 Medio $10M - $233M, 🟢 Bajo < $10M).")

df_semaforo = df_filtrado.groupby('Causal_Estandarizada')['Valor_Glosa_Dev'].sum().reset_index()

def asignar_riesgo_y_color(valor):
    if valor > 233000000:
        return "Alto (Rojo)", "🔴"
    elif valor >= 10000000:
        return "Medio (Amarillo)", "🟡"
    else:
        return "Bajo (Verde)", "🟢"

res_riesgo = df_semaforo['Valor_Glosa_Dev'].apply(asignar_riesgo_y_color)
df_semaforo['Nivel de Riesgo'] = [r[0] for r in res_riesgo]
df_semaforo['Semaforo'] = [r[1] for r in res_riesgo]

# Filtro interactivo local para la matriz de semaforización
filtro_riesgo_sel = st.selectbox(
    "Filtrar Matriz por Nivel de Riesgo",
    ["Todos", "Alto (Rojo)", "Medio (Amarillo)", "Bajo (Verde)"]
)

if filtro_riesgo_sel != "Todos":
    df_semaforo = df_semaforo[df_semaforo['Nivel de Riesgo'] == filtro_riesgo_sel]

df_semaforo = df_semaforo.sort_values(by='Valor_Glosa_Dev', ascending=False)
df_semaforo['Valor_Glosa_Dev'] = df_semaforo['Valor_Glosa_Dev'].map('${:,.0f}'.format)

st.dataframe(
    df_semaforo[['Semaforo', 'Causal_Estandarizada', 'Nivel de Riesgo', 'Valor_Glosa_Dev']],
    use_container_width=True,
    hide_index=True
)
