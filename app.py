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
    BIBLIOTECA_TECNICA,
    render_formulario_dinamico,
    calcular_materiales_partida,
)

st.set_page_config(page_title="ECOLUZ - Inspector Técnico", layout="wide")

# ------------------------------------------------------------------------------
# BASE DE DATOS Y CONEXIÓN
# ------------------------------------------------------------------------------
DB_FILE = "ecoluz_database.db"


def get_connection():
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  """Inicializa y migra automáticamente la tabla para soportar datos JSON dinámicos."""
  conn = get_connection()
  c = conn.cursor()

  # Crear tabla base si no existe
  c.execute("""
        CREATE TABLE IF NOT EXISTS recintos_levantamiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id TEXT,
            nombre_recinto TEXT,
            elemento_constructivo TEXT,
            estado_diagnostico TEXT,
            patologia_observada TEXT,
            datos_tecnicos_json TEXT,
            observaciones_ito TEXT,
            puntos_enchufes INTEGER DEFAULT 0,
            centros_iluminacion INTEGER DEFAULT 0,
            interruptores INTEGER DEFAULT 0,
            puntos_fuerza_clima INTEGER DEFAULT 0,
            estado_canalizacion TEXT DEFAULT ''
        )
    """)

  # Verificar si la columna datos_tecnicos_json existe (Migración automática)
  c.execute("PRAGMA table_info(recintos_levantamiento)")
  columns = [row["name"] for row in c.fetchall()]
  if "datos_tecnicos_json" not in columns:
    c.execute(
        "ALTER TABLE recintos_levantamiento ADD COLUMN datos_tecnicos_json"
        " TEXT"
    )

  conn.commit()
  conn.close()


init_db()

# ------------------------------------------------------------------------------
# PANEL LATERAL
# ------------------------------------------------------------------------------
st.sidebar.title("📌 Proyecto en Inspección")
proy_id = st.sidebar.selectbox("Seleccionar Proyecto Activo:", ["ID 1 - miguel"])

