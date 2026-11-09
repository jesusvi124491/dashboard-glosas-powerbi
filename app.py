import streamlit as st
import textwrap
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
    st.session_state.codigos_sel = []
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
st.markdown('<div class="main-title">📊 Tablero Gerencial: Analítica de Glosas</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-banner">S.O. Servicios Médicos Oftalmológicos (Bogotá)</div>', unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# --- PANEL DE FILTROS INTERACTIVOS ---
# ==========================================
st.markdown("### 🎛️ Filtros Interactivos del Tablero")

# Fila 1 de filtros
col_f1, col_f2, col_f3, col_f7 = st.columns(4)

with col_f1:
    tipologias_disp = ["Todas"] + list(df_base['tipologia'].unique())
    tipologia_sel = st.selectbox("📌 Filtrar por Tipología", tipologias_disp, key='tipologia_sel')

with col_f2:
    causales_disp = ["Todas"] + list(df_base['Causal_Estandarizada'].unique())
    causal_sel = st.selectbox("⚠️ Filtrar por Causal Estandarizada", causales_disp, key='causal_sel')

with col_f3:
    riesgo_disp = ["Todos", "Alto (Rojo)", "Medio (Amarillo)", "Bajo (Verde)"]
    riesgo_sel = st.selectbox("🚦 Filtrar por Nivel de Riesgo (Semáforo)", riesgo_disp, key='riesgo_sel')

with col_f7:
    codigos_disp = sorted(df['Codigo_Glosa_Dev'].dropna().astype(str).unique())
    codigos_sel = st.multiselect("🔢 Filtrar por Código de Glosa", options=codigos_disp, key='codigos_sel')

# Fila 2 de filtros (Servicios y Fechas)
col_f4, col_f5, col_f6 = st.columns(3)

with col_f4:
    servicios_disp = list(df_base['Nombre del servicio '].unique())
    servicios_sel = st.multiselect("👁️ Filtrar Servicios Específicos", options=servicios_disp, key='servicios_sel')

with col_f5:
    st.markdown("📅 **Rango de Fecha de Atención**")
    sub_fa1, sub_fa2 = st.columns([4, 1])
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
        if st.button("🔄", key="btn_reset_at", help="Restablecer Fecha de Atención"):
            st.session_state.trigger_reset_at = True
            st.rerun()

with col_f6:
    st.markdown("📈 **Rango de Fecha de Radicación**")
    sub_fr1, sub_fr2 = st.columns([4, 1])
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
        if st.button("🔄", key="btn_reset_rad", help="Restablecer Fecha de Radicación"):
            st.session_state.trigger_reset_rad = True
            st.rerun()

# Botón de Restablecimiento Global centrado justo después del último filtro
st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([3, 4, 3])
with col_btn2:
    if st.button("🔄 Restablecer Todos los Filtros (Global)", use_container_width=True):
        st.session_state.trigger_reset_global = True
        st.rerun()

st.markdown("---")

# ==========================================
# --- APLICAR FILTROS EN CASCADA A TODO EL DATASET ---
# ==========================================
def asignar_riesgo_y_color(valor):
    if valor > 233000000:
        return "Alto (Rojo)", "🔴"
    elif valor >= 10000000:
        return "Medio (Amarillo)", "🟡"
    else:
        return "Bajo (Verde)", "🟢"


def aplicar_filtros(base):
    """Aplica en cascada los filtros del tablero a cualquier base (depurada o completa)."""
    d = base.copy()

    if st.session_state.get('tipologia_sel', 'Todas') != "Todas":
        d = d[d['tipologia'] == st.session_state.tipologia_sel]

    if st.session_state.get('causal_sel', 'Todas') != "Todas":
        d = d[d['Causal_Estandarizada'] == st.session_state.causal_sel]

    if st.session_state.get('codigos_sel', []):
        d = d[d['Codigo_Glosa_Dev'].astype(str).isin(st.session_state.codigos_sel)]

    if st.session_state.get('servicios_sel', []):
        d = d[d['Nombre del servicio '].isin(st.session_state.servicios_sel)]

    if 'widget_rango_atencion' in st.session_state and len(st.session_state.widget_rango_atencion) == 2:
        f_ini, f_fin = st.session_state.widget_rango_atencion
        d = d[
            (d['Fecha_Atencion'].dt.date >= f_ini) &
            (d['Fecha_Atencion'].dt.date <= f_fin)
        ]

    if 'widget_rango_radicacion' in st.session_state and len(st.session_state.widget_rango_radicacion) == 2:
        r_ini, r_fin = st.session_state.widget_rango_radicacion
        d = d[
            (d['Fecha_Hora_Radicacion'].dt.date >= r_ini) &
            (d['Fecha_Hora_Radicacion'].dt.date <= r_fin)
        ]

    if st.session_state.get('riesgo_sel', 'Todos') != "Todos":
        causales_riesgo = d.groupby('Causal_Estandarizada')['Valor_Glosa_Dev'].sum().reset_index()
        causales_riesgo['Nivel'] = causales_riesgo['Valor_Glosa_Dev'].apply(lambda x: asignar_riesgo_y_color(x)[0])
        causales_validas = causales_riesgo[causales_riesgo['Nivel'] == st.session_state.riesgo_sel]['Causal_Estandarizada'].tolist()
        d = d[d['Causal_Estandarizada'].isin(causales_validas)]

    return d


df_filtrado = aplicar_filtros(df_base)


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
# --- 4. % FRECUENCIA DE GLOSA POR CÓDIGO (TOP 10) ---
# ==========================================
# Réplica de la medida DAX:
#   % Frecuencia de Glosa = DIVIDE(COUNTROWS(Sheet1), CALCULATE(COUNTROWS(Sheet1), ALL(Sheet1)), 0)
# El denominador (ALL) ignora todo filtro: siempre es el total de filas del dataset completo.
st.markdown("### 🍩 % Frecuencia de Glosa por Código de Glosa (Top 10)")

# Base completa (incluye ítems repetidos), igual que el informe de Power BI.
df_freq_base = aplicar_filtros(df)
total_filas_all = len(df)  # equivale a ALL('Sheet1')

if not df_freq_base.empty and total_filas_all > 0:
    df_freq = (
        df_freq_base.groupby('Codigo_Glosa_Dev')
        .size()
        .reset_index(name='Filas')
        .sort_values('Filas', ascending=False)
        .head(10)
    )
    df_freq['Pct'] = df_freq['Filas'] / total_filas_all * 100  # DIVIDE(..., 0)
    pct_top10 = df_freq['Pct'].sum()

    def fmt_pct(x, dec=2):
        return f"{x:.{dec}f}".replace(".", ",") + "%"

    fig_freq = go.Figure(go.Pie(
        labels=df_freq['Codigo_Glosa_Dev'].astype(str),
        values=df_freq['Pct'],
        hole=0.7,
        sort=False,
        direction='clockwise',
        text=[fmt_pct(p) for p in df_freq['Pct']],
        textinfo='text',
        textposition='outside',
        customdata=df_freq[['Filas', 'Pct']].values,
        hovertemplate="<b>%{label}</b><br>Filas: %{customdata[0]:,.0f}"
                      "<br>% Frecuencia de Glosa: %{customdata[1]:.2f}%<extra></extra>",
        marker=dict(line=dict(color="white", width=2))
    ))
    fig_freq.update_layout(
        margin=dict(t=30, b=30, l=30, r=30),
        height=480,
        legend=dict(title="Código de Glosa", orientation="v", y=0.5),
        annotations=[dict(
            text=f"<b>{fmt_pct(pct_top10).replace('%', ' %')}</b>",
            x=0.5, y=0.5, showarrow=False, font=dict(size=28)
        )]
    )
    st.plotly_chart(fig_freq, use_container_width=True)
    st.caption(
        f"Cada porcentaje = filas con ese código ÷ {total_filas_all:,} filas totales. "
        f"El centro muestra la suma del Top 10."
    )
else:
    st.info("ℹ️ No hay registros disponibles con los filtros seleccionados.")

st.markdown("---")

# ==========================================
# --- 5. ASOCIACIÓN SERVICIO–TIPOLOGÍA (TOP 10 SERVICIOS) ---
# ==========================================
# Réplica de la Figura 9 del trabajo (sección 8.4.3): tipología de la glosa en los diez servicios (CUPS)
# con más unidades únicas de factura–CUPS–tipología. Se calcula sobre la base de análisis completa y
# NO cambia con los filtros del tablero (igual que en el documento).
st.markdown("### 🔗 Asociación Servicio–Tipología (Top 10 servicios más frecuentes)")
st.markdown("Distribución porcentual de la tipología de la glosa dentro de cada servicio (CUPS). "
            "Una barra con un color dominante indica que ese servicio se glosa sobre todo por ese motivo.")

ORDEN_TIPOLOGIAS = ['Autorizaciones', 'Devoluciones', 'Facturación', 'Soportes', 'Tarifas']
COLORES_TIPOLOGIA = {
    'Autorizaciones': '#FF9E1B', 'Devoluciones': '#8A94A6', 'Facturación': '#91DC00',
    'Soportes': '#0C2340', 'Tarifas': '#3553C8'
}

# Mismo procedimiento del script oficial (Tabla 17 / Figura 9):
# 1) Top 10 CUPS por frecuencia de registros en la base de análisis completa
# 2) Unidad única = (factura, CUPS, tipología)
# 3) Se excluye 'Calidad' (< 30 unidades)
top_cups = df['Codigo_Servicio'].value_counts().head(10).index.tolist()
df_asoc = (
    df[df['Codigo_Servicio'].isin(top_cups)]
    .drop_duplicates(['Numero_Factura', 'Codigo_Servicio', 'tipologia'])
)
df_asoc = df_asoc[df_asoc['tipologia'].isin(ORDEN_TIPOLOGIAS)]
df_top = df_asoc[df_asoc['Codigo_Servicio'].isin(top_cups)]

if not df_top.empty:
    tabla_asoc = pd.crosstab(df_top['Codigo_Servicio'], df_top['tipologia'])
    tabla_asoc = tabla_asoc.reindex(index=top_cups, columns=ORDEN_TIPOLOGIAS, fill_value=0)
    tabla_pct = tabla_asoc.div(tabla_asoc.sum(axis=1), axis=0) * 100

    nombres = (df.drop_duplicates('Codigo_Servicio')
                 .set_index('Codigo_Servicio')['Nombre del servicio ']
                 .astype(str).str.strip().str.title())

    def etiqueta(c):
        n = nombres.get(c, '')
        # Nombre completo, partido en líneas de ~38 caracteres para que no se corte
        return f"{c} · " + "<br>".join(textwrap.wrap(n, 38)) if n else str(c)

    largo = tabla_pct.reset_index().melt(id_vars='Codigo_Servicio', var_name='Tipología', value_name='Porcentaje')
    largo['Servicio'] = largo['Codigo_Servicio'].map(etiqueta)
    largo['Unidades'] = [int(tabla_asoc.loc[c, t]) for c, t in zip(largo['Codigo_Servicio'], largo['Tipología'])]
    largo['Texto'] = largo['Porcentaje'].apply(lambda v: f"{v:.0f}%" if v >= 7 else "")

    fig_asoc = px.bar(
        largo, x='Porcentaje', y='Servicio', color='Tipología', orientation='h',
        category_orders={'Tipología': ORDEN_TIPOLOGIAS, 'Servicio': [etiqueta(c) for c in top_cups]},
        color_discrete_map=COLORES_TIPOLOGIA, text='Texto',
        custom_data=['Unidades'],
        labels={'Porcentaje': '% de las glosas del servicio'}
    )
    fig_asoc.update_traces(
        textposition='inside', insidetextanchor='middle',
        hovertemplate="<b>%{y}</b><br>%{fullData.name}: %{x:.1f}% (%{customdata[0]} unidades)<extra></extra>"
    )
    fig_asoc.update_layout(
        barmode='stack', height=640, margin=dict(t=40, b=40, l=20, r=20),
        yaxis=dict(autorange='reversed', title='', automargin=True, tickfont=dict(size=11)),
        xaxis=dict(range=[0, 100], ticksuffix='%'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0, title_text='')
    )
    st.plotly_chart(fig_asoc, use_container_width=True)

    st.caption("Réplica de la Figura 9 del trabajo (sección 8.4.3). Unidades únicas de factura, CUPS y tipología; "
               "no cambia con los filtros del tablero.")

    with st.expander("Ver tabla de frecuencias (unidades por servicio y tipología)"):
        tabla_vista = tabla_asoc.copy()
        tabla_vista['Total'] = tabla_vista.sum(axis=1)
        tabla_vista.index = [etiqueta(c).replace('<br>', ' ') for c in tabla_vista.index]
        tabla_vista.index.name = 'Servicio (CUPS)'
        st.dataframe(tabla_vista, use_container_width=True)
else:
    st.info("ℹ️ No hay datos suficientes para la asociación servicio–tipología.")

st.markdown("---")

# ==========================================
# --- 6. MATRIZ DE SEMAFORIZACIÓN DE RIESGO FINANCIERO ---
# ==========================================
st.markdown("### 🚦 Matriz de Semaforización de Riesgo Financiero por Causales de Glosa")
st.markdown("Clasificación de riesgo basada en el valor acumulado de glosas por causal (🔴 Alto > $233M, 🟡 Medio $10M - $233M, 🟢 Bajo < $10M).")

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
    st.info("ℹ️ No hay registros de glosas disponibles con los filtros seleccionados.") 
