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

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros del Reporte")

# Selector de Modo de Datos (Depurado vs Bruto)
modo_datos = st.sidebar.radio(
    "Tipo de Datos",
    ["Depurado (Recomendado - Excluye duplicados)", "En Bruto (Todos los registros)"]
)

# Aplicar filtro de depuración basado en la columna 'item_repetido' del Power BI
if "Depurado" in modo_datos:
    df_base = df[df['item_repetido'] == False].copy()
else:
    df_base = df.copy()

# Filtro por Tipología
tipologias = ["Todas"] + list(df_base['tipologia'].unique())
tipologia_sel = st.sidebar.selectbox("Seleccione Tipología", tipologias)

# Filtro por Causal Estandarizada
causales = ["Todas"] + list(df_base['Causal_Estandarizada'].unique())
causal_sel = st.sidebar.selectbox("Seleccione Causal Estandarizada", causales)

# Aplicar filtros interactivos
df_filtrado = df_base.copy()
if tipologia_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['tipologia'] == tipologia_sel]
if causal_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Causal_Estandarizada'] == causal_sel]

# --- CUERPO PRINCIPAL ---
st.title("📊 Análisis Gerencial: Analítica de Glosas")
st.subheader("S.O. Servicios Médicos Oftalmológicos (Bogotá)")
st.markdown("---")

# 1. TARJETAS DE MÉTRICAS (KPIs)
total_facturado = df_filtrado['Valor_Total_Factura'].sum()
total_glosado = df_filtrado['Valor_Glosa_Dev'].sum()
porcentaje_glosa = (total_glosado / total_facturado * 100) if total_facturado > 0 else 0
total_registros = len(df_filtrado)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Facturado", f"${total_facturado:,.0f}")
with col2:
    st.metric("Valor Depurado / Glosado", f"${total_glosado:,.0f}")
with col3:
    st.metric("% Impacto Depurado", f"{porcentaje_glosa:.2f}%")
with col4:
    st.metric("Registros Analizados", f"{total_registros:,}")

st.markdown("---")

# 2. GRÁFICOS PRINCIPALES
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("### 📌 Glosas por Tipología")
    df_tipologia = df_filtrado.groupby('tipologia')['Valor_Glosa_Dev'].sum().reset_index()
    fig_tip = px.bar(
        df_tipologia, 
        x='tipologia', 
        y='Valor_Glosa_Dev', 
        text_auto='.2s',
        color='tipologia',
        labels={'tipologia': 'Tipología', 'Valor_Glosa_Dev': 'Valor Glosado ($)'}
    )
    fig_tip.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_tip, use_container_width=True)

with col_g2:
    st.markdown("### ⚠️ Top 5 Causales Estandarizadas")
    df_causal = df_filtrado.groupby('Causal_Estandarizada')['Valor_Glosa_Dev'].sum().reset_index()
    df_causal = df_causal.sort_values(by='Valor_Glosa_Dev', ascending=False).head(5)
    fig_causal = px.bar(
        df_causal, 
        y='Causal_Estandarizada', 
        x='Valor_Glosa_Dev', 
        orientation='h',
        text_auto='.2s',
        labels={'Causal_Estandarizada': 'Causal Estandarizada', 'Valor_Glosa_Dev': 'Valor Glosado ($)'}
    )
    fig_causal.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_causal, use_container_width=True)

st.markdown("---")

# 3. EVOLUCIÓN TEMPORAL Y SERVICIOS
col_g3, col_g4 = st.columns(2)

with col_g3:
    st.markdown("### 📈 Tendencia de Glosas en el Tiempo")
    if not df_filtrado.empty and 'Fecha_Hora_Radicacion' in df_filtrado.columns:
        # Agrupamiento robusto por mes y año para evitar errores de resample en Streamlit Cloud
        df_temp = df_filtrado.copy()
        df_temp['Periodo'] = df_temp['Fecha_Hora_Radicacion'].dt.to_period('M').astype(str)
        df_temp_grouped = df_temp.groupby('Periodo')['Valor_Glosa_Dev'].sum().reset_index()
        
        fig_temp = px.line(
            df_temp_grouped, 
            x='Periodo', 
            y='Valor_Glosa_Dev',
            markers=True,
            labels={'Periodo': 'Mes de Radicación', 'Valor_Glosa_Dev': 'Valor Glosado ($)'}
        )
        fig_temp.update_layout(xaxis_tickangle=-45, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_temp, use_container_width=True)
    else:
        st.info("No hay datos suficientes para la tendencia temporal.")

with col_g4:
    st.markdown("### 👁️ Servicios con Mayor Afectación")
    df_serv = df_filtrado.groupby('Nombre del servicio ')['Valor_Glosa_Dev'].sum().reset_index()
    df_serv = df_serv.sort_values(by='Valor_Glosa_Dev', ascending=False).head(5)
    fig_serv = px.bar(
        df_serv,
        x='Valor_Glosa_Dev',
        y='Nombre del servicio ',
        orientation='h',
        text_auto='.2s',
        labels={'Nombre del servicio ': 'Servicio', 'Valor_Glosa_Dev': 'Valor Glosado ($)'}
    )
    fig_serv.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_serv, use_container_width=True)

st.markdown("---")

# 4. TABLA DETALLADA DE DATOS
st.markdown("### 📋 Detalle de Registros Filtrados")
columnas_mostrar = [
    'Numero_Radicacion', 'Numero_Factura', 'Valor_Total_Factura', 
    'Fecha_Atencion', 'Valor_Glosa_Dev', 'tipologia', 'Causal_Estandarizada', 'Nombre del servicio ', 'item_repetido'
]
st.dataframe(df_filtrado[columnas_mostrar], use_container_width=True)