menu_opcion = st.sidebar.radio(
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
# MÓDULO 2: INSPECCIÓN EN TERRENO (ARQUITECTURA DINÁMICA)
# ------------------------------------------------------------------------------
if "📊 2. Inspección en Terreno" in menu_opcion:
  st.title("📊 Inspección Espacial: Recintos, Elementos y Materiales")

  if not proy_id:
    st.warning("⚠️ Selecciona un proyecto activo en el panel lateral.")
  else:
    tab_ingreso_rec, tab_resumen_cub, tab_desglose_mat = st.tabs([
        "📝 Levantamiento Diagnóstico por Recinto",
        "📋 Resumen Consolidado de Levantamientos",
        "📦 Cubicación Detallada de Materiales (APU)",
    ])

    conn = get_connection()

    # TAB 1: FORMULARIO DINÁMICO
    with tab_ingreso_rec:
      st.subheader(
          "📍 Diagnóstico de Elementos Constructivos y Prescripción Técnica"
      )

      # Selección previa fuera del form para refrescar dinámicamente el lado derecho
      c_top1, c_top2 = st.columns(2)
      with c_top1:
        nombre_rec = st.selectbox(
            "Recinto / Espacio Físico:",
            [
                "Baño Principal (Zona Húmeda)",
                "Cocina (Zona Húmeda)",
                "Baño Visitas",
                "Estar / Comedor",
                "Dormitorio Principal",
                "Dormitorio 2",
                "Pasillo / Acceso",
                "Exterior / Fachada",
                "Logia / Lavadero",
            ],
        )

      with c_top2:
        elem_constructivo = st.selectbox(
            "Elemento Constructivo Evaluado:",
            list(BIBLIOTECA_TECNICA.keys()),
        )

      st.divider()

      with st.form("form_recinto_dinamico"):
        cr1, cr2 = st.columns(2)

        with cr1:
          st.markdown("#### 🔍 Estado Diagnóstico ITO")
          diag_estado = st.selectbox(
              "Diagnóstico ITO / Estado Actual:",
              [
                  "Sin Instalación / Obra Gruesa",
                  "Conforme / Normalizado",
                  "No Conforme (Requiere Intervención/Cambio)",
                  "Deterioro por Humedad / Desprendimiento",
                  "Instalación Incompleta",
              ],
          )

          patologia_txt = st.text_input(
              "Descripción de la Patología o Deficiencia Observada:",
              placeholder=(
                  "Ej: Muros sin placa RH o canalizaciones eléctricas expuestas."
              ),
          )

          obs_ito = st.text_area(
              "Observaciones y Prescripción Técnica del ITO:"
          )

        with cr2:
          # RENDERIZADO DINÁMICO BASADO EN LA BIBLIOTECA TÉCNICA
          respuestas_dinamicas = render_formulario_dinamico(elem_constructivo)

        submit_btn = st.form_submit_button(
            "➕ Registrar Inspección de Recinto"
        )

        if submit_btn:
          # Precondición y preparación de datos JSON
          json_data = json.dumps(respuestas_dinamicas, ensure_ascii=False)

          # Mapeo de fallback para compatibilidad eléctrica antigua
          num_enchufes = int(respuestas_dinamicas.get("num_enchufes", 0))
          num_centros = int(respuestas_dinamicas.get("num_centros", 0))
          num_interruptores = int(
              respuestas_dinamicas.get("num_interruptores", 0)
          )
          num_fuerza = int(respuestas_dinamicas.get("num_fuerza", 0))
          est_canal = str(
              respuestas_dinamicas.get("tipo_canalizacion", elem_constructivo)
          )

          c = conn.cursor()
          c.execute(
              """
                        INSERT INTO recintos_levantamiento 
                        (proyecto_id, nombre_recinto, elemento_constructivo, estado_diagnostico, patologia_observada,
                         datos_tecnicos_json, observaciones_ito, puntos_enchufes, centros_iluminacion, interruptores, puntos_fuerza_clima, estado_canalizacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  proy_id,
                  nombre_rec,
                  elem_constructivo,
                  diag_estado,
                  patologia_txt,
                  json_data,
                  obs_ito,
                  num_enchufes,
                  num_centros,
                  num_interruptores,
                  num_fuerza,
                  est_canal,
              ),
          )
          conn.commit()
          st.success(
              f"✅ Se registró **{elem_constructivo}** en **{nombre_rec}**"
              " exitosamente."
          )
          st.rerun()

    # TAB 2: RESUMEN CONSOLIDADO DE LEVANTAMIENTOS
    with tab_resumen_cub:
      st.subheader("📋 Registros de Inspección por Recinto")
      df_recintos = pd.read_sql_query(
          """
                SELECT id, nombre_recinto AS [Recinto], elemento_constructivo AS [Elemento], 
                       estado_diagnostico AS [Estado Diagnóstico], patologia_observada AS [Patología],
                       datos_tecnicos_json AS [Parametros_JSON], observaciones_ito AS [Observación ITO]
                FROM recintos_levantamiento WHERE proyecto_id = ?
            """,
          conn,
          params=(proy_id,),
      )

      if df_recintos.empty:
        st.info("ℹ️ No hay registros guardados para este proyecto.")
      else:
        st.dataframe(
            df_recintos.drop(columns=["Parametros_JSON"]),
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("🗑️ Eliminar Registro de Recinto"):
          rec_del = st.selectbox(
              "Selecciona el registro a borrar:",
              options=df_recintos["id"].tolist(),
              format_func=lambda x: (
                  f"ID {x} - "
                  f"{df_recintos[df_recintos['id']==x]['Recinto'].values[0]} ("
                  f"{df_recintos[df_recintos['id']==x]['Elemento'].values[0]})"
              ),
          )
          if st.button("Confirmar Eliminación"):
            conn.execute(
                "DELETE FROM recintos_levantamiento WHERE id = ?", (rec_del,)
            )
            conn.commit()
            st.rerun()

    # TAB 3: CUBICACIÓN DETALLADA Y LISTA DE MATERIALES PARA APU
    with tab_desglose_mat:
      st.subheader(
          "📦 Cubicación Consolidada de Materiales por Partida Evaluada"
      )

      c = conn.cursor()
      c.execute(
          """
                SELECT id, nombre_recinto, elemento_constructivo, datos_tecnicos_json 
                FROM recintos_levantamiento WHERE proyecto_id = ?
            """,
          (proy_id,),
      )
      filas = c.fetchall()

      if not filas:
        st.info("ℹ️ No existen materiales para calcular aún.")
      else:
        todos_materiales = []

        for f in filas:
          rec = f["nombre_recinto"]
          elem = f["elemento_constructivo"]
          raw_json = f["datos_tecnicos_json"]

          if raw_json:
            try:
              respuestas_dict = json.loads(raw_json)
            except Exception:
              respuestas_dict = {}
          else:
            respuestas_dict = {}

          # Cálculo automático utilizando la Biblioteca Técnica
          mat_calculados = calcular_materiales_partida(elem, respuestas_dict)

          for m in mat_calculados:
            todos_materiales.append({
                "Recinto": rec,
                "Partida": elem,
                "Insumo / Material": m["insumo"],
                "Cantidad Cúbica": m["cantidad"],
                "Unidad": m["unidad"],
            })

        if todos_materiales:
          df_mat = pd.DataFrame(todos_materiales)
          st.dataframe(df_mat, use_container_width=True, hide_index=True)

          # Exportación directa
          csv_data = df_mat.to_csv(index=False).encode("utf-8")
          st.download_button(
              label="📥 Descargar Cubicación de Materiales (CSV)",
              data=csv_data,
              file_name=f"cubicacion_materiales_{proy_id}.csv",
              mime="text/csv",
          )

    conn.close()
