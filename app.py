import json
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# 1. BASE DE DATOS LOCAL (SQLite)
# ==========================================
DB_NAME = "ecoluz.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            direccion TEXT,
            inspector TEXT,
            fecha_creacion TEXT
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones_versiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_nombre TEXT,
            version TEXT,
            monto_total REAL,
            detalles_json TEXT,
            observaciones TEXT,
            fecha TEXT
        )
    """)
  conn.commit()
  conn.close()


def guardar_version(
    proyecto, version, monto_total, detalles_dict, observaciones=""
):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  cursor.execute(
      """
        INSERT INTO cotizaciones_versiones (proyecto_nombre, version, monto_total, detalles_json, observaciones, fecha)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
      (
          proyecto,
          version,
          monto_total,
          json.dumps(detalles_dict),
          observaciones,
          fecha_actual,
      ),
  )
  conn.commit()
  conn.close()


def obtener_historial_versiones():
  conn = sqlite3.connect(DB_NAME)
  try:
    df = pd.read_sql_query(
        "SELECT id, proyecto_nombre, version, monto_total, observaciones, fecha"
        " FROM cotizaciones_versiones ORDER BY id DESC",
        conn,
    )
  except Exception:
    df = pd.DataFrame()
  conn.close()
  return df


# ==========================================
# 2. MOTOR DE DEPENDENCIAS Y CUBICACIONES (BOM)
# ==========================================
class MaterialDependencyEngine:

  @staticmethod
  def obtener_kit_dependiente(partida_principal, cantidad_m2):
    if partida_principal == "Cerámica / Porcelanato":
      return [
          {
              "Item / Insumo": "Adhesivo Cerámico (Sacos 25kg)",
              "Cantidad": round(cantidad_m2 / 5.0, 2),
              "Unidad": "saco",
              "P. Unitario ($)": 7500,
          },
          {
              "Item / Insumo": "Fragüe",
              "Cantidad": round(cantidad_m2 / 4.0, 2),
              "Unidad": "kg",
              "P. Unitario ($)": 2800,
          },
          {
              "Item / Insumo": "Crucetas / Niveladores",
              "Cantidad": round(cantidad_m2 * 20, 0),
              "Unidad": "un",
              "P. Unitario ($)": 35,
          },
          {
              "Item / Insumo": "Silicona Sanitaria Anti-hongos",
              "Cantidad": round(cantidad_m2 / 15.0, 1),
              "Unidad": "tubo",
              "P. Unitario ($)": 4200,
          },
      ]
    elif partida_principal == "Estructura Metalcom":
      return [
          {
              "Item / Insumo": "Perfil Montante 60x38x0.85mm",
              "Cantidad": round(cantidad_m2 * 1.2, 1),
              "Unidad": "tira",
              "P. Unitario ($)": 6200,
          },
          {
              "Item / Insumo": "Perfil Canal 61x28x0.85mm",
              "Cantidad": round(cantidad_m2 * 0.5, 1),
              "Unidad": "tira",
              "P. Unitario ($)": 5400,
          },
          {
              "Item / Insumo": "Tornillos Framing 8x1/2 (Caja 500 un)",
              "Cantidad": round((cantidad_m2 * 40) / 500, 1),
              "Unidad": "caja",
              "P. Unitario ($)": 8900,
          },
          {
              "Item / Insumo": "Aislación Lana de Vidrio R188",
              "Cantidad": round(cantidad_m2 * 1.05, 2),
              "Unidad": "m2",
              "P. Unitario ($)": 3200,
          },
      ]
    elif partida_principal == "Volcanita / Placa Yeso-Cartón":
      placas = cantidad_m2 / 2.98
      return [
          {
              "Item / Insumo": "Placas Volcanita RH / ST",
              "Cantidad": round(placas, 1),
              "Unidad": "placa",
              "P. Unitario ($)": 9800,
          },
          {
              "Item / Insumo": "Tornillos Drywall 6x1 5/8 (Caja 1000 un)",
              "Cantidad": round((placas * 30) / 1000, 1),
              "Unidad": "caja",
              "P. Unitario ($)": 11500,
          },
          {
              "Item / Insumo": "Masa Junta Lista (Juntaprop)",
              "Cantidad": round(cantidad_m2 * 1.2, 1),
              "Unidad": "kg",
              "P. Unitario ($)": 1800,
          },
          {
              "Item / Insumo": "Cinta Malla / Papel Junta",
              "Cantidad": round(cantidad_m2 * 1.2, 1),
              "Unidad": "mL",
              "P. Unitario ($)": 450,
          },
      ]
    return []


