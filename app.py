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

# --- BARRA LATERAL (FILTROS GLOBALES E INTERACTIVOS) ---
st.sidebar.header("🔍 Filtros Globales del Tablero")

df_base = df[df['item_repetido'] == False].copy()

# 1. Filtro por Tipología (Interactivo en cascada)
tipologias = ["Todas"] + list(df_base['tipologia'].unique())
tipologia_sel = st.sidebar.selectbox("Seleccione Tipología", tipologias)

# 2. Filtro de Fecha de Atención amigable y fácil de limpiar
st.sidebar.subheader("📅 Rango de Fechas de Atención")
usar_filtro_fecha = st.sidebar.checkbox("Activar filtro por fechas de atención", value=False)

f_inicio, f_fin = None, None
if usar_filtro_fecha:
    min_f = df_base['Fecha_Atencion'].min().date()
    max_f = df_base['Fecha_Atencion'].max().date()
    rango_f = st.sidebar.date_input("Seleccione rango", value=(min_f, max_f), min_value=min_f, max_value=max_f)
    if len(rango_f) == 2:
        f_inicio, f_fin = rango_f

# 3. Filtro por Causal Estandarizada
causales = ["Todas"] + list(df_base['Causal_Estandarizada'].unique())
causal_sel = st.sidebar.selectbox("Seleccione Causal Estandarizada", causales)

# --- APLICAR FILTROS GLOBALES EN CASCADA A TODO EL DASHBOARD ---
df_filtrado = df_base.copy()

if tipologia_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['tipologia'] == tipologia_sel]

if causal_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Causal_Estandarizada'] == causal_sel]

if usar_filtro_fecha and f_inicio and f_fin:
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha_Atencion'].dt.date >= f_inicio) & 
        (df_filtrado['Fecha_Atencion'].dt.date <= f_fin)
    ]

# --- CUERPO PRINCIPAL ---
st.title("📊 Tablero Gerencial: Analítica de Glosas")
st.subheader("S.O. Servicios Médicos Oftalmológicos (Bogotá)")
st.markdown("---")

# 1. TARJETAS DE MÉTRICAS (KPIs Interactivos)
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

# 3. EVOLUCIÓN TEMPORAL Y TOP 10 SERVICIOS CON MAYOR AFECTACIÓN
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

# 4. MATRIZ DE SEMAFORIZACIÓN DE RIESGO FINANCIERO POR CAUSALES (CON TOTALES)
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

if not df_semaforo.empty:
    res_riesgo = df_semaforo['Valor_Glosa_Dev'].apply(asignar_riesgo_y_color)
    df_semaforo['Nivel de Riesgo'] = [r[0] for r in res_riesgo]
    df_semaforo['Semaforo'] = [r[1] for r in res_riesgo]
    
    # Guardar la suma total antes de formatear como texto
    suma_total_glosas = df_semaforo['Valor_Glosa_Dev'].sum()
    
    df_semaforo = df_semaforo.sort_values(by='Valor_Glosa_Dev', ascending=False)
    df_semaforo['Valor_Glosa_Dev'] = df_semaforo['Valor_Glosa_Dev'].map('${:,.0f}'.format)
    
    # Agregar fila de totales
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
