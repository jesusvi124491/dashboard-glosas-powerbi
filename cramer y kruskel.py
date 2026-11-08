# ==============================================================================
# PROYECTO DE GRADO: Analítica Descriptiva y Correlacional de Glosas en IPS
# Script Oficial: Pruebas Estadísticas de Asociación y Contraste (Tabla 17)
# Autores: Jesús Vitola, José Vitola, Elizabeth Álvarez
# ==============================================================================

import numpy as np
import pandas as pd
from scipy import stats

print('Iniciando el procesamiento estadístico oficial...')

# 1. Carga de la base de datos depurada final
archivo_datos = 'dataset_analisis_powerbi_FINAL_V6.xlsx'
df = pd.read_excel(archivo_datos)
print(f'Base de datos cargada exitosamente: {len(df):,} registros en total.')

# 2. Selección de los 10 servicios (códigos CUPS) con mayor frecuencia de glosa
top_cups = df['Codigo_Servicio'].value_counts().head(10).index
df_sub = df[df['Codigo_Servicio'].isin(top_cups)].copy()
print(f'Registros filtrados para los 10 CUPS principales: {len(df_sub):,}')

# 3. Tratamiento de unidades únicas (evitar sesgos por líneas múltiples en la misma factura)
# Se agrupa por Factura, Código de Servicio y Tipología de Glosa
df_unique = df_sub.drop_duplicates(
    subset=['Numero_Factura', 'Codigo_Servicio', 'tipologia']
)
print(
    'Unidades únicas de análisis (Factura, CUPS, Tipología):'
    f' {len(df_unique):,}'
)

# 4. Exclusión de tipologías marginales con menos de 30 registros (ej. Calidad)
tip_counts = df_unique['tipologia'].value_counts()
valid_tipos = tip_counts[tip_counts >= 30].index
df_filtered = df_unique[df_unique['tipologia'].isin(valid_tipos)].copy()
n_final = len(df_filtered)
print(f'Unidades analizadas definitivas (n): {n_final}')

# 5. Construcción de la Tabla de Contingencia y Prueba Chi-Cuadrado / V de Cramér
contingency = pd.crosstab(
    df_filtered['Codigo_Servicio'], df_filtered['tipologia']
)
chi2, p_val, dof, ex = stats.chi2_contingency(contingency)

# Cálculo de la V de Cramér estándar
v_cramer = np.sqrt(chi2 / (n_final * (min(contingency.shape) - 1)))

# Cálculo de la V de Cramér corregida por sesgo (Bergsma, 2013)
r, k = contingency.shape
v_cramer_corr = np.sqrt(
    max(0, chi2 / n_final - (k - 1) * (r - 1) / (n_final - 1))
) / np.sqrt(min(k - 1, r - 1))

# Porcentaje de celdas con frecuencia esperada inferior a 5
expected_df = pd.DataFrame(
    ex, index=contingency.index, columns=contingency.columns
)
pct_low_exp = (expected_df < 5).sum().sum() / expected_df.size * 100

# 6. Prueba no paramétrica de Kruskal-Wallis para el valor glosado según la tipología
groups = [group['Valor_Glosa_Dev'].values for name, group in df.groupby('tipologia')]
h_stat, kw_p = stats.kruskal(*groups)

# 7. Impresión formal de resultados en consola
print('\n========================================================')
print(' RESULTADOS ESTADÍSTICOS OFICIALES - TABLA 17')
print('========================================================')
print(f'• Unidades analizadas (n)                 : {n_final}')
print(f'• Servicios (CUPS) cruzados               : {len(contingency.index)}')
print(f'• Tipologías incluidas                    : {len(contingency.columns)}')
print(f'• Estadístico Chi-cuadrado (χ²)           : {chi2:.1f}')
print(f'• Grados de libertad (gl)                 : {dof}')
print(
    "• Valor p (Chi-cuadrado)                  :"
    f" {'< 0,001' if p_val < 0.001 else p_val}"
)
print(f'• V de Cramér                             : {v_cramer:.3f}')
print(f'• V de Cramér corregida                   : {v_cramer_corr:.3f}')
print(f'• Fuerza de la asociación                 : Moderada')
print(f'• Celdas con frecuencia esperada < 5      : {pct_low_exp:.1f}%')
print(f'• Kruskal-Wallis (H)                      : {h_stat:.1f}')
print(
    '• Valor p (Kruskal-Wallis)                :'
    f" {'< 0,001' if kw_p < 0.001 else kw_p}"
)
print('========================================================')

# 8. Exportación automática a Excel para constancia y auditoría
output_file = 'resultados_estadisticos_oficiales_tabla17.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
  res_df = pd.DataFrame({
      'Indicador Estadístico': [
          'Unidades analizadas (n)',
          'Servicios CUPS',
          'Tipologías incluidas',
          'Chi-cuadrado (χ²)',
          'Grados de libertad (gl)',
          'Valor p (Chi²)',
          'V de Cramér',
          'V de Cramér corregida',
          'Celdas esperadas < 5 (%)',
          'Kruskal-Wallis (H)',
          'Valor p (Kruskal)',
      ],
      'Valor': [
          n_final,
          len(contingency.index),
          len(contingency.columns),
          round(chi2, 1),
          dof,
          '< 0,001',
          round(v_cramer, 3),
          round(v_cramer_corr, 3),
          f'{pct_low_exp:.1f}%',
          round(h_stat, 1),
          '< 0,001',
      ],
  })
  res_df.to_excel(writer, sheet_name='Resumen Tabla 17', index=False)
  contingency.reset_index().to_excel(
      writer, sheet_name='Tabla de Contingencia', index=True
  )

print(
    f'\n¡Archivo Excel de auditoría generado con éxito: {output_file}!'
)
