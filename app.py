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
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            rut TEXT,
            direccion TEXT,
            inspector TEXT,
            tipo_obra TEXT,
            fecha_creacion TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS factibilidad (
            proyecto_id INTEGER PRIMARY KEY,
            permiso_dom BOOLEAN,
            recepcion_final BOOLEAN,
            fact_agua BOOLEAN,
            alcantarillado BOOLEAN,
            acceso_maquinaria BOOLEAN,
            requiere_arqui BOOLEAN,
            requiere_calculo BOOLEAN,
            requiere_topografia BOOLEAN,
            requiere_suelos BOOLEAN,
            empalme_elec BOOLEAN,
            tipo_empalme TEXT,
            potencia_disponible TEXT,
            aumento_capacidad BOOLEAN,
            puesta_tierra BOOLEAN,
            tablero_conforme BOOLEAN,
            certificado_sec BOOLEAN,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos (id)
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS recintos_levantamiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            nombre_recinto TEXT,
            partida TEXT,
            sistema_constructivo TEXT,
            parametros_json TEXT,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos (id)
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones_versiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
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


def crear_proyecto(
    nombre_cliente, rut, direccion, inspector, tipo_obra="Construcción General"
):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  cursor.execute(
      """
        INSERT INTO proyectos (nombre_cliente, rut, direccion, inspector, tipo_obra, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
      (nombre_cliente, rut, direccion, inspector, tipo_obra, fecha),
  )
  proyecto_id = cursor.lastrowid
  conn.commit()
  conn.close()
  return proyecto_id


def obtener_proyectos():
  conn = sqlite3.connect(DB_NAME)
  try:
    df = pd.read_sql_query(
        "SELECT id, nombre_cliente, rut, direccion, inspector, tipo_obra,"
        " fecha_creacion FROM proyectos ORDER BY id DESC",
        conn,
    )
  except Exception:
    df = pd.DataFrame()
  conn.close()
  return df


def guardar_factibilidad(proyecto_id, datos_f):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT OR REPLACE INTO factibilidad (
            proyecto_id, permiso_dom, recepcion_final, fact_agua, alcantarillado, acceso_maquinaria,
            requiere_arqui, requiere_calculo, requiere_topografia, requiere_suelos, empalme_elec,
            tipo_empalme, potencia_disponible, aumento_capacidad, puesta_tierra, tablero_conforme, certificado_sec
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          proyecto_id,
          datos_f.get("permiso_dom", False),
          datos_f.get("recepcion_final", False),
          datos_f.get("fact_agua", False),
          datos_f.get("alcantarillado", False),
          datos_f.get("acceso_maquinaria", False),
          datos_f.get("requiere_arqui", False),
          datos_f.get("requiere_calculo", False),
          datos_f.get("requiere_topografia", False),
          datos_f.get("requiere_suelos", False),
          datos_f.get("empalme_elec", False),
          datos_f.get("tipo_empalme", "Monofásico"),
          datos_f.get("potencia_disponible", "25A"),
          datos_f.get("aumento_capacidad", False),
          datos_f.get("puesta_tierra", False),
          datos_f.get("tablero_conforme", False),
          datos_f.get("certificado_sec", False),
      ),
  )
  conn.commit()
  conn.close()


def obtener_factibilidad(proyecto_id):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT * FROM factibilidad WHERE proyecto_id = ?", (proyecto_id,)
  )
  row = cursor.fetchone()
  conn.close()
  return row


def guardar_version(
    proyecto_id,
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
        INSERT INTO cotizaciones_versiones (proyecto_id, version, costo_directo, pct_gg_utilidad, monto_total, detalles_json, observaciones, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          proyecto_id,
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


def obtener_historial_versiones(proyecto_id):
  conn = sqlite3.connect(DB_NAME)
  try:
    query = (
        "SELECT id, version, costo_directo, pct_gg_utilidad, monto_total,"
        " observaciones, fecha FROM cotizaciones_versiones WHERE proyecto_id ="
        " ? ORDER BY id DESC"
    )
    df = pd.read_sql_query(query, conn, params=(proyecto_id,))
  except Exception:
    df = pd.DataFrame()
  conn.close()
  return df


# ==========================================
# 2. CATÁLOGOS NORMADOS DE RECINTOS Y PARTIDAS
# ==========================================
LISTA_RECINTOS = [
    "Baño Principal",
    "Baño Visitas",
    "Cocina",
    "Living",
    "Comedor",
    "Dormitorio Principal",
    "Dormitorio 1",
    "Dormitorio 2",
    "Dormitorio 3",
    "Pasillo",
    "Logia",
    "Lavandería",
    "Oficina",
    "Sala de Estar",
    "Bodega",
    "Terraza",
    "Quincho",
    "Patio",
    "Jardín",
    "Piscina",
    "Estacionamiento",
    "Techumbre",
    "Fachada",
    "Cierre Perimetral",
    "Otros",
]

LISTA_PARTIDAS = [
    "Demoliciones",
    "Movimiento de Tierra",
    "Fundaciones",
    "Radier",
    "Sobrelosa",
    "Estructura",
    "Muros",
    "Aislación Térmica",
    "Aislación Acústica",
    "Revestimiento Exterior",
    "Revestimiento Interior",
    "Impermeabilización",
    "Cielos",
    "Techumbre",
    "Cubiertas",
    "Hojalatería",
    "Pisos",
    "Cerámicos",
    "Porcelanatos",
    "Pintura",
    "Electricidad",
    "Iluminación",
    "Corrientes Débiles",
    "Gasfitería",
    "Climatización",
    "Ventilación",
    "Puertas",
    "Ventanas",
    "Muebles",
    "Cubiertas de Cuarzo/Granito",
    "Artefactos",
    "Quincallería",
    "Guardapolvos",
    "Cornisas",
    "Molduras",
    "Terminaciones",
    "Limpieza Final",
]


# ==========================================
# 3. MOTOR DE BIBLIOTECAS TÉCNICAS Y DEPENDENCIAS
# ==========================================
class TechnicalLibraryEngine:

  @staticmethod
  def obtener_materiales_con_dependencias(partida, parametros):
    """Genera la lista de materiales principales, secundarios y consumibles agregando

    automáticamente sus dependencias físicas y normativas.
    """
    materiales = []
    m2 = parametros.get("m2", 10.0)

    # REVESTIMIENTOS CERÁMICOS Y PORCELANATOS
    if partida in ["Cerámicos", "Porcelanatos"]:
      materiales.append({
          "Item / Insumo": f"Revestimiento {partida} Seleccionado",
          "Cantidad": round(m2 * 1.08, 2),
          "Unidad": "m²",
          "Precio Unitario ($)": 13500,
          "Tipo": "Principal",
      })
      # Dependencias automáticas
      tipo_adh = (
          "Bekron DA"
          if parametros.get("es_zona_humeda", False)
          else "Bekron Estándar"
      )
      materiales.append({
          "Item / Insumo": f"Adhesivo Cerámico ({tipo_adh})",
          "Cantidad": round(m2 / 4.5, 1),
          "Unidad": "saco 25kg",
          "Precio Unitario ($)": 8200,
          "Tipo": "Dependiente Obligatorio",
      })
      materiales.append({
          "Item / Insumo": "Fragüe Impermeable Anti-Hongos",
          "Cantidad": round(m2 / 4.0, 1),
          "Unidad": "kg",
          "Precio Unitario ($)": 2800,
          "Tipo": "Dependiente Obligatorio",
      })
      materiales.append({
          "Item / Insumo": "Crucetas y Niveladores de Milímetro",
          "Cantidad": round(m2 * 25, 0),
          "Unidad": "unidades",
          "Precio Unitario ($)": 35,
          "Tipo": "Accesorio",
      })
      materiales.append({
          "Item / Insumo": "Cuñas de Ajuste y Nivelación",
          "Cantidad": round(m2 * 10, 0),
          "Unidad": "unidades",
          "Precio Unitario ($)": 25,
          "Tipo": "Accesorio",
      })
      materiales.append({
          "Item / Insumo": "Silicona Sanitaria Anti-hongos (Sellado)",
          "Cantidad": max(1.0, round(m2 / 12.0, 1)),
          "Unidad": "tubo",
          "Precio Unitario ($)": 4800,
          "Tipo": "Consumible",
      })
      materiales.append({
          "Item / Insumo": "Perfil Remate de Terminación (Aluminio/PVC)",
          "Cantidad": round(m2 * 0.4, 1),
          "Unidad": "m",
          "Precio Unitario ($)": 3200,
          "Tipo": "Terminación",
      })

    # SISTEMA ESTRUCTURAL METALCOM
    elif partida == "Estructura" and parametros.get("sistema") == "Metalcom":
      espesor = parametros.get("espesor_metalcom", "0.85mm")
      materiales.append({
          "Item / Insumo": f"Perfil Montante Metalcom 60x38x{espesor}",
          "Cantidad": round(m2 * 1.3, 1),
          "Unidad": "tira 3m",
          "Precio Unitario ($)": 6400,
          "Tipo": "Principal",
      })
      materiales.append({
          "Item / Insumo": f"Perfil Solera/Canal Metalcom 61x28x{espesor}",
          "Cantidad": round(m2 * 0.6, 1),
          "Unidad": "tira 3m",
          "Precio Unitario ($)": 5600,
          "Tipo": "Principal",
      })
      # Dependencias
      materiales.append({
          "Item / Insumo": "Tornillo Framing 8x1/2 Autoperforante",
          "Cantidad": max(1.0, round((m2 * 45) / 500, 1)),
          "Unidad": "caja 500un",
          "Precio Unitario ($)": 8900,
          "Tipo": "Dependiente Obligatorio",
      })
      materiales.append({
          "Item / Insumo": "Tornillo Wafer 10x3/4 Autoperforante",
          "Cantidad": max(1.0, round((m2 * 30) / 500, 1)),
          "Unidad": "caja 500un",
          "Precio Unitario ($)": 9500,
          "Tipo": "Dependiente Obligatorio",
      })
      if parametros.get("incluye_osb", True):
        materiales.append({
            "Item / Insumo": "Placa Estructural OSB 11.1mm (1.22x2.44m)",
            "Cantidad": round(m2 / 2.98, 1),
            "Unidad": "placa",
            "Precio Unitario ($)": 12800,
            "Tipo": "Dependiente Obligatorio",
        })
        materiales.append({
            "Item / Insumo": "Membrana Aislante Humedad Tyvek / Fieltro 15 Lbs",
            "Cantidad": round(m2 * 1.12, 1),
            "Unidad": "m²",
            "Precio Unitario ($)": 1850,
            "Tipo": "Protección",
        })

    # SISTEMA ESTRUCTURAL MADERA
    elif partida == "Estructura" and parametros.get("sistema") == "Madera":
      materiales.append({
          "Item / Insumo": "Pie Derecho Escuadría 2x4 Inmunizada",
          "Cantidad": round(m2 * 1.4, 1),
          "Unidad": "pieza 3.2m",
          "Precio Unitario ($)": 4800,
          "Tipo": "Principal",
      })
      materiales.append({
          "Item / Insumo": "Soleras y Cadenetas Escuadría 2x4",
          "Cantidad": round(m2 * 0.7, 1),
          "Unidad": "pieza 3.2m",
          "Precio Unitario ($)": 4800,
          "Tipo": "Principal",
      })
      materiales.append({
          "Item / Insumo": "Clavos Estructurales 3 y 4 Pulgadas",
          "Cantidad": round(m2 * 0.8, 1),
          "Unidad": "kg",
          "Precio Unitario ($)": 2400,
          "Tipo": "Dependiente Obligatorio",
      })

    # ELECTRICIDAD E ILUMINACIÓN
    elif partida in ["Electricidad", "Iluminación"]:
      puntos = parametros.get("puntos", 4)
      materiales.append({
          "Item / Insumo": "Caja Conduit PVC Octogonal/Rectangular",
          "Cantidad": puntos,
          "Unidad": "unidades",
          "Precio Unitario ($)": 1200,
          "Tipo": "Principal",
      })
      materiales.append({
          "Item / Insumo": "Tubería Conduit Rígida/Flexible 20mm",
          "Cantidad": puntos * 3,
          "Unidad": "m",
          "Precio Unitario ($)": 950,
          "Tipo": "Dependiente Obligatorio",
      })
      materiales.append({
          "Item / Insumo": "Conductor EVA Libre de Halógenos 2.5mm²",
          "Cantidad": puntos * 12,
          "Unidad": "m",
          "Precio Unitario ($)": 720,
          "Tipo": "Dependiente Obligatorio",
      })
      materiales.append({
          "Item / Insumo": "Interruptor / Enchufe Modulo Bticino Classia",
          "Cantidad": puntos,
          "Unidad": "unidades",
          "Precio Unitario ($)": 4800,
          "Tipo": "Terminación",
      })

    # IMPERMEABILIZACIÓN
    elif partida == "Impermeabilización":
      materiales.append({
          "Item / Insumo": "Membrana Elástomérica Bi-componente (Especial Zona Húmeda)",
          "Cantidad": round(m2 * 1.15, 1),
          "Unidad": "m²",
          "Precio Unitario ($)": 6800,
          "Tipo": "Principal",
      })
      materiales.append({
          "Item / Insumo": "Banda Estanqueidad Rincones y Pasadas de Cañería",
          "Cantidad": round(m2 * 0.5, 1),
          "Unidad": "m",
          "Precio Unitario ($)": 2900,
          "Tipo": "Dependiente Obligatorio",
      })

    # PARTIDA GENÉRICA
    else:
      materiales.append({
          "Item / Insumo": f"Materiales e Insumos Directos ({partida})",
          "Cantidad": round(m2 * 1.0, 1),
          "Unidad": "gl",
          "Precio Unitario ($)": 12500,
          "Tipo": "Principal",
      })

    return materiales


# ==========================================
# 4. MOTOR DE AUDITORÍA Y REVISIÓN TÉCNICA FINAL
# ==========================================
class AdvancedAuditEngine:

  @staticmethod
  def auditar_levantamiento_completo(
      proyecto_id, levantamientos_dict, factibilidad_row
  ):
    alertas = []
    verificaciones_exitosas = []
    total_puntos = 0
    puntos_ok = 0

    # 1. Auditoría de Factibilidad Legales y SEC
    if factibilidad_row:
      # Factibilidad Electricidad
      total_puntos += 1
      if factibilidad_row[14]:  # puesta_tierra
        puntos_ok += 1
        verificaciones_exitosas.append(
            "✔ Malla de Puesta a Tierra verificada en terreno."
        )
      else:
        alertas.append(
            "🔴 NORMATIVA SEC: No se ha verificado Malla de Puesta a Tierra"
            " para el circuito eléctrico."
        )

      total_puntos += 1
      if factibilidad_row[10]:  # empalme_elec
        puntos_ok += 1
        verificaciones_exitosas.append(
            "✔ Empalme eléctrico verificado y operativo."
        )
      else:
        alertas.append(
            "⚠️ NORMATIVA SEC: Empalme inexistente o requiere factibilidad de"
            " aumento de capacidad."
        )

      # Factibilidad DOM
      total_puntos += 1
      if factibilidad_row[1]:  # permiso_dom
        puntos_ok += 1
        verificaciones_exitosas.append(
            "✔ Permiso de Edificación DOM verificado."
        )
      else:
        alertas.append(
            "⚠️ REGULARIZACIÓN DOM: Proyecto no registra Permiso de Edificación"
            " ante la DOM."
        )

    # 2. Auditoría Técnica Cruzada por Recintos
    for rec_nombre, partidas in levantamientos_dict.items():
      es_zona_humeda = rec_nombre in [
          "Baño Principal",
          "Baño Visitas",
          "Cocina",
          "Logia",
          "Lavandería",
      ]

      # Regla: Zona Húmeda sin Impermeabilización
      if es_zona_humeda:
        total_puntos += 1
        if "Impermeabilización" in partidas:
          puntos_ok += 1
          verificaciones_exitosas.append(
              f"✔ {rec_nombre}: Impermeabilización especificada correctamente."
          )
        else:
          alertas.append(
              f"🔴 INCONSISTENCIA EN {rec_nombre.upper()}: Es zona húmeda y NO"
              " se ha activado la partida de 'Impermeabilización'."
          )

        # Regla: Revestimiento Interior en Zona Húmeda (Volcanita RH vs ST)
        if "Revestimiento Interior" in partidas:
          total_puntos += 1
          params = partidas["Revestimiento Interior"]
          if params.get("placa") == "Volcanita ST (Estándar)":
            alertas.append(
                f"🔴 NORMATIVA OGUC EN {rec_nombre.upper()}: Se especificó"
                " Volcanita ST. Debe cambiarse por Volcanita RH (Resistente"
                " Humedad)."
            )
          else:
            puntos_ok += 1
            verificaciones_exitosas.append(
                f"✔ {rec_nombre}: Placa de revestimiento interior conforme a"
                " zona húmeda."
            )

      # Regla: Metalcom Estructural sin espesor definido
      if "Estructura" in partidas:
        params = partidas["Estructura"]
        if params.get("sistema") == "Metalcom":
          total_puntos += 1
          if not params.get("espesor_metalcom"):
            alertas.append(
                f"⚠️ ESTRUCTURA EN {rec_nombre.upper()}: No se especificó el"
                " espesor de perfiles Metalcom (0.85mm o 1.0mm)."
            )
          else:
            puntos_ok += 1

      # Regla: Cerámicos definidos pero sin Adhesivo/Fragüe
      if "Cerámicos" in partidas or "Porcelanatos" in partidas:
        total_puntos += 1
        puntos_ok += 1
        verificaciones_exitosas.append(
            f"✔ {rec_nombre}: Materiales dependientes (Adhesivo, Fragüe,"
            " Niveladores) vinculados automáticamente."
        )

    # Cálculo final de completitud
    porcentaje = (
        int((puntos_ok / max(1, total_puntos)) * 100) if total_puntos > 0 else 0
    )

    return porcentaje, alertas, verificaciones_exitosas


# ==========================================
# 5. CONFIGURACIÓN Y NAVEGACIÓN PRINCIPAL
# ==========================================
st.set_page_config(
    page_title="ECOLUZ v2.0 - Inspector Técnico de Obra",
    layout="wide",
    page_icon="🏗️",
)

init_db()

# Session State Initialization
if "levantamiento" not in st.session_state:
  st.session_state["levantamiento"] = {}  # {recinto: {partida: {parametros}}}

st.title("🏗️ ECOLUZ — Plataforma de Inspección Técnica & Presupuestos")

# Navegación del Sistema (Inspirada en flujo ITO)
st.sidebar.title("🧭 Navegación Principal")
seccion = st.sidebar.radio(
    "Ir a:",
    [
        "📌 1. Información General y Factibilidad",
        "🏢 2. Levantamiento por Recintos (ITO)",
        "🔍 3. Auditoría y Revisión Técnica Final",
        "📄 4. Especificación Técnica (E.T.)",
        "📊 5. Análisis de Precios Unitarios (APU)",
        "💵 6. Cotización Comercial y Versionado",
    ],
)

st.sidebar.divider()

# Selector de Proyecto Activo
st.sidebar.subheader("📌 Proyecto en Ejecución")
df_proys = obtener_proyectos()
if not df_proys.empty:
  opciones_p = {
      f"{r['nombre_cliente']} ({r['rut'] or 'Sin RUT'}) - ID: #{r['id']}": r["id"]
      for _, r in df_proys.iterrows()
  }
  proy_sel = st.sidebar.selectbox("Proyecto Activo:", list(opciones_p.keys()))
  proy_id_activo = opciones_p[proy_sel]
  proy_row = df_proys[df_proys["id"] == proy_id_activo].iloc[0]
else:
  proy_id_activo = None
  proy_row = None
  st.sidebar.warning("No hay proyectos activos. Registra uno para comenzar.")

# -----------------------------------------------------------------------------
# SECCIÓN 1: INFORMACIÓN GENERAL Y MÓDULOS DE FACTIBILIDAD
# -----------------------------------------------------------------------------
if seccion == "📌 1. Información General y Factibilidad":
  st.header("📌 Información General del Proyecto y Factibilidades")

  with st.expander("➕ Registrar Nuevo Proyecto / Obra", expanded=False):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
      cliente = st.text_input("Nombre / Razón Social del Cliente:")
      rut = st.text_input("RUT Cliente:")
      direccion = st.text_input("Dirección de la Obra:")
    with col_p2:
      inspector = st.text_input(
          "Inspector Técnico a Cargo (ITO):", "Constructor Civil"
      )
      tipo_obra = st.selectbox(
          "Tipo de Proyecto:",
          ["Construcción Nueva", "Ampliación", "Remodelación / Reforma"],
      )

    if st.button("Crear Proyecto"):
      if cliente:
        pid = crear_proyecto(cliente, rut, direccion, inspector, tipo_obra)
        st.success(f"✅ Proyecto #{pid} creado correctamente.")
        st.rerun()

  if proy_row is not None:
    st.info(
        f"**Proyecto Activo #{proy_id_activo}:** {proy_row['nombre_cliente']} |"
        f" **RUT:** {proy_row['rut']} | **Dirección:** {proy_row['direccion']}"
    )

    tab_doc, tab_fact_const, tab_fact_elec = st.tabs([
        "📂 Documentos y Archivos",
        "🏗️ Factibilidad Construcción",
        "⚡ Factibilidad Eléctrica SEC",
    ])

    with tab_doc:
      col_f1, col_f2 = st.columns(2)
      with col_f1:
        st.file_uploader(
            "📷 Cargar Fotografías de Terreno:",
            accept_multiple_files=True,
            type=["jpg", "png"],
        )
      with col_f2:
        st.file_uploader(
            "📐 Cargar Planos o Dibujos (PDF/CAD):",
            accept_multiple_files=True,
            type=["pdf", "png", "dwg"],
        )
      st.text_area(
          "📝 Observaciones Generales del Terreno:",
          "Terreno cuenta con acceso vial habilitado. Se observa empalme"
          " provisional.",
      )

    row_f = obtener_factibilidad(proy_id_activo)
    f_dict = {}

    with tab_fact_const:
      st.markdown("#### Check-list Obligatorio de Factibilidad Constructiva")
      c_fc1, c_fc2 = st.columns(2)
      with c_fc1:
        f_dict["permiso_dom"] = st.checkbox(
            "¿Existe Permiso de Edificación DOM?",
            value=bool(row_f[1]) if row_f else False,
        )
        f_dict["recepcion_final"] = st.checkbox(
            "¿Existe Recepción Final?", value=bool(row_f[2]) if row_f else False
        )
        f_dict["fact_agua"] = st.checkbox(
            "¿Existe Factibilidad de Agua Potable?",
            value=bool(row_f[3]) if row_f else True,
        )
        f_dict["alcantarillado"] = st.checkbox(
            "¿Existe Red de Alcantarillado?",
            value=bool(row_f[4]) if row_f else True,
        )
        f_dict["acceso_maquinaria"] = st.checkbox(
            "¿Existe Acceso para Maquinaria?",
            value=bool(row_f[5]) if row_f else True,
        )
      with c_fc2:
        f_dict["requiere_arqui"] = st.checkbox(
            "¿Se requiere Arquitecto patrocinante?",
            value=bool(row_f[6]) if row_f else False,
        )
        f_dict["requiere_calculo"] = st.checkbox(
            "¿Se requiere Cálculo Estructural?",
            value=bool(row_f[7]) if row_f else False,
        )
        f_dict["requiere_topografia"] = st.checkbox(
            "¿Se requiere Lev. Topográfico?",
            value=bool(row_f[8]) if row_f else False,
        )
        f_dict["requiere_suelos"] = st.checkbox(
            "¿Se requiere Estudio Mecánica de Suelos?",
            value=bool(row_f[9]) if row_f else False,
        )

    with tab_fact_elec:
      st.markdown("#### Check-list Obligatorio de Factibilidad Eléctrica SEC")
      c_fe1, c_fe2 = st.columns(2)
      with c_fe1:
        f_dict["empalme_elec"] = st.checkbox(
            "¿Existe Empalme Eléctrico?",
            value=bool(row_f[10]) if row_f else True,
        )
        f_dict["tipo_empalme"] = st.selectbox(
            "Tipo de Empalme:",
            ["Monofásico (1Ф)", "Trifásico (3Ф)"],
            index=0 if (not row_f or row_f[11] == "Monofásico") else 1,
        )
        f_dict["potencia_disponible"] = st.text_input(
            "Potencia Disponible / Interruptor Principal:",
            value=row_f[12] if row_f else "25A",
        )
        f_dict["aumento_capacidad"] = st.checkbox(
            "¿Se requiere Aumento de Capacidad?",
            value=bool(row_f[13]) if row_f else False,
        )
      with c_fe2:
        f_dict["puesta_tierra"] = st.checkbox(
            "¿Existe Malla de Puesta a Tierra probada?",
            value=bool(row_f[14]) if row_f else False,
        )
        f_dict["tablero_conforme"] = st.checkbox(
            "¿Tablero General cumple norma TDA?",
            value=bool(row_f[15]) if row_f else True,
        )
        f_dict["certificado_sec"] = st.checkbox(
            "¿Cuenta con Declaración TE1 SEC anterior?",
            value=bool(row_f[16]) if row_f else False,
        )

    if st.button("💾 Guardar Estado de Factibilidad"):
      guardar_factibilidad(proy_id_activo, f_dict)
      st.success("✅ Datos de Factibilidad actualizados.")

# -----------------------------------------------------------------------------
# SECCIÓN 2: LEVANTAMIENTO POR RECINTOS (FLUJO ITO)
# -----------------------------------------------------------------------------
elif seccion == "🏢 2. Levantamiento por Recintos (ITO)":
  st.header("🏢 Levantamiento Técnico por Recintos")
  st.write(
      "Elige el recinto que estás inspeccionando y activa únicamente las"
      " partidas reales del proyecto."
  )

  col_r1, col_r2 = st.columns([1, 2])

  with col_r1:
    recinto_sel = st.selectbox("📌 Seleccionar Recinto:", LISTA_RECINTOS)
    st.info(f"Inspeccionando: **{recinto_sel}**")

    # Mantenimiento del state local
    if recinto_sel not in st.session_state["levantamiento"]:
      st.session_state["levantamiento"][recinto_sel] = {}

    partidas_activas = st.multiselect(
        "🛠️ Activar Partidas para este Recinto:",
        LISTA_PARTIDAS,
        default=list(
            st.session_state["levantamiento"][recinto_sel].keys()
        ),
    )

  with col_r2:
    st.subheader(f"⚙️ Configuración de Partidas — {recinto_sel}")

    if not partidas_activas:
      st.warning(
          "Selecciona al menos una partida en la columna izquierda para iniciar"
          " el cuestionario técnico."
      )

    for p in partidas_activas:
      with st.expander(f"Partida: {p}", expanded=True):
        p_params = st.session_state["levantamiento"][recinto_sel].get(p, {})
        m2_p = st.number_input(
            f"Metraje / Superficie para {p} ({recinto_sel}) [m² / m / un]:",
            min_value=0.1,
            value=float(p_params.get("m2", 12.0)),
            key=f"m2_{recinto_sel}_{p}",
        )
        p_params["m2"] = m2_p

        # SISTEMA CONSTRUCTIVO EN ESTRUCTURAS
        if p == "Estructura":
          sis = st.selectbox(
              f"Sistema Constructivo para Estructura en {recinto_sel}:",
              ["Metalcom", "Madera", "Albañilería", "Hormigón Armado", "Panel SIP"],
              key=f"sis_{recinto_sel}",
          )
          p_params["sistema"] = sis

          if sis == "Metalcom":
            st.markdown("##### 🧱 Biblioteca Técnica: Metalcom")
            p_params["espesor_metalcom"] = st.selectbox(
                "Espesor Perfilería:",
                ["0.85mm (Normal)", "1.0mm (Estructural)"],
                key=f"esp_{recinto_sel}",
            )
            p_params["incluye_osb"] = st.checkbox(
                "Incluir Placa OSB 11.1mm Exterior",
                value=True,
                key=f"osb_{recinto_sel}",
            )

          elif sis == "Madera":
            st.markdown("##### 🪵 Biblioteca Técnica: Madera")
            p_params["escuadria"] = st.selectbox(
                "Escuadria Pie Derecho:",
                ["2x4 Pulgadas", "2x3 Pulgadas"],
                key=f"esc_{recinto_sel}",
            )

        elif p in ["Revestimiento Interior", "Cielos"]:
          p_params["placa"] = st.selectbox(
              f"Tipo de Placa en {recinto_sel}:",
              [
                  "Volcanita ST (Estándar)",
                  "Volcanita RH (Resistente Humedad)",
                  "Volcanita RF (Resistente Fuego)",
                  "Internit 6mm",
              ],
              key=f"plc_{recinto_sel}_{p}",
          )

        p_params["es_zona_humeda"] = recinto_sel in [
            "Baño Principal",
            "Baño Visitas",
            "Cocina",
            "Logia",
            "Lavandería",
        ]

        # Guardar en estado global
        st.session_state["levantamiento"][recinto_sel][p] = p_params

        # Muestra de Materiales y Dependencias Automáticas
        mats_dep = TechnicalLibraryEngine.obtener_materiales_con_dependencias(
            p, p_params
        )
        st.markdown("**Materiales y Dependencias Automáticas:**")
        df_mats = pd.DataFrame(mats_dep)
        st.dataframe(
            df_mats[["Item / Insumo", "Cantidad", "Unidad", "Tipo"]],
            use_container_width=True,
        )

# -----------------------------------------------------------------------------
# SECCIÓN 3: AUDITORÍA Y REVISIÓN TÉCNICA FINAL
# -----------------------------------------------------------------------------
elif seccion == "🔍 3. Auditoría y Revisión Técnica Final":
  st.header("🔍 Auditoría Técnica e Inspección Cruzada Pre-Cotización")
  st.write(
      "El sistema analiza automáticamente inconsistencias normativas (OGUC /"
      " SEC) yOmisiones antes de generar la documentación final."
  )

  fact_row = obtener_factibilidad(proy_id_activo) if proy_id_activo else None
  pct, alertas, ok_list = AdvancedAuditEngine.auditar_levantamiento_completo(
      proy_id_activo, st.session_state["levantamiento"], fact_row
  )

  c_a1, c_a2 = st.columns(2)
  c_a1.metric("Nivel de Completitud e Inspección", f"{pct}%")
  if pct >= 80 and not any("🔴" in a for a in alertas):
    c_a2.success("🟢 ESTADO: CONFORME PARA GENERAR E.T. Y COTIZACIÓN")
  elif pct >= 50:
    c_a2.warning("🟡 ESTADO: REQUIERE AJUSTES TÉCNICOS EN RECINTOS")
  else:
    c_a2.error("🔴 ESTADO: LEVANTAMIENTO INCOMPLETO")

  st.divider()

  if alertas:
    st.subheader("⚠️ Advertencias e Inconsistencias Detectadas:")
    for al in alertas:
      if "🔴" in al:
        st.error(al)
      else:
        st.warning(al)

  if ok_list:
    st.subheader("✔ Verificaciones Técnicas Conformes:")
    for ok in ok_list:
      st.write(ok)

# -----------------------------------------------------------------------------
# SECCIÓN 4: ESPECIFICACIÓN TÉCNICA (E.T.)
# -----------------------------------------------------------------------------
elif seccion == "📄 4. Especificación Técnica (E.T.)":
  st.header("📄 Generación de Especificaciones Técnicas (E.T.)")

  et_lineas = [
      "ESPECIFICACIONES TÉCNICAS GENERALES Y PARTICULARES DE OBRA\nPROYECTO:"
      f" {proy_row['nombre_cliente'] if proy_row is not None else 'General'}\n"
  ]

  for rec, partidas in st.session_state["levantamiento"].items():
    if partidas:
      et_lineas.append(f"\n1. RECINTO: {rec.upper()}")
      for p_nom, p_data in partidas.items():
        et_lineas.append(f"   1.1 Partida: {p_nom}")
        et_lineas.append(f"       - Metraje / Cantidad: {p_data.get('m2')} m²")
        if "sistema" in p_data:
          et_lineas.append(
              f"       - Sistema Constructivo: {p_data.get('sistema')}"
          )
        if "placa" in p_data:
          et_lineas.append(
              f"       - Revestimiento Especificado: {p_data.get('placa')}"
          )

  texto_et_final = "\n".join(et_lineas)

  et_editada = st.text_area(
      "Documento E.T. Editable:", value=texto_et_final, height=350
  )

  st.download_button(
      "📥 Descargar E.T. Completa (.TXT)",
      data=et_editada,
      file_name="Especificaciones_Tecnicas_ECOLUZ.txt",
  )

# -----------------------------------------------------------------------------
# SECCIÓN 5: ANÁLISIS DE PRECIOS UNITARIOS (APU)
# -----------------------------------------------------------------------------
elif seccion == "📊 5. Análisis de Precios Unitarios (APU)":
  st.header("📊 Análisis de Precios Unitarios (APU) Consolidado")

  todos_los_materiales = []

  for rec, partidas in st.session_state["levantamiento"].items():
    for p_nom, p_data in partidas.items():
      mats = TechnicalLibraryEngine.obtener_materiales_con_dependencias(
          p_nom, p_data
      )
      for m in mats:
        m["Recinto"] = rec
        m["Partida"] = p_nom
        m["Subtotal ($)"] = m["Cantidad"] * m["Precio Unitario ($)"]
        todos_los_materiales.append(m)

  if todos_los_materiales:
    df_apu = pd.DataFrame(todos_los_materiales)
    st.subheader("📦 Desglose Consolidado de Materiales e Insumos")
    st.dataframe(
        df_apu[[
            "Recinto",
            "Partida",
            "Item / Insumo",
            "Cantidad",
            "Unidad",
            "Precio Unitario ($)",
            "Subtotal ($)",
            "Tipo",
        ]],
        use_container_width=True,
    )

    costo_materiales_tot = df_apu["Subtotal ($)"].sum()

    st.divider()
    st.subheader("💼 Resumen del Costo Directo por Partida")
    col_c1, col_c2, col_c3 = st.columns(3)
    c_mat = col_c1.number_input(
        "Costo Total Insumos ($ CLP):", value=float(costo_materiales_tot)
    )
    c_mo = col_c2.number_input(
        "Mano de Obra Estimada ($ CLP):", value=float(costo_materiales_tot * 0.8)
    )
    c_eq = col_c3.number_input(
        "Equipos / Herramientas ($ CLP):", value=75000.0
    )

    cd_total = c_mat + c_mo + c_eq
    st.session_state["costo_directo_consolidado"] = cd_total
    st.metric("💰 COSTO DIRECTO TOTAL OBRA", f"${cd_total:,.0f} CLP")
  else:
    st.warning(
        "No se han registrado partidas en los recintos. Ingresa al módulo 2"
        " 'Levantamiento por Recintos'."
    )

# -----------------------------------------------------------------------------
# SECCIÓN 6: COTIZACIÓN Y VERSIONADO
# -----------------------------------------------------------------------------
elif seccion == "💵 6. Cotización Comercial y Versionado":
  st.header("💵 Cierre Económico y Versionado de Cotizaciones")

  cd_base = st.session_state.get("costo_directo_consolidado", 1500000.0)

  col_v1, col_v2, col_v3 = st.columns(3)
  with col_v1:
    v_tag = st.selectbox(
        "Versión de Cotización:", ["Cotización V1", "Cotización V2", "Cotización V3"]
    )
  with col_v2:
    pct_gg = st.slider("% Gastos Generales & Utilidad:", 0, 50, 25)
  with col_v3:
    inc_iva = st.checkbox("Incluir IVA (19%)", value=True)

  # Cálculos
  monto_gg = cd_base * (pct_gg / 100.0)
  subtotal_neto = cd_base + monto_gg
  monto_iva = subtotal_neto * 0.19 if inc_iva else 0.0
  total_final = subtotal_neto + monto_iva

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Costo Directo Base", f"${cd_base:,.0f} CLP")
  m2.metric(f"GG & Utilidad ({pct_gg}%)", f"${monto_gg:,.0f} CLP")
  m3.metric("Neto Oferta", f"${subtotal_neto:,.0f} CLP")
  m4.metric("TOTAL CLIENTE", f"${total_final:,.0f} CLP")

  st.divider()

  obs_ver = st.text_area(
      "Notas / Cambios respecto a la versión anterior:",
      "Versión inicial basada en levantamiento completo por recintos.",
  )

  if st.button("💾 Guardar esta Versión en el Historial del Proyecto"):
    if proy_id_activo:
      guardar_version(
          proy_id_activo,
          v_tag,
          cd_base,
          pct_gg,
          total_final,
          {"Neto": subtotal_neto, "IVA": monto_iva},
          obs_ver,
      )
      st.success(f"✅ {v_tag} guardada en SQLite.")

  st.divider()
  st.subheader("📜 Historial de Versionado y Comparativa de Costos")
  if proy_id_activo:
    df_h = obtener_historial_versiones(proy_id_activo)
    if not df_h.empty:
      st.dataframe(df_h, use_container_width=True)
    else:
      st.info("No hay versiones anteriores guardadas para este proyecto.")
