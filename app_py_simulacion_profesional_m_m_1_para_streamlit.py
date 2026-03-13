# ==============================================================
# app.py
# Simulación de Eventos Discretos (M/M/1)
# Versión 100% compatible con Streamlit Cloud
# SIN matplotlib (evita errores de entorno)
# ==============================================================

import streamlit as st
import numpy as np
import pandas as pd

# ==============================================================
# CONFIGURACIÓN
# ==============================================================

st.set_page_config(page_title="Simulación M/M/1", layout="wide")

st.title("Simulación de Eventos Discretos – Modelo M/M/1")

st.markdown("""
Aplicación profesional de simulación SED para un sistema M/M/1.
Compatible totalmente con Streamlit Cloud.
""")

# ==============================================================
# PARÁMETROS
# ==============================================================

st.sidebar.header("Parámetros")

lam = st.sidebar.number_input("Tasa de llegada λ (clientes/hora)", min_value=0.1, value=4.0)
mu = st.sidebar.number_input("Tasa de servicio μ (clientes/hora)", min_value=0.1, value=5.0)
n_clientes = st.sidebar.number_input("Número de pacientes", min_value=10, value=10)
seed = st.sidebar.number_input("Semilla aleatoria", min_value=1, value=42)

np.random.seed(seed)

rho = lam / mu

if rho >= 1:
    st.error("Sistema inestable: λ ≥ μ")

# ==============================================================
# GENERACIÓN DE VARIABLES
# ==============================================================

inter_arrivals = np.random.exponential(1/lam, int(n_clientes))
services = np.random.exponential(1/mu, int(n_clientes))
arrivals = np.cumsum(inter_arrivals)

start_service = np.zeros(int(n_clientes))
end_service = np.zeros(int(n_clientes))
wait_time = np.zeros(int(n_clientes))
system_time = np.zeros(int(n_clientes))

# ==============================================================
# SIMULACIÓN
# ==============================================================

for i in range(int(n_clientes)):
    if i == 0:
        start_service[i] = arrivals[i]
    else:
        start_service[i] = max(arrivals[i], end_service[i-1])

    end_service[i] = start_service[i] + services[i]
    wait_time[i] = start_service[i] - arrivals[i]
    system_time[i] = end_service[i] - arrivals[i]

# ==============================================================
# TABLA
# ==============================================================

st.subheader("Simulación Paso a Paso")

results = pd.DataFrame({
    "Paciente": np.arange(1, int(n_clientes)+1),
    "Llegada": arrivals,
    "Servicio": services,
    "Inicio Servicio": start_service,
    "Fin Servicio": end_service,
    "Tiempo en Cola": wait_time,
    "Tiempo en Sistema": system_time
})

st.dataframe(results, use_container_width=True)

# ==============================================================
# MÉTRICAS
# ==============================================================

W_sim = np.mean(system_time)
Wq_sim = np.mean(wait_time)
L_sim = lam * W_sim
Lq_sim = lam * Wq_sim

if rho < 1:
    W_theory = 1/(mu - lam)
    Wq_theory = rho/(mu - lam)
    L_theory = rho/(1 - rho)
    Lq_theory = rho**2/(1 - rho)
else:
    W_theory = None
    Wq_theory = None
    L_theory = None
    Lq_theory = None

st.subheader("Comparación Simulación vs Teoría")

col1, col2 = st.columns(2)

with col1:
    st.write("Resultados Simulados")
    st.write("ρ:", rho)
    st.write("W:", W_sim)
    st.write("Wq:", Wq_sim)
    st.write("L:", L_sim)
    st.write("Lq:", Lq_sim)

with col2:
    st.write("Resultados Teóricos")
    if rho < 1:
        st.write("W:", W_theory)
        st.write("Wq:", Wq_theory)
        st.write("L:", L_theory)
        st.write("Lq:", Lq_theory)
    else:
        st.write("Sistema inestable")

# ==============================================================
# VISUALIZACIONES SIN MATPLOTLIB
# ==============================================================

st.subheader("Convergencia del Promedio (Visualización nativa)")

if rho < 1:
    cumulative_mean = np.cumsum(system_time)/np.arange(1, int(n_clientes)+1)
    df_plot = pd.DataFrame({"Promedio acumulado": cumulative_mean})
    st.line_chart(df_plot)

st.subheader("Distribución aproximada del Tiempo en Sistema")

hist_values = np.histogram(system_time, bins=20)[0]
st.bar_chart(hist_values)

# ==============================================================
# EXPLICACIÓN
# ==============================================================

st.subheader("Transitorio vs Estacionario")

st.markdown("""
Transitorio: primeras observaciones con alta variabilidad.

Estacionario: cuando el número de pacientes aumenta,
las métricas convergen al valor teórico.
""")

st.success("Aplicación ejecutada correctamente.")
