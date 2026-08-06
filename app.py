import json
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="ECOLUZ - Inspector Técnico & Presupuestos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_NAME = "ecoluz.db"


def get_connection():
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = sqlite3.Row
  return conn


# ==========================================
# 1. BASE DE DATOS Y MIGRACIÓN AUTOMÁTICA
# ==========================================
def init_db():
  conn = get_connection()
  cursor = conn.cursor()

  # 1.1 Tabla de Proyectos
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            rut TEXT,
            direccion TEXT,
            inspector TEXT,
            tipo_obra TEXT DEFAULT 'Construcción Nueva',
            fecha_creacion TEXT
        )
    """)

  # 1.2 Tabla de Factibilidad Ampliada (SSOT - Opción B)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS factibilidad (
            proyecto_id INTEGER PRIMARY KEY,
            permiso_dom BOOLEAN DEFAULT 0,
            recepcion_final BOOLEAN DEFAULT 0,
            fact_agua BOOLEAN DEFAULT 1,
            alcantarillado BOOLEAN DEFAULT 1,
            acceso_maquinaria BOOLEAN DEFAULT 1,
            requiere_arqui BOOLEAN DEFAULT 0,
            requiere_calculo BOOLEAN DEFAULT 0,
            requiere_topografia BOOLEAN DEFAULT 0,
            requiere_suelos BOOLEAN DEFAULT 0,
            empalme_elec BOOLEAN DEFAULT 1,
            tipo_empalme TEXT DEFAULT 'Monofásico (1Ф)',
            potencia_disponible TEXT DEFAULT '25A',
            aumento_capacidad BOOLEAN DEFAULT 0,
            puesta_tierra BOOLEAN DEFAULT 0,
            tablero_conforme BOOLEAN DEFAULT 1,
            certificado_sec BOOLEAN DEFAULT 0,
            suministro_elec BOOLEAN DEFAULT 1,
            potencia_requerida TEXT DEFAULT '40A',
            empresa_distribuidora TEXT DEFAULT 'CGE',
            medidor_existente BOOLEAN DEFAULT 1,
            requiere_nuevo_empalme BOOLEAN DEFAULT 0,
            requiere_proyecto_sec BOOLEAN DEFAULT 0,
            requiere_declaracion_sec BOOLEAN DEFAULT 1,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos (id) ON DELETE CASCADE
        )
    """)

  # Migraciones seguras para tabla factibilidad
  cursor.execute("PRAGMA table_info(factibilidad)")
  col_fact = [c[1] for c in cursor.fetchall()]
  nuevos_campos = [
      ("suministro_elec", "BOOLEAN DEFAULT 1"),
      ("potencia_requerida", "TEXT DEFAULT '40A'"),
      ("empresa_distribuidora", "TEXT DEFAULT 'CGE'"),
      ("medidor_existente", "BOOLEAN DEFAULT 1"),
      ("requiere_nuevo_empalme", "BOOLEAN DEFAULT 0"),
      ("requiere_proyecto_sec", "BOOLEAN DEFAULT 0"),
      ("requiere_declaracion_sec", "BOOLEAN DEFAULT 1"),
  ]
  for campo, tipo in nuevos_campos:
    if campo not in col_fact:
      try:
        cursor.execute(f"ALTER TABLE factibilidad ADD COLUMN {campo} {tipo}")
      except Exception:
        pass

  # 1.3 Tabla de Levantamiento por Recintos (MÓDULO 2)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS recintos_levantamiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            nombre_recinto TEXT NOT NULL,
            puntos_enchufes INTEGER DEFAULT 0,
            centros_iluminacion INTEGER DEFAULT 0,
            interruptores INTEGER DEFAULT 0,
            puntos_fuerza_clima INTEGER DEFAULT 0,
            estado_canalizacion TEXT DEFAULT 'Conforme',
            observaciones_ito TEXT,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos (id) ON DELETE CASCADE
        )
    """)

  # 1.4 Tabla Maestra de Materiales e Insumos (Opción A)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            unidad TEXT NOT NULL,
            precio_unitario REAL NOT NULL DEFAULT 0,
            porcentaje_perdida REAL NOT NULL DEFAULT 5.0
        )
    """)

  # Insertar materiales por defecto si la tabla está vacía
  cursor.execute("SELECT COUNT(*) FROM materiales_master")
  if cursor.fetchone()[0] == 0:
    materiales_semilla = [
        ("MAT-ELE-001", "Cable EVA 2.5mm² Rojo", "Conductores", "m", 650, 5.0),
        ("MAT-ELE-002", "Cable EVA 2.5mm² Blanco", "Conductores", "m", 650, 5.0),
        ("MAT-ELE-003", "Cable EVA 2.5mm² Verde", "Conductores", "m", 650, 5.0),
        (
            "MAT-ELE-004",
            "Módulo Enchufe Doble 10A/16A + Placa",
            "Aparatos",
            "un",
            3800,
            2.0,
        ),
        (
            "MAT-ELE-005",
            "Downlight LED 18W Embutido Borde Blanco",
            "Luminarias",
            "un",
            6900,
            2.0,
        ),
        (
            "MAT-ELE-006",
            "Tubo PVC Conduit 20mm x 3m",
            "Canalizaciones",
            "un",
            1850,
            5.0,
        ),
        (
            "MAT-ELE-007",
            "Caja Chuqui Plástica Embutir",
            "Cajas y Accesorios",
            "un",
            450,
            3.0,
        ),
        (
            "MAT-ELE-008",
            "Interruptor Termomagnético 1x16A 6kA Legrand",
            "Tableros",
            "un",
            5200,
            0.0,
        ),
        (
            "MAT-ELE-009",
            "Interruptor Diferencial 2x25A 30mA Legrand",
            "Tableros",
            "un",
            14900,
            0.0,
        ),
        (
            "MO-ELE-001",
            "H.H. Maestro Eléctrico SEC Clasi F/G",
            "Mano de Obra",
            "HH",
            8500,
            0.0,
        ),
    ]
    cursor.executemany(
        """
            INSERT INTO materiales_master (codigo, nombre, categoria, unidad, precio_unitario, porcentaje_perdida)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        materiales_semilla,
    )

  # 1.5 Tabla de Partidas APU
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas_apu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_partida TEXT NOT NULL,
            nombre_partida TEXT NOT NULL,
            unidad_medida TEXT NOT NULL,
            categoria TEXT NOT NULL
        )
    """)

  cursor.execute("SELECT COUNT(*) FROM partidas_apu")
  if cursor.fetchone()[0] == 0:
    partidas_semilla = [
        (
            "PAR-ELE-01",
            "Punto de Enchufe Doble 16A Embutido",
            "puntu",
            "Electricidad",
        ),
        (
            "PAR-ELE-02",
            "Punto Centro Alumbrado LED Embutido",
            "puntu",
            "Electricidad",
        ),
        (
            "PAR-ELE-03",
            "Provisión y Montaje Tablero TDA 12 Módulos",
            "un",
            "Electricidad",
        ),
    ]
    cursor.executemany(
        """
            INSERT INTO partidas_apu (codigo_partida, nombre_partida, unidad_medida, categoria)
            VALUES (?, ?, ?, ?)
        """,
        partidas_semilla,
    )

  # 1.6 Receta APU (Composición de Partidas)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS apu_receta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            rendimiento REAL NOT NULL,
            FOREIGN KEY (partida_id) REFERENCES partidas_apu(id),
            FOREIGN KEY (material_id) REFERENCES materiales_master(id)
        )
    """)

  cursor.execute("SELECT COUNT(*) FROM apu_receta")
  if cursor.fetchone()[0] == 0:
    recetas_semilla = [
        (1, 4, 1.0),
        (1, 7, 1.0),
        (1, 6, 1.0),
        (1, 1, 3.5),
        (1, 2, 3.5),
        (1, 3, 3.5),
        (1, 10, 0.40),
        (2, 5, 1.0),
        (2, 7, 1.0),
        (2, 6, 1.0),
        (2, 1, 3.0),
        (2, 2, 3.0),
        (2, 3, 3.0),
        (2, 10, 0.35),
        (3, 8, 3.0),
        (3, 9, 1.0),
        (3, 10, 2.00),
    ]
    cursor.executemany(
        """
            INSERT INTO apu_receta (partida_id, material_id, rendimiento)
            VALUES (?, ?, ?)
        """,
        recetas_semilla,
    )

  # 1.7 Historial de Cotizaciones y Versiones
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones_versiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            version TEXT,
            costo_directo REAL,
            pct_gg REAL,
            pct_utilidad REAL,
            monto_total REAL,
            fecha TEXT,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos (id) ON DELETE CASCADE
        )
    """)

  conn.commit()
  conn.close()


