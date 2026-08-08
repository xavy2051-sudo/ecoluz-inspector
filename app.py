# app.py
# ==============================================================================
# ECOLUZ - INSPECTOR TÉCNICO E IMPULSOR DE CUBICACIÓN
# ==============================================================================

import json
import sqlite3
import pandas as pd
import streamlit as st

# Importación de la Biblioteca Técnica Desacoplada
from biblioteca_tecnica import (
    calcular_cubicacion_y_apu,
    inicializar_fase1_db,
    obtener_configuracion_partida,
    obtener_lista_partidas,
)

st.set_page_config(
    page_title="ECOLUZ - Inspector Técnico",
    page_icon="👷‍♂️",
    layout="wide",
)

# Inicialización de la base de datos relacional
inicializar_fase1_db()

DB_FILE = "ecoluz_database.db"


def get_connection():
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  conn = get_connection()
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            mandante TEXT,
            direccion TEXT,
            fecha TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()

# ------------------------------------------------------------------------------
# SIDEBAR - NAVEGACIÓN
# ------------------------------------------------------------------------------
st.sidebar.title("📌 Proyecto en Inspección")

conn = get_connection()
proyectos_df = pd.read_sql_query("SELECT id, nombre FROM proyectos", conn)
conn.close()

proyectos_options = {"N/A": "Sin Proyectos"}
if not proyectos_df.empty:
  proyectos_options = {
      f"ID {row['id']} - {row['nombre']}": row["id"]
      for _, row in proyectos_df.iterrows()
  }

proyecto_seleccionado = st.sidebar.selectbox(
    "Seleccionar Proyecto Activo:", list(proyectos_options.keys())
)
proyecto_id_activo = proyectos_options[proyecto_seleccionado]

st.sidebar.markdown("---")
modulo = st.sidebar.radio(
    "Flujo del Inspector Técnico",
    [
        "📌 1. Información General",
        "📊 2. Inspección en Terreno (Recintos y Patologías)",
        "🔍 3. Motor de Auditoría y Alertas RIC/SEC",
        "📄 4. Generador de EETT y Cotizaciones",
        "💰 5. Módulo APU y Cubicaciones de Materiales",
    ],
)

# ------------------------------------------------------------------------------
# MÓDULO 1: INFORMACIÓN GENERAL
# ------------------------------------------------------------------------------
if modulo == "📌 1. Información General":
  st.header("📌 Gestión de Proyectos")
  with st.form("form_proyecto"):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
      p_id = st.text_input("Código / ID Proyecto:", "PRJ-001")
      p_nombre = st.text_input("Nombre del Proyecto:", "Remodelación de Baño")
    with col_p2:
      p_mandante = st.text_input("Cliente / Mandante:", "Constructora Ejemplo")
      p_direccion = st.text_input("Dirección de la Obra:", "Av. Principal 123")

    submit_p = st.form_submit_button("Guardar Proyecto")
    if submit_p:
      conn = get_connection()
      c = conn.cursor()
      c.execute(
          "INSERT OR REPLACE INTO proyectos VALUES (?, ?, ?, ?, DATE('now'))",
          (p_id, p_nombre, p_mandante, p_direccion),
      )
      conn.commit()
      conn.close()
      st.success(f"Proyecto '{p_nombre}' registrado exitosamente.")
      st.rerun()

