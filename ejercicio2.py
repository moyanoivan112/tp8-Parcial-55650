import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Análisis de Ventas", layout="wide")

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
        # Convertir las columnas necesarias a tipos correctos
        df["Año"] = pd.to_numeric(df["Año"], errors="coerce").fillna(0).astype(int)
        df["Mes"] = pd.to_numeric(df["Mes"], errors="coerce").fillna(0).astype(int)
        df["Unidades_vendidas"] = pd.to_numeric(df["Unidades_vendidas"], errors="coerce")
        df["Ingreso_total"] = pd.to_numeric(df["Ingreso_total"], errors="coerce")
        df["Costo_total"] = pd.to_numeric(df["Costo_total"], errors="coerce")

        # Filtro por sucursal
        sucursal = st.selectbox("Selecciona una sucursal", options=["Todas"] + list(df["Sucursal"].unique()))
        if sucursal != "Todas":
            df = df[df["Sucursal"] == sucursal]

        # Cálculo de métricas por producto
        df["Precio_unitario"] = df["Ingreso_total"] / df["Unidades_vendidas"]
        df["Margen_unitario"] = (df["Ingreso_total"] - df["Costo_total"]) / df["Ingreso_total"]

        df_metrics = df.groupby("Producto").agg(
            Precio_promedio=("Precio_unitario", "mean"),
            Margen_promedio=("Margen_unitario", "mean"),
            Unidades_vendidas=("Unidades_vendidas", "sum")
        ).reset_index()

        st.markdown("### Resumen por Producto")
        st.dataframe(df_metrics)

        # Gráfico de evolución de ventas
        st.markdown("### Evolución de Ventas Mensuales")
        df["Fecha"] = pd.to_datetime({"year": df["Año"], "month": df["Mes"], "day": 1}, errors="coerce")
        df_monthly = df.groupby("Fecha").agg(
            Unidades_vendidas=("Unidades_vendidas", "sum")
        ).reset_index()

        # Línea de tendencia
        z = np.polyfit(range(len(df_monthly)), df_monthly["Unidades_vendidas"], 1)
        p = np.poly1d(z)

        # Crear gráfico
        plt.figure(figsize=(12, 8))
        plt.plot(df_monthly["Fecha"], df_monthly["Unidades_vendidas"], label="Unidades Vendidas", marker="o")

        # Añadir información de productos
        for idx, row in df_metrics.iterrows():
            plt.annotate(
                f'{row["Producto"]}\nPrecio Prom: {row["Precio_promedio"]:.2f}\nMargen Prom: {row["Margen_promedio"]:.2%}',
                xy=(df_monthly["Fecha"].iloc[-1], df_monthly["Unidades_vendidas"].iloc[-1]),
                xytext=(df_monthly["Fecha"].iloc[-1], df_monthly["Unidades_vendidas"].iloc[-1] + 10),
                arrowprops=dict(facecolor='black', arrowstyle="->"),
                fontsize=10
            )

        plt.plot(df_monthly["Fecha"], p(range(len(df_monthly))), label="Tendencia", linestyle="--", color="red")
        plt.xlabel("Mes")
        plt.ylabel("Unidades Vendidas")
        plt.title("Evolución de Ventas")
        plt.legend()
        st.pyplot(plt)
    else:
        st.error("El archivo no tiene las columnas esperadas. Por favor, verifica el formato.")
