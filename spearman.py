import pandas as pd
from scipy import stats

# 1. Cargar TU base de datos final (V6_4)
archivo = 'dataset_analisis_powerbi_FINAL_V6_4.xlsx'
df = pd.read_excel(archivo)

# 2. Aplicar las reglas de exclusión de tu tesis
df_clean = df[df['Numero_Factura'] != 'FE310107'].copy() # Aislar factura atípica
df_depurado = df_clean[df_clean['item_repetido'] == False].copy() # Solo ítems reales

# 3. Formato de fecha
df_depurado['Fecha_Hora_Radicacion'] = pd.to_datetime(df_depurado['Fecha_Hora_Radicacion'])

# 4. Dividir en los dos semestres analizados
p1 = df_depurado[(df_depurado['Fecha_Hora_Radicacion'].dt.year == 2025) & 
                 (df_depurado['Fecha_Hora_Radicacion'].dt.month >= 9) & 
                 (df_depurado['Fecha_Hora_Radicacion'].dt.month <= 12)]

p2 = df_depurado[(df_depurado['Fecha_Hora_Radicacion'].dt.year == 2026) & 
                 (df_depurado['Fecha_Hora_Radicacion'].dt.month >= 1) & 
                 (df_depurado['Fecha_Hora_Radicacion'].dt.month <= 7)]

# 5. Agrupar el Valor Depurado Real por Causales Estandarizadas
v1_causal = p1.groupby('Causal_Estandarizada')['Valor_Glosa_Dev'].sum().rename('Valor_P1')
v2_causal = p2.groupby('Causal_Estandarizada')['Valor_Glosa_Dev'].sum().rename('Valor_P2')
df_causales = pd.concat([v1_causal, v2_causal], axis=1).fillna(0)

# 6. Calcular el Coeficiente de Spearman
rho, p_val = stats.spearmanr(df_causales['Valor_P1'], df_causales['Valor_P2'])

print("\n========================================================")
print(" RESULTADO FINAL: ESTABILIDAD TEMPORAL (SPEARMAN)")
print("========================================================")
print(f"• Spearman (ρ) real de la base V6_4 : {rho:.4f}")
print(f"• Valor p real                      : {p_val:.4e}")
print("========================================================")