# ==========================================
# 3. MOTOR DE AUDITORÍA Y NORMATIVA CHILENA
# ==========================================
class AuditEngine:

  @staticmethod
  def auditar_proyecto(datos):
    alertas = []
    campos = [
        "permiso_dom",
        "factibilidad_sec",
        "tipo_aislacion",
        "zona_humeda",
        "puesta_tierra",
    ]
    completados = sum(1 for c in campos if datos.get(c))
    porcentaje = int((completados / len(campos)) * 100)

    if datos.get("zona_humeda") and datos.get("placa_std"):
      alertas.append(
          "🔴 NORMATIVA OGUC: En zonas húmedas (baños/cocinas) es obligatorio"
          " utilizar Volcanita RH (Resistente a Humedad) en lugar de ST"
          " (Estándar)."
      )

    if not datos.get("factibilidad_sec"):
      alertas.append(
          "⚠️ NORMATIVA SEC: Falta verificación del empalme y tablero eléctrico"
          " bajo norma TE1."
      )

    if not datos.get("permiso_dom"):
      alertas.append(
          "⚠️ REGULARIZACIÓN DOM: Obra sin permiso de edificación preliminar"
          " verificado."
      )

    if porcentaje >= 80 and not any("🔴" in a for a in alertas):
      semaforo = "🟢 APTO PARA COTIZAR"
    elif porcentaje >= 50:
      semaforo = "🟡 REQUIERE REVISIÓN TÉCNICA"
    else:
      semaforo = "🔴 NO CONFORME"

    return porcentaje, semaforo, alertas


# ==========================================
# 4. APLICACIÓN Y NAVEGACIÓN
# ==========================================
st.set_page_config(
    page_title="ECOLUZ v2.0 - Inspector Técnico", layout="wide", page_icon="🏗️"
)

init_db()

st.title("🏗️ ECOLUZ v2.0 — Inspector Técnico Profesional")
st.caption(
    "Sistema Integral de Inspección, Cubicaciones, Auditoría Normativa y APU"
)

opcion = st.sidebar.radio("Navegación / Módulos:", [
    "1. Levantamiento y Factibilidad",
    "2. Motor de Cubicaciones y Kits",
    "3. Auditoría Pre-Cotización",
    "4. APU e Historial de Versiones",
])

if opcion == "1. Levantamiento y Factibilidad":
  st.header("📋 Factibilidad Técnica de la Obra")
  col1, col2 = st.columns(2)
  with col1:
    st.subheader("Edificación y Terreno (DOM)")
    st.checkbox("¿Terreno cuenta con Rol propio?")
    st.checkbox("¿Cuenta con Permiso de Edificación DOM?")
    st.checkbox("¿Requiere Cálculo Estructural?")
  with col2:
    st.subheader("Servicios Eléctricos (SEC)")
    st.selectbox(
        "Tipo de Empalme Existente:",
        ["Monofásico (1Ф)", "Trifásico (3Ф)", "Sin Empalme"],
    )
    st.checkbox("¿Cuenta con Puesta a Tierra y Tablero SEC?")

elif opcion == "2. Motor de Cubicaciones y Kits":
  st.header("📦 Cálculo Automático de Insumos (BOM)")
  partida = st.selectbox(
      "Seleccione Partida Principal:",
      [
          "Cerámica / Porcelanato",
          "Estructura Metalcom",
          "Volcanita / Placa Yeso-Cartón",
      ],
  )
  m2 = st.number_input(
      "Superficie / Cantidad a ejecutar (m²):", min_value=1.0, value=20.0
  )

  if st.button("Generar Kit de Materiales"):
    insumos = MaterialDependencyEngine.obtener_kit_dependiente(partida, m2)
    df = pd.DataFrame(insumos)
    df["Subtotal ($)"] = df["Cantidad"] * df["P. Unitario ($)"]
    st.success(
        f"Kit de insumos calculado automáticamente para {m2} m² de {partida}:"
    )
    st.dataframe(df, use_container_width=True)
    st.metric("Total Insumos ($)", f"${df['Subtotal ($)'].sum():,.0f} CLP")

