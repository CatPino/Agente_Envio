import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from app.metrics import calcular_metricas, analizar_logs_falla, cargar_logs

st.set_page_config(
    page_title="Observabilidad — Agente ChileEnvia",
    layout="wide"
)

st.title("Dashboard de Observabilidad — Agente ChileEnvia")

if st.button("🔄 Actualizar datos"):
    st.rerun()

metricas = calcular_metricas()
hallazgos = analizar_logs_falla()

st.header("Métricas de observabilidad (IL3.1)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total interacciones", metricas["total_interacciones"])
col2.metric("Tasa de éxito", f"{metricas['tasa_exito']}%")
col3.metric("Latencia promedio", f"{metricas['latencia_promedio_ms']} ms")
col4.metric("Pasos promedio por respuesta", metricas["pasos_promedio"])

col5, col6, col7 = st.columns(3)
col5.metric("Latencia mínima", f"{metricas['latencia_min_ms']} ms")
col6.metric("Latencia máxima", f"{metricas['latencia_max_ms']} ms")
col7.metric("Latencia P95", f"{metricas['latencia_p95_ms']} ms")

st.info(f"**Consistencia:** {metricas['consistencia_nota']}")

st.divider()

logs = cargar_logs()
interacciones = [r for r in logs if r.get("tipo") == "interaccion"]

if interacciones:
    df = pd.DataFrame(interacciones)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Latencia por interacción (ms)")
        fig_lat = px.line(
            df, x="timestamp", y="latencia_ms",
            labels={"latencia_ms": "Latencia (ms)", "timestamp": "Hora"},
            markers=True, color_discrete_sequence=["#6C63FF"]
        )
        fig_lat.add_hline(
            y=metricas["latencia_promedio_ms"],
            line_dash="dash", line_color="orange",
            annotation_text=f"Promedio: {metricas['latencia_promedio_ms']} ms"
        )
        st.plotly_chart(fig_lat, use_container_width=True)

    with col_b:
        st.subheader("Pasos de razonamiento por consulta")
        fig_steps = px.bar(
            df, x="timestamp", y="pasos",
            labels={"pasos": "Pasos", "timestamp": "Hora"},
            color_discrete_sequence=["#00C9A7"]
        )
        st.plotly_chart(fig_steps, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Éxito vs. error")
        conteo = df["exitoso"].value_counts().reset_index()
        conteo.columns = ["resultado", "cantidad"]
        conteo["resultado"] = conteo["resultado"].map({True: "Exitoso", False: "Error"})
        fig_pie = px.pie(
            conteo, names="resultado", values="cantidad",
            color_discrete_sequence=["#00C9A7", "#FF6B6B"]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_d:
        st.subheader("Frecuencia de uso de herramientas")
        freq = metricas.get("herramientas_frecuencia", {})
        if freq:
            df_tools = pd.DataFrame(
                list(freq.items()), columns=["herramienta", "usos"]
            ).sort_values("usos", ascending=True)
            fig_tools = px.bar(
                df_tools, x="usos", y="herramienta", orientation="h",
                color_discrete_sequence=["#6C63FF"]
            )
            st.plotly_chart(fig_tools, use_container_width=True)
        else:
            st.info("Sin datos de herramientas aún.")

else:
    st.warning("Sin interacciones en el log. Ejecuta algunas consultas al agente y recarga.")

st.divider()

st.header("Análisis de trazabilidad y logs (IL3.2)")

for h in hallazgos:
    if "error" in h.lower() or "falla" in h.lower():
        st.error(h)
    elif "detectaron" in h.lower() or "alcanzaron" in h.lower():
        st.warning(h)
    else:
        st.success(h)

if interacciones:
    st.subheader("Registro detallado de ejecuciones")
    df_display = df[["timestamp", "session_id", "pregunta", "latencia_ms", "pasos", "exitoso", "error"]].copy()
    df_display["pregunta"] = df_display["pregunta"].str[:60] + "..."
    st.dataframe(df_display, use_container_width=True)