# Inicializar base de datos
init_db()

# ==========================================
# 2. NAVEGACIÓN Y PANEL LATERAL
# ==========================================
st.sidebar.image(
    "https://img.icons8.com/color/96/lightning-bolt.png", width=60
)
st.sidebar.title("ECOLUZ v2.0")
st.sidebar.caption("Inspector Técnico & Presupuestos SEC")

# Selección / Creación de Proyecto Activo
conn = get_connection()
proyectos_df = pd.read_sql_query(
    "SELECT id, nombre_cliente, direccion FROM proyectos ORDER BY id DESC", conn
)
conn.close()

if "proyecto_id" not in st.session_state:
  st.session_state["proyecto_id"] = (
      proyectos_df["id"].iloc[0] if not proyectos_df.empty else None
  )

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Proyecto en Ejecución")

if not proyectos_df.empty:
  opciones_proy = {
      row["id"]: f"ID {row['id']} - {row['nombre_cliente']}"
      for _, row in proyectos_df.iterrows()
  }
  proy_sel = st.sidebar.selectbox(
      "Seleccionar Proyecto Activo:",
      options=list(opciones_proy.keys()),
      format_func=lambda x: opciones_proy[x],
      index=0,
  )
  st.session_state["proyecto_id"] = proy_sel
else:
  st.sidebar.warning("No hay proyectos activos. Registra uno para comenzar.")