elif opcion == "3. Auditoría Pre-Cotización":
  st.header("🔍 Auditoría e Inspección Técnica")
  st.write("Verificación de inconsistencias técnicas y normas OGUC / SEC.")

  c1, c2 = st.columns(2)
  with c1:
    z_humeda = st.checkbox("¿El trabajo incluye zonas húmedas (baño/cocina)?")
    p_std = st.checkbox(
        "¿Se especificó Volcanita Estándar (ST) en zona húmeda?"
    )
    f_sec = st.checkbox("¿Factibilidad Eléctrica aprobada por SEC?")
  with c2:
    p_dom = st.checkbox("¿Permiso DOM verificado?")
    p_tierra = st.checkbox("¿Malla de Puesta a Tierra comprobada?")

  datos_audit = {
      "zona_humeda": z_humeda,
      "placa_std": p_std,
      "factibilidad_sec": f_sec,
      "permiso_dom": p_dom,
      "puesta_tierra": p_tierra,
      "tipo_aislacion": True,
  }

  if st.button("Ejecutar Auditoría Pre-Cotización"):
    completitud, semaforo, alertas = AuditEngine.auditar_proyecto(datos_audit)
    st.divider()
    m1, m2 = st.columns(2)
    m1.metric("Nivel de Cumplimiento", f"{completitud}%")
    m2.metric("Estado del Proyecto", semaforo)

    if alertas:
      st.subheader("Observaciones y Alertas:")
      for a in alertas:
        st.warning(a)
    else:
      st.success("✅ El proyecto cumple con las condiciones técnicas para cotizar.")

elif opcion == "4. APU e Historial de Versiones":
  st.header("💰 Análisis de Precios Unitarios (APU) y Versiones")

  nombre_proyecto = st.text_input(
      "Nombre del Proyecto / Cliente:", "Obra Residencial San Miguel"
  )
  num_version = st.selectbox("Versión de Cotización:", ["V1.0", "V1.1", "V2.0"])

  st.subheader("Tabla Editable de Partidas y Costos")
  datos_apu = pd.DataFrame([
      {
          "Partida": "Estructura Metalcom 60mm",
          "Unidad": "m2",
          "Cantidad": 20,
          "Costo Unitario ($)": 18500,
      },
      {
          "Partida": "Revestimiento Volcanita 12.5mm",
          "Unidad": "m2",
          "Cantidad": 20,
          "Costo Unitario ($)": 8900,
      },
      {
          "Partida": "Instalación Eléctrica Monofásica",
          "Unidad": "gl",
          "Cantidad": 1,
          "Costo Unitario ($)": 150000,
      },
  ])

  df_editado = st.data_editor(
      datos_apu, num_rows="dynamic", use_container_width=True
  )
  df_editado["Total ($)"] = (
      df_editado["Cantidad"] * df_editado["Costo Unitario ($)"]
  )
  monto_total = df_editado["Total ($)"].sum()

  st.metric("Monto Total Cotizado", f"${monto_total:,.0f} CLP")

  obs = st.text_area(
      "Observaciones de la versión:",
      "Cotización inicial sujeto a revisión de terreno.",
  )

  if st.button("Guardar Versión en Base de Datos"):
    guardar_version(
        nombre_proyecto,
        num_version,
        monto_total,
        df_editado.to_dict(orient="records"),
        obs,
    )
    st.success(
        f"✅ Versión {num_version} guardada correctamente en la base de datos."
    )

  st.divider()
  st.subheader("📜 Historial de Cotizaciones Guardadas")
  df_historial = obtener_historial_versiones()
  if not df_historial.empty:
    st.dataframe(df_historial, use_container_width=True)
  else:
    st.info("No hay cotizaciones guardadas aún en la base de datos.")
