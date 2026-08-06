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
  """Inicializa la estructura relacional de ECOLUZ v2.0."""
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  # Tabla de Proyectos
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            rut TEXT,
            direccion TEXT,
            inspector TEXT,
            fecha_creacion TEXT
        )
    """)

  # Tabla de Versiones de Cotización vinculadas a Proyecto
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones_versiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            proyecto_nombre TEXT,
            version TEXT,
            monto_directo REAL,
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


def crear_proyecto(nombre_cliente, rut, direccion, inspector):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  cursor.execute(
      """
        INSERT INTO proyectos (nombre_cliente, rut, direccion, inspector, fecha_creacion)
        VALUES (?, ?, ?, ?, ?)
    """,
      (nombre_cliente, rut, direccion, inspector, fecha),
  )
  proyecto_id = cursor.lastrowid
  conn.commit()
  conn.close()
  return proyecto_id


def obtener_proyectos():
  conn = sqlite3.connect(DB_NAME)
  try:
    df = pd.read_sql_query(
        "SELECT id, nombre_cliente, rut, direccion, inspector, fecha_creacion"
        " FROM proyectos ORDER BY id DESC",
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
    monto_directo,
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
        INSERT INTO cotizaciones_versiones (proyecto_id, proyecto_nombre, version, monto_directo, pct_gg_utilidad, monto_total, detalles_json, observaciones, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          proyecto_id,
          proyecto_nombre,
          version,
          monto_directo,
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
          "SELECT id, proyecto_nombre, version, monto_directo, pct_gg_utilidad,"
          " monto_total, observaciones, fecha FROM cotizaciones_versiones WHERE"
          " proyecto_id = ? ORDER BY id DESC"
      )
      df = pd.read_sql_query(query, conn, params=(proyecto_id,))
    else:
      query = (
          "SELECT id, proyecto_nombre, version, monto_directo, pct_gg_utilidad,"
          " monto_total, observaciones, fecha FROM cotizaciones_versiones ORDER"
          " BY id DESC"
      )
      df = pd.read_sql_query(query, conn)
  except Exception:
    df = pd.DataFrame()
  conn.close()
  return df


# ==========================================
# 2. MOTOR DE DEPENDENCIAS Y CUBICACIONES (BOM Completo)
# ==========================================
class MaterialDependencyEngine:

  @staticmethod
  def obtener_kit_dependiente(partida_principal, cantidad_m2):
    """Genera el kit completo con insumos principales, secundarios y consumibles."""
    if partida_principal == "Cerámica / Porcelanato":
      return [
          {
              "Item / Insumo": "Adhesivo Cerámico Polvo (Sacos 25kg)",
              "Cantidad": round(cantidad_m2 / 5.0, 2),
              "Unidad": "saco",
              "P. Unitario ($)": 7500,
          },
          {
              "Item / Insumo": "Fragüe para Fraguado",
              "Cantidad": round(cantidad_m2 / 4.0, 2),
              "Unidad": "kg",
              "P. Unitario ($)": 2800,
          },
          {
              "Item / Insumo": "Crucetas / Niveladores de Milímetro",
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
          {
              "Item / Insumo": "Esponja de Limpieza y Fraguado",
              "Cantidad": max(1, round(cantidad_m2 / 20.0, 0)),
              "Unidad": "un",
              "P. Unitario ($)": 1500,
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
              "Item / Insumo": "Tornillos Framing 8x1/2 Cabeza Lenteja (500 un)",
              "Cantidad": max(1.0, round((cantidad_m2 * 40) / 500, 1)),
              "Unidad": "caja",
              "P. Unitario ($)": 8900,
          },
          {
              "Item / Insumo": "Tornillos Wafer 10x3/4 Autoperforante (500 un)",
              "Cantidad": max(1.0, round((cantidad_m2 * 25) / 500, 1)),
              "Unidad": "caja",
              "P. Unitario ($)": 9500,
          },
          {
              "Item / Insumo": "Aislación Lana de Vidrio R188",
              "Cantidad": round(cantidad_m2 * 1.05, 2),
              "Unidad": "m2",
              "P. Unitario ($)": 3200,
          },
          {
              "Item / Insumo": "Banda Acústica Aislante de Espuma",
              "Cantidad": round(cantidad_m2 * 0.8, 1),
              "Unidad": "mL",
              "P. Unitario ($)": 1100,
          },
      ]

    elif partida_principal == "Volcanita / Placa Yeso-Cartón":
      placas = cantidad_m2 / 2.98
      return [
          {
              "Item / Insumo": "Placas Volcanita RH / ST (1.22x2.44m)",
              "Cantidad": round(placas, 1),
              "Unidad": "placa",
              "P. Unitario ($)": 9800,
          },
          {
              "Item / Insumo": "Tornillos Drywall 6x1 5/8 (Caja 1000 un)",
              "Cantidad": max(1.0, round((placas * 30) / 1000, 1)),
              "Unidad": "caja",
              "P. Unitario ($)": 11500,
          },
          {
              "Item / Insumo": "Masa Junta Lista para Usar (Juntaprop)",
              "Cantidad": round(cantidad_m2 * 1.2, 1),
              "Unidad": "kg",
              "P. Unitario ($)": 1800,
          },
          {
              "Item / Insumo": "Cinta Malla / Papel de Junta",
              "Cantidad": round(cantidad_m2 * 1.2, 1),
              "Unidad": "mL",
              "P. Unitario ($)": 450,
          },
      ]
    return []


# ==========================================
# 3. MOTOR DE AUDITORÍA Y NORMATIVA COMPLETO
# ==========================================
class AuditEngine:

  @staticmethod
  def auditar_proyecto(datos):
    alertas = []
    campos_requeridos = [
        "permiso_dom",
        "factibilidad_sec",
        "tipo_aislacion",
        "espesor_metalcom",
        "color_frague",
        "pendiente_piso",
        "puesta_tierra",
    ]

    completados = sum(
        1 for c in campos_requeridos if datos.get(c) is not None and datos.get(c) != ""
    )
    porcentaje = int((completados / len(campos_requeridos)) * 100)

    # Incompatibilidades técnicas y normativas (OGUC / SEC)
    if datos.get("zona_humeda") and datos.get("placa_std"):
      alertas.append(
          "🔴 ALERTA OGUC: En zonas húmedas (baños/cocinas) debe usarse"
          " Volcanita RH (Resistente a la Humedad) en lugar de ST (Estándar)."
      )

    if datos.get("partida_cerámica") and not datos.get("tipo_adhesivo"):
      alertas.append(
          "⚠️ FALTANTE TÉCNICO: Se definió instalación de cerámica pero falta"
          " especificar el tipo de adhesivo (Polvo/Pasta)."
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

    if not datos.get("espesor_metalcom"):
      alertas.append(
          "⚠️ ESPECIFICACIÓN STRUCTURAL: Falta especificar el estructural"
          " / espesor perimetral de perfiles Metalcom (0.85mm ó 1.0mm)."
      )

    # Semáforo de estado
    if porcentaje >= 85 and not any("🔴" in a for a in alertas):
      semaforo = "🟢 APTO PARA COTIZAR"
    elif porcentaje >= 60:
      semaforo = "🟡 REQUIERE REVISIÓN TÉCNICA"
    else:
      semaforo = "🔴 NO CONFORME"

    return porcentaje, semaforo, alertas


# ==========================================
# 4. APLICACIÓN Y INTERFAZ DE USUARIO STREAMLIT
# ==========================================
st.set_page_config(
    page_title="ECOLUZ v2.0 - Inspector Técnico", layout="wide", page_icon="🏗️"
)

init_db()

st.title("🏗️ ECOLUZ v2.0 — Inspector Técnico Profesional")
st.caption(
    "Sistema Integral de Inspección de Campo, Cubicaciones (BOM), Auditoría"
    " Normativa Chilena (OGUC/SEC) y Cotizaciones"
)

# Gestión de Proyecto Activo en Sesión
st.sidebar.subheader("📌 Proyecto Activo")
df_proyectos = obtener_proyectos()

if not df_proyectos.empty:
  opciones_proyectos = {
      f"{r['nombre_cliente']} ({r['rut'] or 'Sin RUT'}) - ID: {r['id']}": r["id"]
      for _, r in df_proyectos.iterrows()
  }
  proyecto_seleccionado_label = st.sidebar.selectbox(
      "Seleccionar Proyecto:", list(opciones_proyectos.keys())
  )
  id_proyecto_activo = opciones_proyectos[proyecto_seleccionado_label]
  proyecto_actual_row = df_proyectos[
      df_proyectos["id"] == id_proyecto_activo
  ].iloc[0]
  st.sidebar.success(f"Proyecto Activo ID #{id_proyecto_activo}")
else:
  id_proyecto_activo = None
  proyecto_actual_row = None
  st.sidebar.warning(
      "No hay proyectos registrados. Crea uno en el Módulo 1."
  )

st.sidebar.divider()

opcion = st.sidebar.radio("Módulos del Sistema:", [
    "1. Levantamiento y Factibilidad",
    "2. Motor de Cubicaciones y Kits",
    "3. Auditoría Pre-Cotización",
    "4. APU e Historial de Versiones",
    "5. Cotización Final a Cliente",
])

# ------------------------------------------
# MÓDULO 1: LEVANTAMIENTO Y REGISTRO
# ------------------------------------------
if opcion == "1. Levantamiento y Factibilidad":
  st.header("📋 Módulo 1: Levantamiento Técnico y Factibilidad de Obra")

  with st.expander("➕ Registrar Nuevo Proyecto / Cliente", expanded=True):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
      nuevo_cliente = st.text_input("Nombre del Cliente / Razon Social:")
      nuevo_rut = st.text_input("RUT Cliente:")
    with col_p2:
      nueva_direccion = st.text_input("Dirección de la Obra:")
      nuevo_inspector = st.text_input(
          "Inspector / Profesional a cargo:", "Constructor Civil"
      )

    if st.button("Guardar y Registrar Proyecto"):
      if nuevo_cliente:
        p_id = crear_proyecto(
            nuevo_cliente, nuevo_rut, nueva_direccion, nuevo_inspector
        )
        st.success(
            f"✅ Proyecto '{nuevo_cliente}' creado exitosamente con ID #{p_id}."
        )
        st.rerun()
      else:
        st.error("Por favor ingresa al menos el nombre del cliente.")

  st.divider()
  st.subheader("🔍 Ficha de Inspección Técnica")
  col1, col2 = st.columns(2)

  with col1:
    st.markdown("#### Edificación y DOM")
    rol_propio = st.checkbox("¿Terreno cuenta con Rol propio?")
    permiso_dom = st.checkbox("¿Cuenta con Permiso de Edificación DOM?")
    calculo_estructural = st.checkbox("¿Requiere Cálculo Estructural?")
    espesor_mcom = st.selectbox(
        "Espesores Metalcom requeridos:",
        ["", "Estructura 0.85mm (Normal)", "Estructura 1.0mm (Estructural)"],
    )

  with col2:
    st.markdown("#### Servicios y Normativa SEC")
    tipo_empalme = st.selectbox(
        "Tipo de Empalme Existente:",
        ["Monofásico (1Ф)", "Trifásico (3Ф)", "Sin Empalme / Factibilidad"],
    )
    puesta_tierra = st.checkbox("¿Cuenta con Malla de Puesta a Tierra y Tablero SEC?")
    factibilidad_sec = st.checkbox("¿Factibilidad Eléctrica Aprobada por SEC?")

  st.markdown("#### Detalles de Partidas en Terreno")
  col_det1, col_det2, col_det3 = st.columns(3)
  with col_det1:
    zona_humeda = st.checkbox("¿Se ejecutará en zona húmeda (baño/cocina)?")
    placa_std = st.checkbox("¿Se especificó Volcanita ST (Estándar)?")
  with col_det2:
    partida_cer = st.checkbox("¿Incluye partida de Cerámica / Porcelanato?")
    tipo_adh = st.selectbox("Tipo Adhesivo Cerámico:", ["", "Polvo", "Pasta"])
  with col_det3:
    pendiente_piso = st.text_input("Pendiente de piso registrada (%):", "1.5%")
    color_frague = st.text_input("Color / Tipo Fragüe definido:", "Gris / Beige")

  # Guardar estado en sesión
  st.session_state["inspection_data"] = {
      "permiso_dom": permiso_dom,
      "factibilidad_sec": factibilidad_sec,
      "puesta_tierra": puesta_tierra,
      "espesor_metalcom": espesor_mcom,
      "zona_humeda": zona_humeda,
      "placa_std": placa_std,
      "partida_cerámica": partida_cer,
      "tipo_adhesivo": tipo_adh,
      "color_frague": color_frague,
      "pendiente_piso": pendiente_piso,
      "tipo_aislacion": "Lana de Vidrio R188",
  }

# ------------------------------------------
# MÓDULO 2: CUBICACIONES AUTOMÁTICAS (BOM)
# ------------------------------------------
elif opcion == "2. Motor de Cubicaciones y Kits":
  st.header("📦 Módulo 2: Motor de Cubicaciones e Insumos (BOM)")
  st.write(
      "Selecciona la partida principal y el metraje. El motor calculará"
      " automáticamente todos los insumos secundarios, fijaciones y"
      " consumibles."
  )

  partida = st.selectbox(
      "Seleccione Partida Principal a Cubicar:",
      [
          "Cerámica / Porcelanato",
          "Estructura Metalcom",
          "Volcanita / Placa Yeso-Cartón",
      ],
  )
  m2 = st.number_input(
      "Superficie o Metraje a ejecutar (m²):", min_value=1.0, value=25.0
  )

  if st.button("Generar Kit Completo de Materiales"):
    insumos = MaterialDependencyEngine.obtener_kit_dependiente(partida, m2)
    df_insumos = pd.DataFrame(insumos)
    df_insumos["Subtotal ($)"] = (
        df_insumos["Cantidad"] * df_insumos["P. Unitario ($)"]
    )

    st.success(
        f"Kit completo generado para **{m2} m²** de **{partida}**:"
    )
    st.dataframe(df_insumos, use_container_width=True)

    total_bom = df_insumos["Subtotal ($)"].sum()
    st.metric("Total Materiales e Insumos Kit ($)", f"${total_bom:,.0f} CLP")

    # Guardar kit en sesión para APU
    st.session_state["ultimo_bom"] = df_insumos

# ------------------------------------------
# MÓDULO 3: AUDITORÍA PRE-COTIZACIÓN
# ------------------------------------------
elif opcion == "3. Auditoría Pre-Cotización":
  st.header("🔍 Módulo 3: Auditoría e Inspección Pre-Cotización")
  st.write(
      "Evaluación técnica automatizada de factibilidad, incompatibilidades y"
      " cumplimiento de normativas OGUC y SEC."
  )

  datos_evaluar = st.session_state.get(
      "inspection_data",
      {
          "permiso_dom": True,
          "factibilidad_sec": False,
          "puesta_tierra": False,
          "espesor_metalcom": "Estructura 0.85mm (Normal)",
          "zona_humeda": True,
          "placa_std": True,
          "partida_cerámica": True,
          "tipo_adhesivo": "",
          "color_frague": "Gris",
          "pendiente_piso": "1%",
          "tipo_aislacion": "Lana de Vidrio R188",
      },
  )

  if st.button("Ejecutar Auditoría del Proyecto"):
    completitud, semaforo, alertas = AuditEngine.auditar_proyecto(datos_evaluar)

    st.divider()
    m1, m2 = st.columns(2)
    m1.metric("Índice de Completitud de Levantamiento", f"{completitud}%")
    m2.metric("Semáforo Normativo y Técnico", semaforo)

    st.subheader("Resultados y Observaciones de Inspección:")
    if alertas:
      for alerta in alertas:
        if "🔴" in alerta:
          st.error(alerta)
        else:
          st.warning(alerta)
    else:
      st.success(
          "✅ El proyecto cumple con la totalidad de exigencias normativas"
          " para cotizar."
      )

# ------------------------------------------
# MÓDULO 4: APU E HISTORIAL DE VERSIONES
# ------------------------------------------
elif opcion == "4. APU e Historial de Versiones":
  st.header("💰 Módulo 4: Análisis de Precios Unitarios (APU) y Versiones")

  if proyecto_actual_row is not None:
    st.info(
        f"Proyecto Activo: **{proyecto_actual_row['nombre_cliente']}** | ID:"
        f" {id_proyecto_activo}"
    )
  else:
    st.warning("⚠️ No hay un proyecto seleccionado en la barra lateral.")

  col_v1, col_v2 = st.columns(2)
  with col_v1:
    nom_proj_input = st.text_input(
        "Nombre Proyecto / Referencia:",
        proyecto_actual_row["nombre_cliente"]
        if proyecto_actual_row is not None
        else "Obra San Miguel",
    )
  with col_v2:
    num_version = st.selectbox(
        "Versión de Cotización:", ["V1.0", "V1.1", "V2.0", "V3.0"]
    )

  st.subheader("Tabla Editable de Partidas, Mano de Obra y Costo Directo")

  datos_apu_inicial = pd.DataFrame([
      {
          "Partida": "Estructura Metalcom 60mm",
          "Unidad": "m2",
          "Cantidad": 25.0,
          "Costo Unitario ($)": 18500,
      },
      {
          "Partida": "Revestimiento Volcanita 12.5mm",
          "Unidad": "m2",
          "Cantidad": 25.0,
          "Costo Unitario ($)": 8900,
      },
      {
          "Partida": "Instalación Eléctrica Monofásica",
          "Unidad": "gl",
          "Cantidad": 1.0,
          "Costo Unitario ($)": 180000,
      },
      {
          "Partida": "Mano de Obra Especializada",
          "Unidad": "gl",
          "Cantidad": 1.0,
          "Costo Unitario ($)": 350000,
      },
  ])

  df_apu_editado = st.data_editor(
      datos_apu_inicial, num_rows="dynamic", use_container_width=True
  )
  df_apu_editado["Total Partida ($)"] = (
      df_apu_editado["Cantidad"] * df_apu_editado["Costo Unitario ($)"]
  )

  costo_directo_total = df_apu_editado["Total Partida ($)"].sum()
  st.metric("Costo Directo Total (APU)", f"${costo_directo_total:,.0f} CLP")

  pct_gg_input = st.slider(
      "% Gastos Generales y Utilidad:", 0, 50, 25, key="apu_gg"
  )
  total_con_gg = costo_directo_total * (1 + pct_gg_input / 100.0)

  obs_vers = st.text_area(
      "Observaciones de la versión:",
      "Presupuesto inicial con mano de obra e insumos.",
  )

  if st.button("Guardar Versión en Base de Datos"):
    guardar_version(
        id_proyecto_activo or 1,
        nom_proj_input,
        num_version,
        costo_directo_total,
        pct_gg_input,
        total_con_gg,
        df_apu_editado.to_dict(orient="records"),
        obs_vers,
    )
    st.success(f"✅ Versión {num_version} guardada correctamente en SQLite.")

  st.divider()
  st.subheader("📜 Historial de Cotizaciones Guardadas para el Proyecto")
  df_hist = obtener_historial_versiones(id_proyecto_activo)
  if not df_hist.empty:
    st.dataframe(df_hist, use_container_width=True)
  else:
    st.info("No hay cotizaciones guardadas para este proyecto aún.")

# ------------------------------------------
# MÓDULO 5: COTIZACIÓN FINAL A CLIENTE
# ------------------------------------------
elif opcion == "5. Cotización Final a Cliente":
  st.header("📄 Módulo 5: Generador de Cotización Comercial a Cliente")

  # Datos del cliente importados del proyecto activo o manuales
  cli_def = (
      proyecto_actual_row["nombre_cliente"]
      if proyecto_actual_row is not None
      else "Juan Pérez"
  )
  rut_def = (
      proyecto_actual_row["rut"]
      if proyecto_actual_row is not None
      else "12.345.678-9"
  )
  dir_def = (
      proyecto_actual_row["direccion"]
      if proyecto_actual_row is not None
      else "Av. Las Condes 1234, Santiago"
  )

  col_c1, col_c2 = st.columns(2)
  with col_c1:
    cli_nombre = st.text_input("Nombre del Cliente:", cli_def)
    cli_rut = st.text_input("RUT Cliente:", rut_def)
    dir_obra = st.text_input("Dirección de la Obra:", dir_def)
  with col_c2:
    fec_emision = st.date_input("Fecha de Emisión:")
    validez_dias = st.number_input("Validez de Oferta (Días):", value=15)
    plazo_ejec = st.text_input(
        "Plazo de Ejecución Estimado:", "12 días hábiles"
    )

  st.divider()
  st.subheader("💰 Configuración Financiera y Desglose")

  col_f1, col_f2, col_f3 = st.columns(3)
  with col_f1:
    monto_directo_base = st.number_input(
        "Costo Directo Base ($ CLP):", min_value=0, value=1215000, step=25000
    )
  with col_f2:
    gg_util_pct = st.slider(
        "% Gastos Generales + Utilidad:", 0, 50, 25, key="mod5_gg"
    )
  with col_f3:
    aplica_iva = st.checkbox("Incluir IVA (19%)", value=True)

  # Cálculos
  monto_gg_util = monto_directo_base * (gg_util_pct / 100.0)
  subtotal_neto = monto_directo_base + monto_gg_util
  monto_iva = subtotal_neto * 0.19 if aplica_iva else 0.0
  total_final = subtotal_neto + monto_iva

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Costo Directo", f"${monto_directo_base:,.0f} CLP")
  m2.metric(f"GG & Utilidad ({gg_util_pct}%)", f"${monto_gg_util:,.0f} CLP")
  m3.metric("Neto Subtotal", f"${subtotal_neto:,.0f} CLP")
  m4.metric("TOTAL CLIENTE", f"${total_final:,.0f} CLP")

  st.divider()
  st.subheader("📋 Propuesta Formal Comercial")

  propuesta_text = f"""
    ### **COTIZACIÓN DE SERVICIOS TÉCNICOS Y CONSTRUCCIÓN**
    **ECOLUZ Inspecciones & Construcción**
    
    * **Cliente:** {cli_nombre} | **RUT:** {cli_rut}
    * **Ubicación Obra:** {dir_obra}
    * **Fecha:** {fec_emision.strftime('%d/%m/%Y')}
    * **Validez de la Oferta:** {validez_dias} días hábiles
    * **Plazo de Ejecución Estimado:** {plazo_ejec}
    
    ---
    
    #### **DESGLOSE DE VALORES DE LA OFERTA**
    * **Costo Directo e Insumos:** ${monto_directo_base:,.0f} CLP
    * **Subtotal Neto:** ${subtotal_neto:,.0f} CLP
    * **IVA (19%):** ${monto_iva:,.0f} CLP
    * **OFERTA TOTAL CLIENTE:** **${total_final:,.0f} CLP**
    
    ---
    
    #### **CONDICIONES COMERCIALES**
    1. **Forma de Pago:** 50% de anticipo al inicio de obras y 50% contra recepción conforme.
    2. **Materiales:** Incluye suministro, traslados y montaje de acuerdo a la especificación acordada.
    3. **Cumplimiento Normativo:** Trabajos ejecutados bajo normativa OGUC y normas eléctricas SEC.
    """

  st.info(propuesta_text)

  df_export = pd.DataFrame([{
      "Cliente": cli_nombre,
      "RUT": cli_rut,
      "Direccion": dir_obra,
      "Fecha": fec_emision,
      "Costo_Directo_CLP": monto_directo_base,
      "Subtotal_Neto_CLP": subtotal_neto,
      "IVA_19_CLP": monto_iva,
      "Total_Final_CLP": total_final,
      "Plazo": plazo_ejec,
  }])

  st.download_button(
      label="📥 Descargar Cotización Resumida (CSV)",
      data=df_export.to_csv(index=False).encode("utf-8"),
      file_name=f"cotizacion_{cli_nombre.replace(' ', '_')}.csv",
      mime="text/csv",
  )
