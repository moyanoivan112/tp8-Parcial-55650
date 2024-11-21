import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Análisis de Ventas", layout="wide")

# Dirección de la aplicación publicada
# url = 'https://tp8-555555.streamlit.app/'

# Función para mostrar información del alumno
def mostrar_informacion_alumno():
    st.markdown("### Información del Alumno")
    st.markdown("**Legajo:** 55.555")
    st.markdown("**Nombre:** Juan Pérez")
    st.markdown("**Comisión:** C1")

# Mostrar información del alumno
mostrar_informacion_alumno()

st.title("Análisis de Ventas por Producto")

# Cargar archivo CSV
uploaded_file = st.file_uploader("Sube tu archivo CSV con los datos de ventas", type=["csv"])

if uploaded_file:
    # Leer los datos
    df = pd.read_csv(uploaded_file)

    # Validar columnas
    expected_columns = ["Sucursal", "Producto", "Año", "Mes", "Unidades_vendidas", "Ingreso_total", "Costo_total"]
    if all(column in df.columns for column in expected_columns):
        # Filtro por sucursal
        sucursal = st.selectbox("Selecciona una sucursal", options=["Todas"] + list(df["Sucursal"].unique()))
        if sucursal != "Todas":
            df = df[df["Sucursal"] == sucursal]

        # Cálculo de métricas por producto
        df_metrics = df.groupby("Producto").agg(
            Precio_promedio=("Ingreso_total", lambda x: x.sum() / df.loc[df["Producto"] == x.name, "Unidades_vendidas"].sum()),
            Margen_promedio=("Ingreso_total", lambda x: ((x.sum() - df.loc[df["Producto"] == x.name, "Costo_total"].sum()) / x.sum())),
            Unidades_vendidas=("Unidades_vendidas", "sum")
        ).reset_index()

        st.markdown("### Resumen por Producto")
        st.dataframe(df_metrics)

        # Gráfico de evolución de ventas
        st.markdown("### Evolución de Ventas Mensuales")
        #df["Fecha"] = pd.to_datetime(df[["Año", "Mes"]].assign(day=1))
        # Validar que Año y Mes contengan valores numéricos
        if not (df["Año"].dtype in [int, np.int64] and df["Mes"].dtype in [int, np.int64]):
            df["Año"] = pd.to_numeric(df["Año"], errors="coerce")
            df["Mes"] = pd.to_numeric(df["Mes"], errors="coerce")

        # Eliminar filas con valores inválidos en Año o Mes
        df = df.dropna(subset=["Año", "Mes"])

        # Convertir Mes y Año en enteros (por si son flotantes después de la conversión)
        df["Año"] = df["Año"].astype(int)
        df["Mes"] = df["Mes"].astype(int)

        # Crear la columna Fecha
        #df["Fecha"] = pd.to_datetime(df[["Año", "Mes"]].assign(Día=1), errors="coerce")
        #df["Fecha"] = pd.to_datetime(df[["Año", "Mes"]].assign(day=1), errors="coerce")
        df["Fecha"] = pd.to_datetime({'year': df["Año"], 'month': df["Mes"], 'day': 1}, errors="coerce")



        # Eliminar filas con fechas inválidas
        df = df.dropna(subset=["Fecha"])

        df_monthly = df.groupby("Fecha").agg(Unidades_vendidas=("Unidades_vendidas", "sum")).reset_index()

        # Línea de tendencia
        z = np.polyfit(range(len(df_monthly)), df_monthly["Unidades_vendidas"], 1)
        p = np.poly1d(z)

        # Crear gráfico
        plt.figure(figsize=(10, 6))
        plt.plot(df_monthly["Fecha"], df_monthly["Unidades_vendidas"], label="Unidades Vendidas", marker="o")
        plt.plot(df_monthly["Fecha"], p(range(len(df_monthly))), label="Tendencia", linestyle="--", color="red")
        plt.xlabel("Mes")
        plt.ylabel("Unidades Vendidas")
        plt.title("Evolución de Ventas")
        plt.legend()
        st.pyplot(plt)

    else:
        st.error("El archivo no tiene las columnas esperadas. Por favor, verifica el formato.")
