# ==============================================================
# app.py
# Simulación de Eventos Discretos (M/M/1)
# Ingeniería Industrial – Nivel Profesional
# Lista para desplegar en Streamlit Cloud
# ==============================================================

# ============================
# LIBRERÍAS NECESARIAS
# ============================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================
# CONFIGURACIÓN GENERAL
# ==============================================================

st.set_page_config(
    page_title="Simulación Profesional M/M/1",
    layout="wide"
)

st.title("Simulación de Eventos Discretos – Modelo M/M/1")
st.markdown("""
Esta aplicación implementa un modelo completo de **Simulación de Eventos Discretos (SED)**
para un sistema de colas M/M/1.

Incluye:
- Definición formal del estado
- Eventos
- Lista de eventos futuros (implícita)
- Variables estadísticas acumulativas
- Implementación paso a paso
- Comparación contra solución analítica
""")

# ==============================================================
# SIDEBAR – PARÁMETROS
# ==============================================================

st.sidebar.header("Parámetros del Sistema")

lam = st.sidebar.number_input("Tasa de llegada λ (clientes por hora)", min_value=0.1, value=4.0)
mu = st.sidebar.number_input("Tasa de servicio μ (clientes por hora)", min_value=0.1, value=5.0)
n_clientes = st.sidebar.number_input("Número de pacientes a simular", min_value=10, value=10)

seed = st.sidebar.number_input("Semilla aleatoria", min_value=1, value=42)
np.random.seed(seed)

# ==============================================================
# VALIDACIÓN DE ESTABILIDAD
# ==============================================================

rho = lam / mu

if rho >= 1:
    st.error("⚠ Sistema inestable: λ ≥ μ. Ajuste parámetros.")

# ==============================================================
# DEFINICIÓN FORMAL DEL MODELO
# ==============================================================

st.subheader("Definición Formal del Modelo SED")

st.markdown("""
**Estado del sistema:**
- Número de clientes en sistema
- Estado del servidor (ocupado/libre)

**Eventos:**
- Llegada
- Fin de servicio

**FEL (Lista de Eventos Futuros implícita):**
- Próxima llegada
- Próxima salida

**Variables acumulativas:**
- Tiempo total en cola
- Tiempo total en sistema
- Utilización
""")

# ==============================================================
# GENERACIÓN DE VARIABLES ALEATORIAS
# ==============================================================

inter_arrivals = np.random.exponential(1/lam, int(n_clientes))
services = np.random.exponential(1/mu, int(n_clientes))

arrivals = np.cumsum(inter_arrivals)

# ==============================================================
# ESTRUCTURAS DE DATOS
# ==============================================================

start_service = np.zeros(int(n_clientes))
end_service = np.zeros(int(n_clientes))
wait_time = np.zeros(int(n_clientes))
system_time = np.zeros(int(n_clientes))

# ==============================================================
# SIMULACIÓN PASO A PASO
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
# TABLA DE RESULTADOS
# ==============================================================

st.subheader("Simulación Paso a Paso")

results = pd.DataFrame({
    "Paciente": np.arange(1, int(n_clientes)+1),
    "Tiempo Entre Llegadas": inter_arrivals,
    "Llegada": arrivals,
    "Tiempo Servicio": services,
    "Inicio Servicio": start_service,
    "Fin Servicio": end_service,
    "Tiempo en Cola": wait_time,
    "Tiempo en Sistema": system_time
})

st.dataframe(results, use_container_width=True)

# ==============================================================
# MÉTRICAS SIMULADAS
# ==============================================================

W_sim = np.mean(system_time)
Wq_sim = np.mean(wait_time)
L_sim = lam * W_sim
Lq_sim = lam * Wq_sim

# ==============================================================
# MÉTRICAS TEÓRICAS
# ==============================================================

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

# ==============================================================
# RESULTADOS COMPARATIVOS
# ==============================================================

st.subheader("Comparación Simulación vs Teoría")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Resultados Simulados")
    st.write("ρ (Utilización):", rho)
    st.write("W (Sistema):", W_sim)
    st.write("Wq (Cola):", Wq_sim)
    st.write("L (Sistema):", L_sim)
    st.write("Lq (Cola):", Lq_sim)

with col2:
    st.markdown("### Resultados Teóricos")
    if rho < 1:
        st.write("W:", W_theory)
        st.write("Wq:", Wq_theory)
        st.write("L:", L_theory)
        st.write("Lq:", Lq_theory)
    else:
        st.write("Sistema inestable")

# ==============================================================
# VISUALIZACIONES
# ==============================================================

st.subheader("Distribución del Tiempo en Sistema")

fig1, ax1 = plt.subplots()
ax1.hist(system_time, bins=30, density=True)
ax1.set_xlabel("Tiempo en Sistema")
ax1.set_ylabel("Densidad")
st.pyplot(fig1)

if rho < 1:
    st.subheader("Convergencia del Promedio hacia Valor Teórico")

    cumulative_mean = np.cumsum(system_time)/np.arange(1, int(n_clientes)+1)
    fig2, ax2 = plt.subplots()
    ax2.plot(cumulative_mean, label="Promedio acumulado")
    ax2.axhline(W_theory, linestyle="--", label="Valor teórico")
    ax2.set_xlabel("Número de pacientes")
    ax2.set_ylabel("Promedio acumulado W")
    ax2.legend()
    st.pyplot(fig2)

# ==============================================================
# EXPLICACIÓN CONCEPTUAL
# ==============================================================

st.subheader("Comportamiento Transitorio vs Estacionario")

st.markdown("""
**Transitorio:**
Las primeras observaciones presentan alta variabilidad y no representan el
comportamiento estable del sistema.

**Estacionario:**
Cuando el número de pacientes aumenta, las métricas convergen a los valores
teóricos. Esto es consecuencia de la Ley de los Grandes Números.
""")

st.success("Simulación ejecutada correctamente.")
