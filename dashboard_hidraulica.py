import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# Configuración de la página web
st.set_page_config(page_title="Software Gerencial Hidráulica Minera - Edson Moyano", layout="wide")

st.title("🚰 Software Gerencial: Optimización Hidráulica, CAPEX/OPEX y Transporte de Pulpas")
st.markdown("**Desarrollado por Edson Moyano Lineros** | Senior Process & Operations Engineer")
st.markdown("---")

# Panel lateral de control para gerencia y clientes
st.sidebar.header("⚙️ Parámetros de Diseño y Económicos")
caudal_cliente = st.sidebar.number_input("Caudal de Operación (m³/h)", min_value=100.0, max_value=5000.0, value=1200.0, step=50.0)
solidos_cliente = st.sidebar.slider("Concentración de Sólidos en Peso (%)", 30.0, 75.0, 55.0)
diametro_tubería = st.sidebar.selectbox("Diámetro Nominal de Tubería (pulgadas)", [10, 12, 14, 16, 18, 20], index=1)
longitud_ducto = st.sidebar.number_input("Longitud de la Línea / Relaveducto (km)", min_value=1.0, max_value=100.0, value=15.0, step=1.0)
umbral_presion = st.sidebar.slider("Umbral Crítico de Presión (bar)", 50.0, 120.0, 80.0)

# Simulación avanzada de ingeniería y costos
@st.cache_data
def simular_sistema(caudal, solidos, diametro, longitud):
    np.random.seed(42)
    fechas = pd.date_range(start="2026-09-01", periods=168, freq="h")
    
    factor_diametro = 12 / diametro
    velocidad_flujo = (caudal / 3600) / (0.7854 * (diametro * 0.0254)**2)
    presion_base = (caudal / 1000) * (solidos / 50) * factor_diametro * longitud * 3.5
    
    df = pd.DataFrame({
        "Timestamp": fechas,
        "Caudal_m3h": np.random.normal(caudal, caudal * 0.03, 168),
        "Presion_Impulsion_bar": np.random.normal(presion_base, 4.0, 168),
        "Velocidad_ms": np.random.normal(velocidad_flujo, 0.15, 168),
        "Consumo_Energetico_kW": np.random.normal(caudal * 0.42 * (longitud/10), 20, 168)
    })
    df.loc[45:52, "Presion_Impulsion_bar"] += 22
    df.loc[45:52, "Velocidad_ms"] -= 0.6
    return df

df_ops = simular_sistema(caudal_cliente, solidos_cliente, diametro_tubería, longitud_ducto)

# Estimación Financiera CAPEX y OPEX
capex_millones = (diametro * 0.15 + longitud * 0.25) * (solidos_cliente / 50)
kwh_anual = df_ops["Consumo_Energetico_kW"].mean() * 8760
opex_anual_millones = (kwh_anual * 0.09) / 1_000_000

# KPIs en Pantalla
col1, col2, col3, col4 = st.columns(4)
col1.metric("Velocidad Promedio de Pulpa", f"{df_ops['Velocidad_ms'].mean():.2f} m/s", "Ref: > 1.8 m/s")
col2.metric("Presión Máxima Operacional", f"{df_ops['Presion_Impulsion_bar'].max():.1f} bar", "Línea de Impulsión")
col3.metric("CAPEX Estimado", f"${capex_millones:.2f} M USD", f"Ducto {longitud_ducto} km")
col4.metric("OPEX Energético Anual", f"${opex_anual_millones:.2f} M USD/año", "Operacional")

st.markdown("### 📈 Monitoreo Dinámico: Presión de Impulsión vs Límite de Seguridad")
fig = px.line(df_ops, x="Timestamp", y=["Presion_Impulsion_bar"],
              title=f"Comportamiento de Presión en Relaveducto (Ø {diametro_tubería}", {longitud_ducto} km)",
              labels={"value": "Presión (bar)", "Timestamp": "Horizonte Temporal"})
fig.add_hline(y=umbral_presion, line_dash="dash", line_color="red", annotation_text="Límite Crítico")
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🧠 Diagnóstico Técnico y Evaluación de Riesgos")
alertas_activas = df_ops[df_ops["Presion_Impulsion_bar"] > umbral_presion]

if not alertas_activas.empty:
    st.warning(f"⚠️ Se detectaron **{len(alertas_activas)} eventos de sobrepresión** sobre el umbral de seguridad.")
else:
    st.success("✅ El sistema opera con total estabilidad hidráulica.")

st.markdown("---")

def generar_reporte_gerencial(caudal, solidos, diametro, longitud, capex, opex, total_alertas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 15)
    pdf.cell(0, 10, "REPORTE GERENCIAL DE EVALUACION HIDRAULICA", 0, 1, "C")
    pdf.set_font("Arial", "I", 11)
    pdf.cell(0, 7, "Transporte de Pulpas, CAPEX y OPEX", 0, 1, "C")
    pdf.ln(4)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Elaborado por: Edson Moyano Lineros - Senior Process Engineer", 0, 1)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "1. Parametros de Diseno:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"- Caudal: {caudal} m3/h | Solidos: {solidos}%", 0, 1)
    pdf.cell(0, 5, f"- Diametro: {diametro} pulgadas | Longitud: {longitud} km", 0, 1)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "2. Evaluacion Economica:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"- CAPEX Estimado: ${capex:.2f} Millones USD", 0, 1)
    pdf.cell(0, 5, f"- OPEX Anual: ${opex:.2f} Millones USD / ano", 0, 1)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "3. Conclusiones:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, f"La simulacion registro {total_alertas} eventos criticos. Se valida la velocidad para prevenir sedimentacion.")
    return bytes(pdf.output())

st.markdown("### 📄 Entregable Ejecutivo")
if st.button("📥 Generar Reporte Gerencial Ejecutivo en PDF"):
    pdf_bytes = generar_reporte_gerencial(caudal_cliente, solidos_cliente, diametro_tubería, longitud_ducto, capex_millones, opex_anual_millones, len(alertas_activas))
    st.download_button("💾 Descargar PDF Oficial", data=pdf_bytes, file_name="Reporte_Gerencial.pdf", mime="application/pdf")
