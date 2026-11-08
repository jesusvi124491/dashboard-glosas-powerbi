# ==========================================
# PROYECTO DE GRADO: Analítica de Glosas IPS
# Autores: Jesús Vitola, José Vitola, Elizabeth Álvarez
# Descripción: Script de ETL - Limpieza Definitiva con Tipologías y Descripciones Oficiales (V6 FINAL)
# ==========================================

import pandas as pd
import numpy as np

print("Iniciando el proceso de limpieza y preparación de datos...")

# 1. CARGA DE DATOS ORIGINALES
archivo_entrada = "data_glosas (2).xlsx"
print(f"Cargando {archivo_entrada}...")
df = pd.read_excel(archivo_entrada)
df_clean = df.copy()

# ==============================================================================
# 2. IMPUTACIONES BASE Y ESTANDARIZACIÓN (Fechas y Servicios)
# ==============================================================================
print("Limpiando textos 'UTC' y estandarizando fechas...")
for col in ['Fecha_Hora_Radicacion', 'Fecha_Hora_Glosa', 'Fecha_Atencion']:
    df_clean[col] = df_clean[col].astype(str).str.replace(' UTC', '', regex=False)
    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce').dt.tz_localize(None)

# Tratamiento de nulos en Código de Servicio (imputar con la moda)
moda_servicio = df_clean['Codigo_Servicio'].mode()[0]
df_clean['Codigo_Servicio'] = df_clean['Codigo_Servicio'].fillna(moda_servicio)

# Tratamiento de nulos en Fecha de Atención (ordenamiento y ffill/bfill)
df_clean = df_clean.sort_values(by='Fecha_Hora_Radicacion')
df_clean['Fecha_Atencion'] = df_clean['Fecha_Atencion'].bfill().ffill()

# Unificación de nombres de servicios 
print("Unificando nombres de servicios y etiquetando los desconocidos...")
col_nombre = [c for c in df_clean.columns if 'Nombre' in c and 'servicio' in c.lower()][0]
diccionario_nombres = df_clean.dropna(subset=[col_nombre]).drop_duplicates('Codigo_Servicio').set_index('Codigo_Servicio')[col_nombre].to_dict()
df_clean[col_nombre] = df_clean[col_nombre].fillna(df_clean['Codigo_Servicio'].map(diccionario_nombres)).fillna('Servicio interno no especificado')