st.sidebar.markdown("---")
st.sidebar.subheader("Ir a:")
menu_opcion = st.sidebar.radio(
    "Navegación Principal",
    [
        "📌 1. Información General y Factibilidad",
        "📊 2. Levantamiento por Recintos (ITO)",
        "🔍 3. Auditoría y Revisión Técnica Final",
        "📄 4. Especificación Técnica (E.T.)",
        "💰 5. Análisis de Precios Unitarios (APU)",
        "🏷️ 6. Cotización Comercial y Versionado",
    ],
)

proy_id = st.session_state.get("proyecto_id")

# ==========================================
# MÓDULO 1: INFORMACIÓN GENERAL Y FACTIBILIDAD
# ==========================================
if "📌 1. Información General" in menu_opcion:
  st.title("📌 Información General del Proyecto y Factibilidades")

  tab_nuevo, tab_fact_elec, tab_fact_gen = st.tabs([
      "➕ Registrar Nuevo Proyecto / Obra",
      "⚡ Factibilidad Eléctrica SEC (SSOT)",
      "🏗️ Factibilidad General / Permisos",
  ])

  # TAB 1: REGISTRO DE PROYECTO
  with tab_nuevo:
    st.subheader("Registrar Ficha de Obra")
    with st.form("form_nuevo_proyecto"):
      col1, col2 = st.columns(2)
      with col1:
        nom_cliente = st.text_input("Nombre / Razón Social del Cliente:")
        rut_cli = st.text_input("RUT Cliente:")
        dir_obra = st.text_input("Dirección de la Obra:")
      with col2:
        ito_cargo = st.text_input("Inspector Técnico a Cargo (ITO):")
        tipo_obra = st.selectbox(
            "Tipo de Proyecto:",
            [
                "Construcción Nueva",
                "Remodelación / Ampliación",
                "Normalización Eléctrica SEC",
                "Inspección Técnica",
            ],
        )

      btn_crear = st.form_submit_button("Crear Proyecto")
      if btn_crear:
        if nom_cliente:
          conn = get_connection()
          c = conn.cursor()
          c.execute(
              """
                        INSERT INTO proyectos (nombre_cliente, rut, direccion, inspector, tipo_obra, fecha_creacion)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
              (
                  nom_cliente,
                  rut_cli,
                  dir_obra,
                  ito_cargo,
                  tipo_obra,
                  datetime.now().strftime("%Y-%m-%d %H:%M"),
              ),
          )
          nuevo_id = c.lastrowid
          c.execute(
              "INSERT INTO factibilidad (proyecto_id) VALUES (?)", (nuevo_id,)
          )
          conn.commit()
          conn.close()

          st.session_state["proyecto_id"] = nuevo_id
          st.success(f"✅ Proyecto N° {nuevo_id} registrado con éxito.")
          st.rerun()
        else:
          st.error("Por favor ingresa el nombre del cliente.")

  if proy_id:
    conn = get_connection()
    row_f = conn.execute(
        "SELECT * FROM factibilidad WHERE proyecto_id = ?", (proy_id,)
    ).fetchone()
    conn.close()

    # TAB 2: FACTIBILIDAD ELÉCTRICA (OPCIÓN B)
    with tab_fact_elec:
      st.markdown(
          "### ⚡ Check-list Unificado de Factibilidad Eléctrica (RIC / SEC)"
      )
      st.caption(
          "Fuente única de verdad para el estado eléctrico inicial del"
          " proyecto."
      )

      with st.form("form_fact_elec"):
        c_fe1, c_fe2, c_fe3 = st.columns(3)

        with c_fe1:
          st.subheader("1. Red y Suministro")
          sum_elec = st.checkbox(
              "¿Existe suministro eléctrico activo?",
              value=bool(row_f["suministro_elec"]) if row_f else True,
          )
          emp_elec = st.checkbox(
              "¿Existe empalme ejecutado?",
              value=bool(row_f["empalme_elec"]) if row_f else True,
          )
          tipo_emp = st.selectbox(
              "Tipo de Empalme:",
              ["Monofásico (1Ф)", "Trifásico (3Ф)"],
              index=(
                  0
                  if (not row_f or row_f["tipo_empalme"] == "Monofásico (1Ф)")
                  else 1
              ),
          )
          req_emp = st.checkbox(
              "¿Se requiere NUEVO empalme?",
              value=bool(row_f["requiere_nuevo_empalme"]) if row_f else False,
          )
          distrib = st.selectbox(
              "Empresa Distribuidora:",
              [
                  "CGE",
                  "Enel",
                  "Saesa",
                  "Chilquinta",
                  "Frontel",
                  "Luz Linares",
                  "Otra",
              ],
              index=0,
          )

        with c_fe2:
          st.subheader("2. Potencia y Tableros")
          pot_disp = st.text_input(
              "Potencia Instalada / Disyuntor General:",
              value=row_f["potencia_disponible"] if row_f else "25A",
          )
          pot_req = st.text_input(
              "Potencia Requerida por Proyecto:",
              value=row_f["potencia_requerida"] if row_f else "40A",
          )
          aum_cap = st.checkbox(
              "¿Se requiere Aumento de Capacidad?",
              value=bool(row_f["aumento_capacidad"]) if row_f else False,
          )
          medidor = st.checkbox(
              "¿Existe Medidor Instalado?",
              value=bool(row_f["medidor_existente"]) if row_f else True,
          )
          tablero = st.checkbox(
              "¿Tablero TDA cumple norma vigente?",
              value=bool(row_f["tablero_conforme"]) if row_f else True,
          )

        with c_fe3:
          st.subheader("3. Protecciones y SEC")
          puesta_t = st.checkbox(
              "¿Existe Malla/Puesta a Tierra probada?",
              value=bool(row_f["puesta_tierra"]) if row_f else False,
          )
          cert_sec = st.checkbox(
              "¿Cuenta con Declaración TE1 previa?",
              value=bool(row_f["certificado_sec"]) if row_f else False,
          )
          req_proj = st.checkbox(
              "¿Se requiere Proyecto Eléctrico Firmado?",
              value=bool(row_f["requiere_proyecto_sec"]) if row_f else False,
          )
          req_te1 = st.checkbox(
              "¿Se requiere Nueva Declaración TE1 SEC?",
              value=bool(row_f["requiere_declaracion_sec"]) if row_f else True,
          )

        if st.form_submit_button("💾 Guardar Factibilidad Eléctrica"):
          conn = get_connection()
          conn.execute(
              """
              UPDATE factibilidad SET
                  suministro_elec=?, empalme_elec=?, tipo_empalme=?, requiere_nuevo_empalme=?, empresa_distribuidora=?,
                  potencia_disponible=?, potencia_requerida=?, aumento_capacidad=?, medidor_existente=?, tablero_conforme=?,
                  puesta_tierra=?, certificado_sec=?, requiere_proyecto_sec=?, requiere_declaracion_sec=?
              WHERE proyecto_id=?
          """,
              (
                  sum_elec,
                  emp_elec,
                  tipo_emp,
                  req_emp,
                  distrib,
                  pot_disp,
                  pot_req,
                  aum_cap,
                  medidor,
                  tablero,
                  puesta_t,
                  cert_sec,
                  req_proj,
                  req_te1,
                  proy_id,
              ),
          )
          conn.commit()
          conn.close()
          st.success("✅ Factibilidad Eléctrica actualizada correctamente.")

    # TAB 3: FACTIBILIDAD GENERAL
    with tab_fact_gen:
      st.markdown("### 🏗️ Factibilidad Urbana y Topográfica")
      with st.form("form_fact_gen"):
        cg1, cg2 = st.columns(2)
        with cg1:
          p_dom = st.checkbox(
              " Permiso de Edificación DOM",
              value=bool(row_f["permiso_dom"]) if row_f else False,
          )
          r_fin = st.checkbox(
              " Recepción Final DOM",
              value=bool(row_f["recepcion_final"]) if row_f else False,
          )
          f_agu = st.checkbox(
              " Factibilidad Agua Potable",
              value=bool(row_f["fact_agua"]) if row_f else True,
          )
          f_alc = st.checkbox(
              " Factibilidad Alcantarillado",
              value=bool(row_f["alcantarillado"]) if row_f else True,
          )
        with cg2:
          r_arq = st.checkbox(
              " Requiere Proyecto Arquitectura",
              value=bool(row_f["requiere_arqui"]) if row_f else False,
          )
          r_cal = st.checkbox(
              " Requiere Cálculo Estructural",
              value=bool(row_f["requiere_calculo"]) if row_f else False,
          )
          r_top = st.checkbox(
              " Requiere Levantamiento Topográfico",
              value=bool(row_f["requiere_topografia"]) if row_f else False,
          )
          r_sue = st.checkbox(
              " Requiere Estudio de Suelos",
              value=bool(row_f["requiere_suelos"]) if row_f else False,
          )

        if st.form_submit_button("💾 Guardar Factibilidad General"):
          conn = get_connection()
          conn.execute(
              """
              UPDATE factibilidad SET
                  permiso_dom=?, recepcion_final=?, fact_agua=?, alcantarillado=?,
                  requiere_arqui=?, requiere_calculo=?, requiere_topografia=?, requiere_suelos=?
              WHERE proyecto_id=?
          """,
              (
                  p_dom,
                  r_fin,
                  f_agu,
                  f_alc,
                  r_arq,
                  r_cal,
                  r_top,
                  r_sue,
                  proy_id,
              ),
          )
          conn.commit()
          conn.close()
          st.success("✅ Factibilidad General guardada.")

# ==========================================
# MÓDULO 2: LEVANTAMIENTO POR RECINTOS (ITO)
# ==========================================
elif "📊 2. Levantamiento por Recintos" in menu_opcion:
  st.title("📊 Levantamiento Técnico e Inspección por Recintos (ITO)")

  if not proy_id:
    st.warning(
        "⚠️ Debes seleccionar o crear un proyecto activo antes de ingresar"
        " recintos."
    )
  else:
    tab_ingreso_rec, tab_resumen_cub = st.tabs([
        "📝 Inspección en Terreno por Recinto",
        "📋 Cubicación y Resumen Consolidado",
    ])

    conn = get_connection()

    # TAB 1: INGRESO DE RECINTOS
    with tab_ingreso_rec:
      st.subheader("📍 Levantamiento de Puntos Eléctricos por Espacio")

      with st.form("form_recinto"):
        cr1, cr2 = st.columns(2)
        with cr1:
          nombre_rec = st.selectbox(
              "Seleccionar / Tipo de Recinto:",
              [
                  "Cocina",
                  "Estar / Comedor",
                  "Dormitorio Principal",
                  "Dormitorio 2",
                  "Dormitorio 3",
                  "Baño Principal",
                  "Baño Visitas",
                  "Pasillo / Acceso",
                  "Exterior / Fachada",
                  "Zona de Servicio / Logia",
                  "Oficina / Taller",
                  "Otro Recinto",
              ],
          )
          num_enchufes = st.number_input(
              "Puntos de Enchufes (Simples/Dobles):",
              min_value=0,
              value=2,
              step=1,
          )
          num_centros = st.number_input(
              "Centros de Alumbrado / Luminarias:",
              min_value=0,
              value=1,
              step=1,
          )

        with cr2:
          num_interruptores = st.number_input(
              "Interruptores (Simple/Doble/9/24):",
              min_value=0,
              value=1,
              step=1,
          )
          num_fuerza = st.number_input(
              "Puntos Especiales / Fuerza (Clima, Horno, Bomba):",
              min_value=0,
              value=0,
              step=1,
          )
          est_canal = st.selectbox(
              "Estado de Canalizaciones y Cajas Existentes:",
              [
                  "Conforme / Normalizado",
                  "Requiere Cambio de Conductores",
                  "Canalización Incompleta",
                  "Sin Canalización (Obra Gruesa)",
              ],
          )

        obs_ito = st.text_area(
            "Observaciones del Inspector ITO en Terreno:",
            placeholder=(
                "Ejemplo: Canalización en tubo PVC de 20mm. Falta conductor de"
                " tierra de protección en enchufes de mesón."
            ),
        )

        if st.form_submit_button("➕ Agregar Recinto al Proyecto"):
          c = conn.cursor()
          c.execute(
              """
                        INSERT INTO recintos_levantamiento 
                        (proyecto_id, nombre_recinto, puntos_enchufes, centros_iluminacion, interruptores, puntos_fuerza_clima, estado_canalizacion, observaciones_ito)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  proy_id,
                  nombre_rec,
                  num_enchufes,
                  num_centros,
                  num_interruptores,
                  num_fuerza,
                  est_canal,
                  obs_ito,
              ),
          )
          conn.commit()
          st.success(f"✅ Recinto **{nombre_rec}** guardado correctamente.")
          st.rerun()

    # TAB 2: RESUMEN Y CUBICACIÓN
    with tab_resumen_cub:
      st.subheader("📋 Consolidado de Cubicaciones para Presupuesto")

      df_recintos = pd.read_sql_query(
          """
                SELECT id, nombre_recinto AS [Recinto], puntos_enchufes AS [Puntos Enchufe], 
                       centros_iluminacion AS [Centros Alumbrado], interruptores AS [Interruptores], 
                       puntos_fuerza_clima AS [Líneas Fuerza], estado_canalizacion AS [Estado Canalización], 
                       observaciones_ito AS [Observaciones ITO]
                FROM recintos_levantamiento 
                WHERE proyecto_id = ?
            """,
          conn,
          params=(proy_id,),
      )

      if df_recintos.empty:
        st.info(
            "ℹ️ Aún no se han registrado recintos para este proyecto. Utiliza"
            " la pestaña anterior para ingresar los datos de terreno."
        )
      else:
        st.dataframe(
            df_recintos.drop(columns=["id"]),
            use_container_width=True,
            hide_index=True,
        )

        # Totales CUBICACIÓN DIRECTA
        tot_enc = df_recintos["Puntos Enchufe"].sum()
        tot_lum = df_recintos["Centros Alumbrado"].sum()
        tot_int = df_recintos["Interruptores"].sum()
        tot_fue = df_recintos["Líneas Fuerza"].sum()

        st.markdown("---")
        st.markdown("### 🧮 Total Cubicado (Consolidado de Obra)")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Puntos Enchufes", f"{tot_enc} pts")
        k2.metric("Total Centros Alumbrado", f"{tot_lum} pts")
        k3.metric("Total Interruptores", f"{tot_int} pts")
        k4.metric("Total Líneas Fuerza / Clima", f"{tot_fue} pts")

        # Opción para eliminar recinto seleccionado
        st.markdown("---")
        with st.expander("🗑️ Eliminar un Recinto Registrado"):
          rec_del = st.selectbox(
              "Selecciona recinto a eliminar:",
              options=df_recintos["id"].tolist(),
              format_func=lambda x: (
                  f"ID {x} - "
                  f"{df_recintos[df_recintos['id']==x]['Recinto'].values[0]}"
              ),
          )
          if st.button("Eliminar Recinto"):
            conn.execute(
                "DELETE FROM recintos_levantamiento WHERE id = ?", (rec_del,)
            )
            conn.commit()
            st.warning("Recinto eliminado.")
            st.rerun()

    conn.close()

