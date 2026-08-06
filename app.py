import json
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# 1. BASE DE DATOS LOCAL (SQLite Completa)
# ==========================================
DB_NAME = "ecoluz.db"


def init_db():
  """Inicializa la base de datos con tablas de proyectos e historial de cotizaciones."""
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            rut TEXT,
            direccion TEXT,
            inspector TEXT,
            especialidad TEXT,
            fecha_creacion TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones_versiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            proyecto_nombre TEXT,
            version TEXT,
            costo_directo REAL,
            pct_gg_utilidad REAL,
            monto_total REAL,
            detalles_json TEXT,
            observaciones TEXT,
            fecha TEXT,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos (id)
        )
    """)

  conn.commit()
  conn.close()


def crear_proyecto(nombre_cliente, rut, direccion, inspector, especialidad):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  cursor.execute(
      """
        INSERT INTO proyectos (nombre_cliente, rut, direccion, inspector, especialidad, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
      (nombre_cliente, rut, direccion, inspector, especialidad, fecha),
  )
  proyecto_id = cursor.lastrowid
  conn.commit()
  conn.close()
  return proyecto_id


def obtener_proyectos():
  conn = sqlite3.connect(DB_NAME)
  try:
    df = pd.read_sql_query(
        "SELECT id, nombre_cliente, rut, direccion, inspector, especialidad,"
        " fecha_creacion FROM proyectos ORDER BY id DESC",
        conn,
    )
  except Exception:
    df = pd.DataFrame()
  conn.close()
  return df