# ==============================================================================
# 3. DICCIONARIO MAESTRO OFICIAL (Resolución 2284 de 2023)
# ==============================================================================
print("Mapeando códigos oficiales de glosa a tipologías y descripciones normativas...")
maestro_glosas = {
    # SO - Soportes
    'SO2102': ('Soportes', 'El número de autorización incluido en el RIPS no corresponde al prestador de servicios de salud.'),
    'SO2104': ('Soportes', 'El número de autorización incluido en el RIPS no corresponde a la persona atendida.'),
    'SO4101': ('Soportes', 'Ausencia total, parcial o inconsistencia en la copia de la descripción quirúrgica.'),
    'SO0301': ('Soportes', 'Ausencia total, parcial o inconsistencia en los soportes de cobro de los honorarios profesionales en procedimientos quirúrgicos o intervencionistas.'),
    'SO2103': ('Soportes', 'El número de autorización incluido en el RIPS no corresponde al servicio o tecnología prestada o facturada.'),
    'SO0801': ('Soportes', 'Ausencia total, parcial o inconsistencia en los soportes de cobro que evidencian la práctica del apoyo diagnóstico.'),
    'SO2101': ('Soportes', 'El número de autorización no está incluido en el RIPS.'),
    'SO0201': ('Soportes', 'Ausencia total, parcial o inconsistencia en los soportes de cobro de consultas, interconsultas o atenciones domiciliarias.'),
    'SO6101': ('Soportes', 'Uno o varios campos del RIPS presentan inconsistencias con la atención prestada.'),
    'SO6102': ('Soportes', 'Uno o varios campos del RIPS presentan inconsistencias con relación al contrato.'),
    'SO3701': ('Soportes', 'Ausencia total, parcial o inconsistencia en la orden o prescripción facultativa del profesional tratante.'),
    'SO4701': ('Soportes', 'No se incluyen en la factura los soportes de los servicios o tecnologías sujetos a recobro ante la ADRES o la ARL.'),
    'SO3901': ('Soportes', 'Ausencia total, parcial o inconsistencia en el comprobante de recibido del usuario.'),

    # TA - Tarifas
    'TA0201': ('Tarifas', 'El cargo por consulta, interconsulta o atención domiciliaria presenta diferencias con los valores pactados o establecidos por la norma.'),
    'TA0801': ('Tarifas', 'Los cargos por apoyo diagnóstico presentan diferencias con los valores pactados o establecidos por la norma.'),
    'TA5801': ('Tarifas', 'Los cargos por procedimientos quirúrgicos o intervencionistas presentan diferencias con los valores pactados o establecidos por la norma.'),
    'TA0601': ('Tarifas', 'Los cargos por dispositivos médicos presentan diferencias con los valores pactados o establecidos por la norma.'),
    'TA0701': ('Tarifas', 'Los cargos por medicamentos o alimentos para propósitos médicos especiales (APME) presentan diferencias con los valores pactados o establecidos por la norma.'),
    'TA2301': ('Tarifas', 'Los cargos por otros procedimientos no quirúrgicos presentan diferencias con los valores pactados o establecidos por la norma.'),
    'TA2901': ('Tarifas', 'En la factura se adicionan cobros por recargos no pactados previamente entre las partes ni establecidos por la norma.'),

    # FA - Facturación
    'FA1605': ('Facturación', 'La persona corresponde a otro responsable de pago en el momento de la prestación del servicio.'),
    'FA1606': ('Facturación', 'En la factura se relacionan uno o varios servicios o tecnologías en salud que corresponden a otro responsable de pago.'),
    'FA2006': ('Facturación', 'Los recaudos efectivos de pagos compartidos, copagos o cuotas moderadoras efectuados por el prestador no corresponden a lo informado.'),
    'FA2702': ('Facturación', 'Se cobran servicios o tecnologías en salud que ya fueron cobrados dentro de la misma factura o en otra factura.'),
    'FA1905': ('Facturación', 'Los descuentos otorgados se aplicaron de manera diferente a lo pactado o no fueron aplicados.'),

    # AU - Autorizaciones
    'AU0202': ('Autorizaciones', 'La consulta, interconsulta o atención domiciliaria facturada no corresponde a la autorizada.'),
    'AU0602': ('Autorizaciones', 'Los dispositivos médicos facturados no corresponden a los autorizados, sin la debida justificación.'),
    'AU0601': ('Autorizaciones', 'El número de dispositivos médicos facturados presenta diferencias con lo autorizado, sin la debida justificación.'),
    'AU0702': ('Autorizaciones', 'La forma farmacéutica facturada presenta diferencias con la autorizada.'),
    'AU0302': ('Autorizaciones', 'Los honorarios profesionales relacionados en los soportes de la factura no corresponden a los autorizados.'),
    'AU0802': ('Autorizaciones', 'Los apoyos diagnósticos facturados no corresponden a los autorizados.'),
    'AU0201': ('Autorizaciones', 'El número de consultas, interconsultas o atenciones domiciliarias facturadas presenta diferencias con las autorizadas.'),
    'AU5802': ('Autorizaciones', 'Los procedimientos quirúrgicos o intervencionistas facturados no corresponden a los autorizados.'),
    'AU5801': ('Autorizaciones', 'El número de procedimientos quirúrgicos o intervencionistas facturados presenta diferencias con lo autorizado.'),
    'AU4303': ('Autorizaciones', 'La orden o prescripción del profesional tratante, o el número de autorización registrado, ha superado el límite de días de vigencia.'),

    # DE - Devoluciones
    'DE1601': ('Devoluciones', 'La factura corresponde a una persona que pertenecía a otro responsable de pago en el momento de la atención.'),
    'DE4401': ('Devoluciones', 'El profesional que ordenó el servicio o tecnología facturada lo hizo desde una IPS que no pertenece a la red integral.'),

    # CL - Calidad
    'CL0301': ('Calidad', 'Los cargos por honorarios profesionales en procedimientos quirúrgicos o intervencionistas, de hemodinamia, radiología u otros no son pertinentes.')
}