# ------------------------------------------------------------------------------
# MÓDULO 2: INSPECCIÓN EN TERRENO Y FORMULARIO DINÁMICO
# ------------------------------------------------------------------------------
elif modulo == "📊 2. Inspección en Terreno (Recintos y Patologías)":
  st.header("📊 Levantamiento en Terreno")

  cr1, cr2 = st.columns([1, 1])

  # Obtener lista completa de partidas directamente desde la biblioteca
  partidas_disponibles = obtener_lista_partidas()

  with cr1:
    st.subheader("1. Ubicación y Partida")
    recinto = st.selectbox(
        "Recinto Evaluado:",
        [
            "Baño Principal",
            "Baño Visitas",
            "Cocina",
            "Dormitorio 1",
            "Living / Comedor",
        ],
    )

    partida_nombre = st.selectbox(
        "Elemento Constructivo / Partida:", partidas_disponibles
    )

    diagnostico = st.selectbox(
        "Diagnóstico ITO:", ["Conforme", "No Conforme", "Requiere Intervención"]
    )
    patologia = st.text_input(
        "Patología Observada / Comentario:", "Sin observaciones"
    )

  config_partida = obtener_configuracion_partida(partida_nombre)
  respuestas_usuario = {}

  with cr2:
    st.subheader(f"2. Parámetros Técnicos: {partida_nombre}")

    if config_partida and config_partida.get("preguntas"):
      st.caption(f"Categoría: {config_partida.get('categoria', 'General')}")

      for q in config_partida["preguntas"]:
        campo_id = q["campo_id"]
        label = q["etiqueta"]
        tipo = q["tipo_input"]
        val_def = q["valor_default"]

        if tipo == "number":
          val_float = float(val_def) if val_def is not None else 0.0
          respuestas_usuario[campo_id] = st.number_input(
              label,
              value=val_float,
              step=q.get("step_val", 1.0),
              help=q.get("help_text", ""),
              key=f"dyn_{partida_nombre}_{campo_id}",
          )
        elif tipo == "select":
          opciones = q.get("opciones", [])
          idx = opciones.index(val_def) if val_def in opciones else 0
          respuestas_usuario[campo_id] = st.selectbox(
              label,
              opciones,
              index=idx,
              key=f"dyn_{partida_nombre}_{campo_id}",
          )
        else:
          respuestas_usuario[campo_id] = st.text_input(
              label, value=val_def, key=f"dyn_{partida_nombre}_{campo_id}"
          )

  st.markdown("---")

  apu = {}
  if respuestas_usuario:
    resultado_calculo = calcular_cubicacion_y_apu(
        partida_nombre, respuestas_usuario
    )

    st.subheader("💡 Resumen de Cubicación y Materiales Requeridos")
    c_m1, c_m2 = st.columns([2, 1])

    with c_m1:
      mat_df = pd.DataFrame(resultado_calculo["materiales"])
      st.table(mat_df)

    with c_m2:
      apu = resultado_calculo["apu"]
      st.metric(
          "Costo Directo Estimado", f"${apu.get('costo_directo_total_clp', 0):,} CLP"
      )
      st.caption(f"Materiales: ${apu.get('costo_materiales_clp', 0):,} CLP")
      st.caption(
          f"Mano de Obra: {apu.get('hh_mano_obra', 0)} HH ("
          f"${apu.get('costo_mano_obra_clp', 0):,} CLP)"
      )

  if st.button("💾 Registrar Inspección"):
    json_respuestas = json.dumps(respuestas_usuario, ensure_ascii=False)
    conn = get_connection()
    c = conn.cursor()
    costo_txt = (
        f"Costo Directo APU: ${apu.get('costo_directo_total_clp', 0):,} CLP"
        if apu
        else "Sin APU"
    )
    c.execute(
        """
            INSERT INTO recintos_levantamiento 
            (proyecto_id, nombre_recinto, elemento_constructivo, estado_diagnostico, patologia_observada, datos_tecnicos_json, observaciones_ito)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            proyecto_id_activo,
            recinto,
            partida_nombre,
            diagnostico,
            patologia,
            json_respuestas,
            costo_txt,
        ),
    )
    conn.commit()
    conn.close()
    st.success(f"Inspección para '{partida_nombre}' guardada con éxito.")

# ------------------------------------------------------------------------------
# MÓDULOS EN DESARROLLO (3, 4 y 5)
# ------------------------------------------------------------------------------
else:
  st.header(modulo)
  st.info(
      "Módulo activo y conectado a la base de datos relacional. Selecciona"
      " 'Inspección en Terreno' para probar la dynamic UI completa."
  )
