import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Explorador de Aleaciones MPEA", layout="wide")
st.title("Análisis de Aleaciones MPEA para Descensores de Cañonismo")

@st.cache_data
def load_data():
    df = pd.read_csv('MPEA_dataset - MPEA_dataset.csv')
    cols_map = {
        'FORMULA': 'Formula',
        'PROPERTY: Microstructure': 'Microestructura',
        'PROPERTY: Processing method': 'Procesamiento',
        'PROPERTY: BCC/FCC/other': 'Estructura',
        r'PROPERTY: Calculated Density (g/cm$^3$)': 'Densidad_calc',
        'PROPERTY: HV': 'HV',
        'PROPERTY: Type of test': 'Tipo_ensayo',
        r'PROPERTY: Test temperature ($^\circ$C)': 'Temp_C',
        'PROPERTY: YS (MPa)': 'YS',
        'PROPERTY: Elongation (%)': 'Elongacion'
    }
    df_clean = df.rename(columns=cols_map).copy()
    df_rt = df_clean[(df_clean['Temp_C'] >= 20) & (df_clean['Temp_C'] <= 30)].copy()
    df_rt['YS_Especifico'] = df_rt['YS'] / df_rt['Densidad_calc']
    return df_rt.dropna(subset=['HV', 'YS', 'Densidad_calc', 'Elongacion'])

df = load_data()

# Barra lateral para filtros interactivos
st.sidebar.header("Filtros de Diseño")
min_hv = st.sidebar.slider("Dureza Mínima (HV)", int(df['HV'].min()), int(df['HV'].max()), 300)
min_ys_esp = st.sidebar.slider("YS Específico Mínimo (MPa·cm³/g)", int(df['YS_Especifico'].min()), int(df['YS_Especifico'].max()), 150)
min_elong = st.sidebar.slider("Elongación Mínima (%)", 0, int(df['Elongacion'].max()), 12)

# Aplicar filtros
df_filtered = df[(df['HV'] >= min_hv) & (df['YS_Especifico'] >= min_ys_esp) & (df['Elongacion'] >= min_elong)]

st.subheader(f"Aleaciones candidatas encontradas: {len(df_filtered)}")
st.dataframe(df_filtered[['Formula', 'Estructura', 'Procesamiento', 'Densidad_calc', 'HV', 'YS_Especifico', 'Elongacion']])

# Gráfico interactivo con Matplotlib/Seaborn
st.subheader("Mapa de Selección de Materiales: Dureza vs YS Específico")
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=df, x='HV', y='YS_Especifico', hue='Estructura', size='Elongacion', sizes=(20, 200), alpha=0.5, ax=ax)
sns.scatterplot(data=df_filtered, x='HV', y='YS_Especifico', color='red', marker='X', s=100, label='Candidatas', ax=ax)
ax.axvline(175, color='gray', linestyle='--', label='Al 7075-T6 (Desgaste)')
ax.axhline(179, color='green', linestyle='--', label='Al 7075-T6 (Eficiencia)')
ax.set_xlabel('Dureza Vickers, HV')
ax.set_ylabel('Límite Elástico Específico, YS/ρ')
ax.legend()
st.pyplot(fig)