def obtener_info_glosa(codigo):
    if pd.isna(codigo):
        return ('Otro', 'No especificado')
    codigo_limpio = str(codigo).strip().upper()
    return maestro_glosas.get(codigo_limpio, ('Otro', str(codigo)))

# Aplicación del mapeo oficial
df_clean['tipologia'] = df_clean['Codigo_Glosa_Dev'].apply(lambda x: obtener_info_glosa(x)[0])
df_clean['Causal_Estandarizada'] = df_clean['Codigo_Glosa_Dev'].apply(lambda x: obtener_info_glosa(x)[1])

# ==============================================================================
# 4. ANONIMIZACIÓN OPCIONAL (Para Tooltips y auditoría del texto original)
# ==============================================================================
#df_clean['Causal_Agrupada'] = df_clean['Causal de Glosa'].astype(str)
#df_clean['Causal_Agrupada'] = df_clean['Causal_Agrupada'].str.replace(r'\b\d{5,}\b', '***', regex=True)
#df_clean['Causal_Agrupada'] = df_clean['Causal_Agrupada'].str.replace(r'\b[1-9][A-Z0-9]{10,}\b', '***', regex=True)
#df_clean['Causal_Agrupada'] = df_clean['Causal_Agrupada'].str.replace(r'\d{4}-\d{2}-\d{2}', '***', regex=True)
#df_clean['Causal_Agrupada'] = df_clean['Causal_Agrupada'].str.replace(r'\b\d+([.,]\d+)?\b', '***', regex=True)
#df_clean['Causal_Agrupada'] = df_clean['Causal_Agrupada'].str.replace(r'\s+', ' ', regex=True).str.strip()

# ==============================================================================
# 5. CONTROL FINANCIERO Y EXCLUSIÓN DE ATÍPICOS (Cálculo del Valor Depurado)
# ==============================================================================
print("Calculando ítems repetidos y depurando valores...")
df_clean['Valor_Glosa_Dev'] = pd.to_numeric(df_clean['Valor_Glosa_Dev'], errors='coerce')

# Subconjunto exacto para detectar la duplicación de los ítems glosados
columnas_identificadoras = ['Numero_Factura', 'Codigo_Servicio', 'Codigo_Glosa_Dev', 'Valor_Glosa_Dev', 'Fecha_Atencion']
df_clean['item_repetido'] = df_clean.duplicated(subset=columnas_identificadoras, keep='first')

# Exclusión de la factura atípica para mantener la base de análisis de 5.25 mil M
df_final = df_clean[df_clean['Numero_Factura'] != 'FE310107'].copy()

# ==============================================================================
# 6. EXPORTACIÓN A POWER BI
# ==============================================================================
archivo_salida = "dataset_analisis_powerbi_FINAL_V6.xlsx"
print(f"\nGuardando el archivo final limpio como {archivo_salida}...")
df_final.to_excel(archivo_salida, index=False)

# Resumen Financiero en consola para validar
valor_bruto = df_final['Valor_Glosa_Dev'].sum()
valor_depurado = df_final.loc[~df_final['item_repetido'], 'Valor_Glosa_Dev'].sum()
print(f"\nRESUMEN FINANCIERO:")
print(f"Valor Bruto Analizado: ${valor_bruto:,.2f}")
print(f"Valor Depurado Real: ${valor_depurado:,.2f}")
print("\n¡ETL finalizado con éxito! El modelo de datos usa codificación oficial y está 100% listo para Power BI.")