def guardar_version(
    proyecto_id,
    proyecto_nombre,
    version,
    costo_directo,
    pct_gg_utilidad,
    monto_total,
    detalles_dict,
    observaciones="",
):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  cursor.execute(
      """
        INSERT INTO cotizaciones_versiones (proyecto_id, proyecto_nombre, version, costo_directo, pct_gg_utilidad, monto_total, detalles_json, observaciones, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          proyecto_id,
          proyecto_nombre,
          version,
          costo_directo,
          pct_gg_utilidad,
          monto_total,
          json.dumps(detalles_dict),
          observaciones,
          fecha_actual,
      ),
  )
  conn.commit()
  conn.close()


def obtener_historial_versiones(proyecto_id=None):
  conn = sqlite3.connect(DB_NAME)
  try:
    if proyecto_id:
      query = (
          "SELECT id, proyecto_nombre, version, costo_directo, pct_gg_utilidad,"
          " monto_total, observaciones, fecha FROM cotizaciones_versiones WHERE"
          " proyecto_id = ? ORDER BY id DESC"
      )
      df = pd.read_sql_query(query, conn, params=(proyecto_id,))
    else:
      query = (
          "SELECT id, proyecto_nombre, version, costo_directo, pct_gg_utilidad,"
          " monto_total, observaciones, fecha FROM cotizaciones_versiones ORDER"
          " BY id DESC"
      )
      df = pd.read_sql_query(query, conn)
  except Exception:
    df = pd.DataFrame()
  conn.close()
  return df


# ==========================================
# 2. MOTOR DE CUBICACIONES MULTICAPA (BOM)
# ==========================================
class AdvancedBOMEngine:

  @staticmethod
  def calcular_metalcom_multicapa(
      m2, placa_ext, aislacion, revest_int, inc_pintura
  ):
    items = [
        {
            "Item / Insumo": "Perfil Montante Metalcom 60x38x0.85mm",
            "Cantidad": round(m2 * 1.25, 1),
            "Unidad": "tira",
            "P. Unitario ($)": 6200,
        },
        {
            "Item / Insumo": "Perfil Canal Metalcom 61x28x0.85mm",
            "Cantidad": round(m2 * 0.55, 1),
            "Unidad": "tira",
            "P. Unitario ($)": 5400,
        },
        {
            "Item / Insumo": "Tornillos Framing 8x1/2 (Caja 500 un)",
            "Cantidad": max(1.0, round((m2 * 45) / 500, 1)),
            "Unidad": "caja",
            "P. Unitario ($)": 8900,
        },
        {
            "Item / Insumo": "Tornillos Wafer 10x3/4 Autoperforante (Caja 500 un)",
            "Cantidad": max(1.0, round((m2 * 25) / 500, 1)),
            "Unidad": "caja",
            "P. Unitario ($)": 9500,
        },
    ]

    if "OSB" in placa_ext:
      items.extend([
          {
              "Item / Insumo": "Placa Estructural OSB 11.1mm (1.22x2.44m)",
              "Cantidad": round(m2 / 2.98, 1),
              "Unidad": "placa",
              "P. Unitario ($)": 12500,
          },
          {
              "Item / Insumo": "Membrana Aislante Humedad (Tyvek / Fieltro)",
              "Cantidad": round(m2 * 1.1, 1),
              "Unidad": "m2",
              "P. Unitario ($)": 1800,
          },
          {
              "Item / Insumo": (
                  "Revestimiento Exterior Metalsiding / Siding Vinyl"
              ),
              "Cantidad": round(m2 * 1.05, 1),
              "Unidad": "m2",
              "P. Unitario ($)": 14500,
          },
      ])

    items.append({
        "Item / Insumo": f"Aislación Termoacústica ({aislacion})",
        "Cantidad": round(m2 * 1.05, 1),
        "Unidad": "m2",
        "P. Unitario ($)": 3800,
    })

    items.extend([
        {
            "Item / Insumo": f"Placa Interior ({revest_int})",
            "Cantidad": round(m2 / 2.98, 1),
            "Unidad": "placa",
            "P. Unitario ($)": 9800,
        },
        {
            "Item / Insumo": "Masa Junta Lista y Cinta Malla Muro",
            "Cantidad": round(m2 * 1.2, 1),
            "Unidad": "kg",
            "P. Unitario ($)": 2100,
        },
    ])

    if inc_pintura:
      items.append({
          "Item / Insumo": "Esmalte al Agua / Óleo Opaco (Tineta)",
          "Cantidad": max(1.0, round(m2 / 40.0, 1)),
          "Unidad": "tineta",
          "P. Unitario ($)": 42000,
      })

    return items

  @staticmethod
  def calcular_techumbre(m2, tipo_cubierta, hojalateria, aislam_techo):
    items = [
        {
            "Item / Insumo": "Estructura Cerchas Metalcom / Madera",
            "Cantidad": round(m2 * 1.3, 1),
            "Unidad": "m2",
            "P. Unitario ($)": 11500,
        },
        {
            "Item / Insumo": "Placa OSB Techo 15mm",
            "Cantidad": round(m2 / 2.98, 1),
            "Unidad": "placa",
            "P. Unitario ($)": 15800,
        },
        {
            "Item / Insumo": "Fieltro Asfáltico 15 Lbs",
            "Cantidad": round(m2 * 1.15, 1),
            "Unidad": "m2",
            "P. Unitario ($)": 1200,
        },
        {
            "Item / Insumo": f"Cubierta ({tipo_cubierta})",
            "Cantidad": round(m2 * 1.08, 1),
            "Unidad": "m2",
            "P. Unitario ($)": 12800,
        },
    ]
    if hojalateria:
      items.append({
          "Item / Insumo": "Hojalatería Canaletas y Caballetes Zn",
          "Cantidad": round(m2 * 0.3, 1),
          "Unidad": "mL",
          "P. Unitario ($)": 8500,
      })
    items.append({
        "Item / Insumo": f"Aislamiento Cielos ({aislam_techo})",
        "Cantidad": round(m2 * 1.05, 1),
        "Unidad": "m2",
        "P. Unitario ($)": 3500,
    })
    return items

  @staticmethod
  def calcular_ceramica(m2, tipo_adhesivo, color_frague):
    return [
        {
            "Item / Insumo": "Cerámica / Porcelanato Seleccionado",
            "Cantidad": round(m2 * 1.08, 1),
            "Unidad": "m2",
            "P. Unitario ($)": 12900,
        },
        {
            "Item / Insumo": f"Adhesivo Cerámico ({tipo_adhesivo}) Saco 25kg",
            "Cantidad": round(m2 / 5.0, 1),
            "Unidad": "saco",
            "P. Unitario ($)": 7800,
        },
        {
            "Item / Insumo": f"Fragüe Impermeable ({color_frague})",
            "Cantidad": round(m2 / 4.0, 1),
            "Unidad": "kg",
            "P. Unitario ($)": 2900,
        },
        {
            "Item / Insumo": "Crucetas y Niveladores de Milímetro",
            "Cantidad": round(m2 * 20, 0),
            "Unidad": "un",
            "P. Unitario ($)": 35,
        },
        {
            "Item / Insumo": "Silicona Sanitaria Anti-hongos",
            "Cantidad": max(1.0, round(m2 / 15.0, 1)),
            "Unidad": "tubo",
            "P. Unitario ($)": 4500,
        },
    ]

  @staticmethod
  def calcular_electricidad(puntos, empalme_tipo):
    return [
        {
            "Item / Insumo": "Caja Conduit y Tubería Anillada",
            "Cantidad": puntos * 2,
            "Unidad": "un",
            "P. Unitario ($)": 2200,
        },
        {
            "Item / Insumo": "Cable Libre de Halógeno EVA 2.5mm",
            "Cantidad": puntos * 12,
            "Unidad": "m",
            "P. Unitario ($)": 680,
        },
        {
            "Item / Insumo": "Módulos Enchufe / Interruptor Bticino",
            "Cantidad": puntos,
            "Unidad": "un",
            "P. Unitario ($)": 4500,
        },
        {
            "Item / Insumo": (
                f"Tablero Eléctrico Protecciones ({empalme_tipo})"
            ),
            "Cantidad": 1,
            "Unidad": "gl",
            "P. Unitario ($)": 85000,
        },
        {
            "Item / Insumo": "Kit Malla Puesta a Tierra SEC",
            "Cantidad": 1,
            "Unidad": "gl",
            "P. Unitario ($)": 65000,
        },
    ]

  @staticmethod
  def calcular_generico(m2, especialidad):
    return [
        {
            "Item / Insumo": f"Insumo Principal {especialidad}",
            "Cantidad": round(m2 * 1.0, 1),
            "Unidad": "un",
            "P. Unitario ($)": 15000,
        },
        {
            "Item / Insumo": "Insumos Secundarios y Fijaciones",
            "Cantidad": round(m2 * 0.5, 1),
            "Unidad": "gl",
            "P. Unitario ($)": 6500,
        },
        {
            "Item / Insumo": "Consumibles de Montaje",
            "Cantidad": 1.0,
            "Unidad": "gl",
            "P. Unitario ($)": 25000,
        },
    ]


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
        "puesta_tierra",
        "espesor_metalcom",
        "zona_humeda",
        "placa_std",
    ]

    completados = sum(
        1 for c in campos if datos.get(c) is not None and datos.get(c) != ""
    )
    porcentaje = int((completados / len(campos)) * 100)

    if datos.get("zona_humeda") and datos.get("placa_std"):
      alertas.append(
          "🔴 NORMATIVA OGUC: En zonas húmedas (baños/cocinas) debe usarse"
          " Volcanita RH (Resistente a Humedad) en lugar de ST (Estándar)."
      )

    if not datos.get("factibilidad_sec"):
      alertas.append(
          "⚠️ NORMATIVA SEC: Falta verificación de capacidad en empalme o"
          " declaración TE1."
      )

    if not datos.get("puesta_tierra"):
      alertas.append(
          "🔴 NORMATIVA SEC: No se ha verificado la existencia de Malla de"
          " Puesta a Tierra en la instalación eléctrica."
      )

    if not datos.get("permiso_dom"):
      alertas.append(
          "⚠️ REGULARIZACIÓN DOM: Proyecto sin verificación de Permiso de"
          " Edificación ante la Dirección de Obras Municipales."
      )

    if porcentaje >= 80 and not any("🔴" in a for a in alertas):
      semaforo = "🟢 APTO PARA COTIZAR"
    elif porcentaje >= 50:
      semaforo = "🟡 REQUIERE REVISIÓN TÉCNICA"
    else:
      semaforo = "🔴 NO CONFORME"

    return porcentaje, semaforo, alertas


# ==========================================
# 4. APLICACIÓN Y NAVEGACIÓN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="ECOLUZ v2.0 - Inspector & Cubicaciones",
    layout="wide",
    page_icon="🏗️",
)

init_db()

st.title("🏗️ ECOLUZ v2.0 — Inspector Técnico & Sistema de Presupuestos")

# Menú Lateral Principal
st.sidebar.title("📋 Módulo de Trabajo")
fase = st.sidebar.radio(
    "Seleccione Fase:",
    [
        "1. Configuración Técnica y Cubicaciones",
        "2. Registro Fotográfico y Planos",
        "3. Especificaciones Técnicas Detalladas (E.T.)",
        "4. Análisis de Precios Unitarios (APU)",
        "5. Cierre Económico y Presupuesto",
    ],
)

st.sidebar.divider()

# Selector y Gestión de Proyecto Activo
st.sidebar.subheader("📌 Proyecto en Ejecución")
df_proys = obtener_proyectos()
if not df_proys.empty:
  opciones_p = {
      f"{r['nombre_cliente']} ({r['rut'] or 'Sin RUT'}) - ID: {r['id']}": r["id"]
      for _, r in df_proys.iterrows()
  }
  proy_sel = st.sidebar.selectbox("Proyecto Activo:", list(opciones_p.keys()))
  proy_id_activo = opciones_p[proy_sel]
  proy_row = df_proys[df_proys["id"] == proy_id_activo].iloc[0]
  st.sidebar.success(f"Proyecto Activo: #{proy_id_activo}")
else:
  proy_id_activo = None
  proy_row = None
  st.sidebar.warning(
      "No hay proyectos activos. Registra uno en la Fase 1."
  )

# -----------------------------------------------------------------------------
# FASE 1: CONFIGURACIÓN TÉCNICA Y CUBICACIONES (BOM)
# -----------------------------------------------------------------------------
if fase == "1. Configuración Técnica y Cubicaciones":
  st.header("⚙️ Fase 1: Configuración Técnica y Cubicaciones")

  with st.expander("➕ Registrar Nuevo Proyecto / Cliente", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
      cliente = st.text_input("Nombre del Cliente / Razón Social:")
      rut = st.text_input("RUT Cliente:")
    with c2:
      direccion = st.text_input("Dirección de la Obra:")
      inspector = st.text_input(
          "Inspector / Profesional A Cargo:", "Constructor Civil"
      )
      esp_p = st.text_input("Especialidad General:", "Construcción / Montaje")

    if st.button("Guardar y Registrar Proyecto"):
      if cliente:
        pid = crear_proyecto(cliente, rut, direccion, inspector, esp_p)
        st.success(f"✅ Proyecto registrado correctamente con ID #{pid}")
        st.rerun()

  st.divider()

  especialidades = [
      "🧱 Módulo Completo Metalcom (OSB + Metalsiding + Internit + Cerámicos +"
      " Pintura)",
      "🏠 Techumbre y Cubiertas Completa (Cerchas + OSB Techo + Fieltro/Membrana"
      " + Cubierta + Hojalatería)",
      "⚡ Electricidad y Redes SEC",
      "🧱 Revestimientos Cerámicos y Adhesivos",
      "🎨 Pintura y Cielos",
      "🪵 Carpintería y Tabiquería",
      "📐 Terminaciones Finas y Quincallería",
  ]

  especialidad_sel = st.selectbox(
      "Seleccionar Especialidad o Recinto a Cotizar:", especialidades
  )

  st.subheader(f"⚙️ Cuestionario Técnico Específico: {especialidad_sel}")

  if "Metalcom" in especialidad_sel:
    with st.form("form_metalcom"):
      st.markdown("#### 🧱 Parámetros de la Solución Constructiva Multicapa")
      m2_obra = st.number_input(
          "Superficie Muro / Módulo (m²):", min_value=1.0, value=35.0
      )

      col_a, col_b = st.columns(2)
      with col_a:
        placa_ext = st.selectbox(
            "Placa Estructural Exterior:",
            ["OSB 11.1mm + Metalsiding", "Internit 8mm + Pintura", "Directo Siding"],
        )
        aislacion = st.selectbox(
            "Aislación Termoacústica:",
            ["Lana de Vidrio R188", "Lana Mineral 50mm", "Poliestireno AI 40mm"],
        )
      with col_b:
        revest_int = st.selectbox(
            "Revestimiento Interior:",
            [
                "Volcanita ST 12.5mm",
                "Volcanita RH 12.5mm (Resistente Humedad)",
                "Internit 6mm",
            ],
        )
        inc_pintura = st.checkbox("Incluir Esquema de Pintura Interior", value=True)

      btn_calc = st.form_submit_button("📐 Calcular Cubicación y Generar BOM")

    if btn_calc:
      bom = AdvancedBOMEngine.calcular_metalcom_multicapa(
          m2_obra, placa_ext, aislacion, revest_int, inc_pintura
      )
      df_bom = pd.DataFrame(bom)
      df_bom["Subtotal ($)"] = df_bom["Cantidad"] * df_bom["P. Unitario ($)"]
      st.session_state["current_bom"] = df_bom
      st.success("✅ Cubicación multicapa Metalcom calculada exitosamente.")

  elif "Techumbre" in especialidad_sel:
    with st.form("form_techumbre"):
      st.markdown("#### 🏠 Parámetros de Techumbre y Cubiertas")
      m2_techo = st.number_input(
          "Superficie de Cubierta (m²):", min_value=1.0, value=50.0
      )
      col_t1, col_t2 = st.columns(2)
      with col_t1:
        cubierta_tipo = st.selectbox(
            "Tipo de Cubierta:",
            ["Teja Asfáltica", "Plancha Zinc Alum PV4", "Teja Gravillada"],
        )
        hojalateria = st.checkbox("Incluir Hojalatería Completa", value=True)
      with col_t2:
        aislam_techo = st.selectbox(
            "Aislamiento Cielos:", ["Lana Vidrio 80mm", "Lana Mineral 100mm"]
        )

      btn_calc_tech = st.form_submit_button(
          "📐 Calcular Cubicación de Techumbre"
      )

    if btn_calc_tech:
      bom = AdvancedBOMEngine.calcular_techumbre(
          m2_techo, cubierta_tipo, hojalateria, aislam_techo
      )
      df_bom = pd.DataFrame(bom)
      df_bom["Subtotal ($)"] = df_bom["Cantidad"] * df_bom["P. Unitario ($)"]
      st.session_state["current_bom"] = df_bom
      st.success("✅ Cubicación de techumbre calculada.")

  elif "Cerámicos" in especialidad_sel:
    with st.form("form_ceramica"):
      st.markdown("#### 🧱 Parámetros de Revestimientos Cerámicos")
      m2_cer = st.number_input(
          "Superficie a Revestir (m²):", min_value=1.0, value=20.0
      )
      col_c1, col_c2 = st.columns(2)
      with col_c1:
        tipo_adh = st.selectbox(
            "Tipo de Adhesivo:", ["Polvo Acristalado", "Pasta Bekron", "Bekron DA"]
        )
      with col_c2:
        col_frague = st.selectbox(
            "Color de Fragüe:", ["Gris Perla", "Blanco", "Beige", "Negro"]
        )

      btn_calc_cer = st.form_submit_button("📐 Calcular Cubicación Cerámica")

    if btn_calc_cer:
      bom = AdvancedBOMEngine.calcular_ceramica(m2_cer, tipo_adh, col_frague)
      df_bom = pd.DataFrame(bom)
      df_bom["Subtotal ($)"] = df_bom["Cantidad"] * df_bom["P. Unitario ($)"]
      st.session_state["current_bom"] = df_bom
      st.success("✅ Cubicación de cerámicos calculada.")

  elif "Electricidad" in especialidad_sel:
    with st.form("form_elec"):
      st.markdown("#### ⚡ Parámetros Red Eléctrica SEC")
      puntos_e = st.number_input("Número de Puntos / Centros:", min_value=1, value=12)
      empalme_t = st.selectbox(
          "Tipo de Empalme:", ["Monofásico (1Ф)", "Trifásico (3Ф)"]
      )
      btn_calc_elec = st.form_submit_button("📐 Calcular Materiales Eléctricos")

    if btn_calc_elec:
      bom = AdvancedBOMEngine.calcular_electricidad(puntos_e, empalme_t)
      df_bom = pd.DataFrame(bom)
      df_bom["Subtotal ($)"] = df_bom["Cantidad"] * df_bom["P. Unitario ($)"]
      st.session_state["current_bom"] = df_bom
      st.success("✅ Cubicación eléctrica calculada.")

  else:
    m2_gen = st.number_input(
        "Metraje a ejecutar (m² / mL / gl):", min_value=1.0, value=25.0
    )
    if st.button("📐 Generar Cubicación Estándar"):
      bom = AdvancedBOMEngine.calcular_generico(m2_gen, especialidad_sel)
      df_bom = pd.DataFrame(bom)
      df_bom["Subtotal ($)"] = df_bom["Cantidad"] * df_bom["P. Unitario ($)"]
      st.session_state["current_bom"] = df_bom

  # Muestra del BOM si existe en la sesión
  if "current_bom" in st.session_state:
    st.divider()
    st.subheader("📦 Listado de Materiales e Insumos Cubicados (BOM)")
    st.dataframe(st.session_state["current_bom"], use_container_width=True)
    tot_mat = st.session_state["current_bom"]["Subtotal ($)"].sum()
    st.metric("Total Materiales e Insumos ($)", f"${tot_mat:,.0f} CLP")

# -----------------------------------------------------------------------------
# FASE 2: REGISTRO FOTOGRÁFICO Y PLANOS
# -----------------------------------------------------------------------------
elif fase == "2. Registro Fotográfico y Planos":
  st.header("📷 Fase 2: Registro Fotográfico y Planos de Terreno")
  st.write(
      "Documentación visual de la obra, estado inicial y planos explicativos."
  )

  c_up1, c_up2 = st.columns(2)
  with c_up1:
    fotos = st.file_uploader(
        "Cargar Fotografías de Terreno:",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True,
    )
    if fotos:
      st.success(f"✅ {len(fotos)} imágenes cargadas correctamente.")
  with c_up2:
    planos = st.file_uploader(
        "Cargar Planos / Croquis (PDF o Imagen):",
        type=["pdf", "png", "jpg"],
        accept_multiple_files=True,
    )
    if planos:
      st.info(f"✅ {len(planos)} archivos de plano adjuntados.")

  st.subheader("📝 Bitácora de Hallazgos y Observaciones de Inspección")
  hallazgos = st.text_area(
      "Detalle de terreno y observaciones normativas / estructurales:",
      "Terreno nivelado. Se verifica necesidad de refuerzo en soleras y"
      " adecuación de empalme eléctrico bajo norma SEC TE1.",
  )

# -----------------------------------------------------------------------------
# FASE 3: ESPECIFICACIONES TÉCNICAS (E.T.) Y AUDITORÍA NORMATIVA
# -----------------------------------------------------------------------------
elif fase == "3. Especificaciones Técnicas Detalladas (E.T.)":
  st.header("📄 Fase 3: Especificaciones Técnicas Detalladas & Auditoría")

  st.subheader("🔍 Auditoría e Inspección Normativa (OGUC / SEC)")
  col_a1, col_a2 = st.columns(2)
  with col_a1:
    z_humeda = st.checkbox("¿El trabajo incluye zonas húmedas (baños/cocinas)?")
    p_std = st.checkbox(
        "¿Se especificó Volcanita Estándar (ST) en zona húmeda?"
    )
    f_sec = st.checkbox("¿Factibilidad Eléctrica aprobada por SEC?")
  with col_a2:
    p_dom = st.checkbox("¿Permiso DOM verificado?")
    p_tierra = st.checkbox("¿Malla de Puesta a Tierra comprobada?")
    esp_mcom = st.selectbox(
        "Espesor Perfiles Metalcom:",
        ["0.85mm (Normal)", "1.0mm (Estructural)"],
    )

  datos_audit = {
      "zona_humeda": z_humeda,
      "placa_std": p_std,
      "factibilidad_sec": f_sec,
      "permiso_dom": p_dom,
      "puesta_tierra": p_tierra,
      "espesor_metalcom": esp_mcom,
  }

  if st.button("Ejecutar Auditoría Pre-Cotización"):
    completitud, semaforo, alertas = AuditEngine.auditar_proyecto(datos_audit)
    st.divider()
    m1, m2 = st.columns(2)
    m1.metric("Cumplimiento Inspección", f"{completitud}%")
    m2.metric("Estado Normativo", semaforo)

    if alertas:
      st.subheader("Observaciones y Alertas Normativas:")
      for a in alertas:
        if "🔴" in a:
          st.error(a)
        else:
          st.warning(a)
    else:
      st.success(
          "✅ El proyecto cumple con la totalidad de exigencias técnicas."
      )

  st.divider()
  st.subheader("📄 Memoria de Especificaciones Técnicas (E.T.)")

  et_texto = st.text_area(
      "Redacción de Especificaciones Técnicas (Editable):",
      value="""1. ESTRUCTURA Y MONTAJE:
- Perfilería Metalcom de acero galvanizado según norma NCh203 / NCh2123.
- Distanciamiento de montantes a 40cm eje a eje.
- Fijación mediante tornillos autoperforantes Wafer / Lenteja.

2. AISLACIÓN Y BARRERAS TERMOACÚSTICAS:
- Instalación de barrera de humedad Tyvek / Fieltro 15 Lbs sobre OSB exterior.
- Aislación termoacústica en lana de vidrio R188 en cavidades de muro.

3. NORMATIVA ELÉCTRICA SEC:
- Conductores libres de halógenos en canalización embutida.
- Tablero general con protecciones termomagnéticas y diferenciales norma TE1.""",
      height=250,
  )

  st.download_button(
      "📥 Descargar Especificaciones Técnicas (TXT)",
      data=et_texto,
      file_name="Especificaciones_Tecnicas_ECOLUZ.txt",
  )

# -----------------------------------------------------------------------------
# FASE 4: ANÁLISIS DE PRECIOS UNITARIOS (APU) E HISTORIAL
# -----------------------------------------------------------------------------
elif fase == "4. Análisis de Precios Unitarios (APU)":
  st.header("📊 Fase 4: Análisis de Precios Unitarios (APU)")

  if proy_row is not None:
    st.info(
        f"Proyecto Activo: **{proy_row['nombre_cliente']}** | RUT:"
        f" {proy_row['rut'] or 'N/A'}"
    )

  if "current_bom" in st.session_state:
    costo_bom_mat = st.session_state["current_bom"]["Subtotal ($)"].sum()
  else:
    costo_bom_mat = 550000.0

  st.subheader("Tabla Editable de Costos Directos")

  datos_apu_inicial = pd.DataFrame([
      {
          "Componente": "Materiales e Insumos (BOM)",
          "Unidad": "gl",
          "Cantidad": 1.0,
          "Costo Unitario ($)": costo_bom_mat,
      },
      {
          "Componente": "Mano de Obra Especializada",
          "Unidad": "gl",
          "Cantidad": 1.0,
          "Costo Unitario ($)": costo_bom_mat * 0.75,
      },
      {
          "Componente": "Equipos, Herramientas y Traslados",
          "Unidad": "gl",
          "Cantidad": 1.0,
          "Costo Unitario ($)": 85000.0,
      },
  ])

  df_apu_edit = st.data_editor(
      datos_apu_inicial, num_rows="dynamic", use_container_width=True
  )
  df_apu_edit["Subtotal Componente ($)"] = (
      df_apu_edit["Cantidad"] * df_apu_edit["Costo Unitario ($)"]
  )

  costo_directo_total = df_apu_edit["Subtotal Componente ($)"].sum()
  st.session_state["costo_directo_apu"] = costo_directo_total

  st.metric(
      "💰 COSTO DIRECTO TOTAL (APU)", f"${costo_directo_total:,.0f} CLP"
  )

  col_v1, col_v2 = st.columns(2)
  with col_v1:
    version_tag = st.selectbox(
        "Identificador de Versión:", ["V1.0", "V1.1", "V2.0"]
    )
  with col_v2:
    pct_gg = st.slider("% Gastos Generales + Utilidad:", 0, 50, 25)

  monto_con_gg = costo_directo_total * (1 + pct_gg / 100.0)
  obs_apu = st.text_area(
      "Observaciones de la versión:",
      "APU estructurado con materiales de cubicación y mano de obra.",
  )

  if st.button("💾 Guardar Versión de Cotización en Base de Datos"):
    guardar_version(
        proy_id_activo or 1,
        proy_row["nombre_cliente"] if proy_row is not None else "Proyecto",
        version_tag,
        costo_directo_total,
        pct_gg,
        monto_con_gg,
        df_apu_edit.to_dict(orient="records"),
        obs_apu,
    )
    st.success(f"✅ Versión {version_tag} guardada exitosamente en la base de datos.")

  st.divider()
  st.subheader("📜 Historial de Versiones Registradas")
  df_hist = obtener_historial_versiones(proy_id_activo)
  if not df_hist.empty:
    st.dataframe(df_hist, use_container_width=True)
  else:
    st.info("No hay versiones anteriores guardadas para este proyecto.")

# -----------------------------------------------------------------------------
# FASE 5: CIERRE ECONÓMICO Y COTIZACIÓN FINAL A CLIENTE
# -----------------------------------------------------------------------------
elif fase == "5. Cierre Económico y Presupuesto":
  st.header("💵 Fase 5: Cotización Comercial Final para Cliente")

  cli_nom = (
      proy_row["nombre_cliente"] if proy_row is not None else "Juan Pérez"
  )
  cli_rut = proy_row["rut"] if proy_row is not None else "12.345.678-9"
  cli_dir = (
      proy_row["direccion"]
      if proy_row is not None
      else "Av. Las Condes 1234, Santiago"
  )

  col_c1, col_c2 = st.columns(2)
  with col_c1:
    cliente_f = st.text_input("Nombre del Cliente:", cli_nom)
    rut_f = st.text_input("RUT Cliente:", cli_rut)
    dir_f = st.text_input("Dirección Obra:", cli_dir)
  with col_c2:
    fecha_emision = st.date_input("Fecha Emisión:")
    validez = st.number_input("Validez Oferta (Días):", value=15)
    plazo_dias = st.text_input("Plazo Ejecución Estimado:", "12 días hábiles")

  st.divider()
  st.subheader("⚙️ Parámetros Financieros de la Oferta")

  cd_base_apu = st.session_state.get("costo_directo_apu", 1250000.0)

  col_f1, col_f2, col_f3 = st.columns(3)
  with col_f1:
    costo_directo_final = st.number_input(
        "Costo Directo Base ($ CLP):", min_value=0, value=int(cd_base_apu)
    )
  with col_f2:
    pct_gg_utilidad = st.slider(
        "% Gastos Generales y Utilidad:", 0, 50, 25, key="f5_gg"
    )
  with col_f3:
    incluye_iva = st.checkbox("Incluir IVA (19%)", value=True)

  # Calculadora Financiera
  monto_gg_utilidad = costo_directo_final * (pct_gg_utilidad / 100.0)
  subtotal_neto = costo_directo_final + monto_gg_utilidad
  monto_iva = subtotal_neto * 0.19 if incluye_iva else 0.0
  total_oferta_cliente = subtotal_neto + monto_iva

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Costo Directo", f"${costo_directo_final:,.0f} CLP")
  m2.metric(f"GG & Utilidad ({pct_gg_utilidad}%)", f"${monto_gg_utilidad:,.0f} CLP")
  m3.metric("Subtotal Neto", f"${subtotal_neto:,.0f} CLP")
  m4.metric("TOTAL CLIENTE", f"${total_oferta_cliente:,.0f} CLP")

  st.divider()
  st.subheader("📋 Propuesta Comercial Formal")

  tarjeta_cotizacion = f"""
    ### **COTIZACIÓN DE SERVICIOS TÉCNICOS Y CONSTRUCCIÓN**
    **ECOLUZ Inspecciones & Construcción**
    
    * **Cliente:** {cliente_f} | **RUT:** {rut_f}
    * **Dirección Obra:** {dir_f}
    * **Fecha de Emisión:** {fecha_emision.strftime('%d/%m/%Y')}
    * **Validez de Oferta:** {validez} días hábiles
    * **Plazo de Ejecución:** {plazo_dias}
    
    ---
    
    #### **DESGLOSE DE VALORES**
    * **Costo Directo e Insumos:** ${costo_directo_final:,.0f} CLP
    * **Subtotal Neto Oferta:** ${subtotal_neto:,.0f} CLP
    * **IVA (19%):** ${monto_iva:,.0f} CLP
    * **VALOR TOTAL OFERTA:** **${total_oferta_cliente:,.0f} CLP**
    
    ---
    
    #### **CONDICIONES COMERCIALES Y DE PAGO**
    1. **Forma de Pago:** 50% de anticipo al inicio de obras y 50% contra recepción conforme.
    2. **Materiales:** Incluye suministro e instalación según especificaciones acordadas.
    3. **Inspección y Normativa:** Cumplimiento de normas OGUC y SEC.
    """

  st.info(tarjeta_cotizacion)

  df_exp = pd.DataFrame([{
      "Cliente": cliente_f,
      "RUT": rut_f,
      "Direccion": dir_f,
      "Fecha": fecha_emision,
      "Costo_Directo_CLP": costo_directo_final,
      "Subtotal_Neto_CLP": subtotal_neto,
      "IVA_19_CLP": monto_iva,
      "Total_Oferta_CLP": total_oferta_cliente,
      "Plazo": plazo_dias,
  }])

  st.download_button(
      label="📥 Descargar Cotización Resumida (CSV)",
      data=df_exp.to_csv(index=False).encode("utf-8"),
      file_name=f"cotizacion_{cliente_f.replace(' ', '_')}.csv",
      mime="text/csv",
  )