# ==========================================
# MÓDULO 5: ANÁLISIS DE PRECIOS UNITARIOS (OPCIÓN A)
# ==========================================
elif "💰 5. Análisis de Precios Unitarios" in menu_opcion:
  st.title("💰 Módulo APU y Administración de Precios")

  tab_mat, tab_apu_read, tab_resumen = st.tabs([
      "🛠️ 1. Base de Datos de Materiales (Editable)",
      "🔍 2. Análisis APU por Partida (Solo Lectura)",
      "📊 3. Resumen y Cotización Automática",
  ])

  conn = get_connection()

  # TAB 1: BASE DE DATOS MAESTRA (EDITABLE)
  with tab_mat:
    st.subheader("📦 Base de Datos Centralizada de Insumos y Precios Base")
    st.info(
        "💡 **Regla de Negocio:** Modifica aquí los precios base de los"
        " materiales. El sistema re-calculará automáticamente todos los APU,"
        " partidas y totales sin alterar fórmulas."
    )

    df_materiales = pd.read_sql_query(
        "SELECT id, codigo, nombre, categoria, unidad, precio_unitario,"
        " porcentaje_perdida FROM materiales_master",
        conn,
    )

    edited_df = st.data_editor(
        df_materiales,
        column_config={
            "id": None,
            "codigo": st.column_config.TextColumn(
                "Código Insumo", disabled=True
            ),
            "nombre": st.column_config.TextColumn(
                "Descripción Insumo", disabled=True
            ),
            "categoria": st.column_config.TextColumn(
                "Categoría", disabled=True
            ),
            "unidad": st.column_config.TextColumn("Unidad", disabled=True),
            "precio_unitario": st.column_config.NumberColumn(
                "Precio Base ($)", min_value=0, step=100, format="$%d"
            ),
            "porcentaje_perdida": st.column_config.NumberColumn(
                "% Pérdida / Merma",
                min_value=0.0,
                max_value=25.0,
                step=0.5,
                format="%.1f %%",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    if st.button("💾 Actualizar Precios Base de la Obra"):
      cursor = conn.cursor()
      for _, row in edited_df.iterrows():
        cursor.execute(
            """
                UPDATE materiales_master 
                SET precio_unitario = ?, porcentaje_perdida = ?
                WHERE id = ?
            """,
            (row["precio_unitario"], row["porcentaje_perdida"], row["id"]),
        )
      conn.commit()
      st.success("✅ Precios maestros actualizados. Recalculando APUs...")
      st.rerun()

  # TAB 2: DETALLE APU (SOLO LECTURA)
  with tab_apu_read:
    st.subheader("🔍 Desglose de Costo Directo por Partida")
    st.warning(
        "🔒 **Valores Protegidos:** Esta tabla es de solo lectura. Los"
        " subtotales se obtienen multiplicando el Rendimiento × (1 + %Pérdida) ×"
        " Precio Base."
    )

    query_apu_detalle = """
        SELECT 
            p.codigo_partida AS [Cód Partida],
            p.nombre_partida AS [Partida],
            m.nombre AS [Material / Insumo],
            m.unidad AS [Unidad Insumo],
            r.rendimiento AS [Rendimiento],
            m.porcentaje_perdida AS [% Pérdida],
            m.precio_unitario AS [Precio Base $],
            ROUND(r.rendimiento * (1 + (m.porcentaje_perdida / 100.0)) * m.precio_unitario, 0) AS [Subtotal Insumo $]
        FROM apu_receta r
        JOIN partidas_apu p ON r.partida_id = p.id
        JOIN materiales_master m ON r.material_id = m.id
        ORDER BY p.id ASC
    """
    df_apu = pd.read_sql_query(query_apu_detalle, conn)
    st.dataframe(df_apu, use_container_width=True, hide_index=True)

  # TAB 3: RESUMEN Y COTIZACIÓN INVIOLABLE
  with tab_resumen:
    st.subheader("📊 Totales Inviolables del Presupuesto")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
      pct_gg = st.number_input("% Gastos Generales (GG)", value=15.0, step=1.0)
    with col_g2:
      pct_util = st.number_input("% Utilidad", value=10.0, step=1.0)

    # Cálculo dinámico
    query_costo_partidas = """
        SELECT 
            p.id AS partida_id,
            p.codigo_partida AS [Código],
            p.nombre_partida AS [Partida],
            p.unidad_medida AS [Unidad],
            SUM(r.rendimiento * (1 + (m.porcentaje_perdida / 100.0)) * m.precio_unitario) AS [Costo Unitario Directo]
        FROM apu_receta r
        JOIN partidas_apu p ON r.partida_id = p.id
        JOIN materiales_master m ON r.material_id = m.id
        GROUP BY p.id
    """
    df_partidas = pd.read_sql_query(query_costo_partidas, conn)

    # Cargar cubicación real desde recintos si existen datos
    if proy_id:
      rec_df = pd.read_sql_query(
          "SELECT SUM(puntos_enchufes) as tot_enc, SUM(centros_iluminacion)"
          " as tot_lum FROM recintos_levantamiento WHERE proyecto_id = ?",
          conn,
          params=(proy_id,),
      )
      c_enc = rec_df["tot_enc"].iloc[0] or 1.0
      c_lum = rec_df["tot_lum"].iloc[0] or 1.0
    else:
      c_enc, c_lum = 1.0, 1.0

    cantidades_dict = {1: float(c_enc), 2: float(c_lum), 3: 1.0}
    df_partidas["Cantidad Obra"] = df_partidas["partida_id"].map(
        lambda x: cantidades_dict.get(x, 1.0)
    )
    df_partidas["Total Directo $"] = (
        df_partidas["Costo Unitario Directo"] * df_partidas["Cantidad Obra"]
    )

    st.markdown("##### 📋 Resumen de Costo Directo por Partida")
    st.dataframe(
        df_partidas[[
            "Código",
            "Partida",
            "Unidad",
            "Cantidad Obra",
            "Costo Unitario Directo",
            "Total Directo $",
        ]],
        use_container_width=True,
        hide_index=True,
    )

    # Totales Calculados
    costo_directo_total = df_partidas["Total Directo $"].sum()
    monto_gg = costo_directo_total * (pct_gg / 100.0)
    monto_utilidad = costo_directo_total * (pct_util / 100.0)
    monto_neto = costo_directo_total + monto_gg + monto_utilidad
    monto_iva = monto_neto * 0.19
    monto_bruto = monto_neto + monto_iva

    st.markdown("---")
    st.markdown("##### 💰 Resumen Financiero Consolidado")

    m1, m2, m3 = st.columns(3)
    m1.metric("Costo Directo Total", f"${costo_directo_total:,.0f}")
    m2.metric(f"Gastos Generales ({pct_gg}%)", f"${monto_gg:,.0f}")
    m3.metric(f"Utilidad ({pct_util}%)", f"${monto_utilidad:,.0f}")

    m4, m5, m6 = st.columns(3)
    m4.metric("Subtotal Neto", f"${monto_neto:,.0f}")
    m5.metric("IVA (19%)", f"${monto_iva:,.0f}")
    m6.metric(
        "TOTAL PRESUPUESTO BRUTO",
        f"${monto_bruto:,.0f}",
        delta="Calculado Automáticamente",
    )

  conn.close()

# ==========================================
# OTROS MÓDULOS (ESTRUCTURA DE SOPORTE)
# ==========================================
else:
  st.title(menu_opcion)
  st.info(
      f"Módulo **{menu_opcion}** listo para vinculación con el proyecto activo"
      f" N° {st.session_state.get('proyecto_id', 'Sin Seleccionar')}."
  )
