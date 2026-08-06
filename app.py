import io
import json
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="ECOLUZ - Inspector Técnico Inteligente",
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
# 1. BASE DE DATOS Y MIGRACIONES AUTOMÁTICAS
# ==========================================
def init_db():
  conn = get_connection()
  cursor = conn.cursor()

  # 1.1 Proyectos
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

  # 1.2 Factibilidad y Sistemas Transversales (SSOT)
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
            resistencia_malla REAL DEFAULT 0.0,
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

  # Migraciones dinámicas para Factibilidad
  cursor.execute("PRAGMA table_info(factibilidad)")
  col_fact = [c[1] for c in cursor.fetchall()]
  nuevos_campos_fact = [
      ("suministro_elec", "BOOLEAN DEFAULT 1"),
      ("potencia_requerida", "TEXT DEFAULT '40A'"),
      ("empresa_distribuidora", "TEXT DEFAULT 'CGE'"),
      ("medidor_existente", "BOOLEAN DEFAULT 1"),
      ("requiere_nuevo_empalme", "BOOLEAN DEFAULT 0"),
      ("requiere_proyecto_sec", "BOOLEAN DEFAULT 0"),
      ("requiere_declaracion_sec", "BOOLEAN DEFAULT 1"),
      ("resistencia_malla", "REAL DEFAULT 0.0"),
  ]
  for campo, tipo in nuevos_campos_fact:
    if campo not in col_fact:
      try:
        cursor.execute(f"ALTER TABLE factibilidad ADD COLUMN {campo} {tipo}")
      except Exception:
        pass

  # 1.3 Levantamiento Espacial y Diagnosticador de Patologías por Recintos
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS recintos_levantamiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            nombre_recinto TEXT NOT NULL,
            elemento_constructivo TEXT DEFAULT 'Instalación Eléctrica General',
            estado_diagnostico TEXT DEFAULT 'Conforme / Normalizado',
            patologia_observada TEXT,
            puntos_enchufes INTEGER DEFAULT 0,
            centros_iluminacion INTEGER DEFAULT 0,
            interruptores INTEGER DEFAULT 0,
            puntos_fuerza_clima INTEGER DEFAULT 0,
            estado_canalizacion TEXT DEFAULT 'Conforme',
            observaciones_ito TEXT,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos (id) ON DELETE CASCADE
        )
    """)

  # Migraciones para Recintos (Diagnóstico e Inspección ITO)
  cursor.execute("PRAGMA table_info(recintos_levantamiento)")
  col_rec = [c[1] for c in cursor.fetchall()]
  nuevos_campos_rec = [
      (
          "elemento_constructivo",
          "TEXT DEFAULT 'Instalación Eléctrica General'",
      ),
      ("estado_diagnostico", "TEXT DEFAULT 'Conforme / Normalizado'"),
      ("patologia_observada", "TEXT"),
  ]
  for campo, tipo in nuevos_campos_rec:
    if campo not in col_rec:
      try:
        cursor.execute(
            f"ALTER TABLE recintos_levantamiento ADD COLUMN {campo} {tipo}"
        )
      except Exception:
        pass

  # 1.4 Tabla Maestra de Materiales e Insumos con Clasificación de Rol
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            rol_material TEXT DEFAULT 'Principal',
            unidad TEXT NOT NULL,
            precio_unitario REAL NOT NULL DEFAULT 0,
            porcentaje_perdida REAL NOT NULL DEFAULT 5.0
        )
    """)

  # Migraciones para Materiales
  cursor.execute("PRAGMA table_info(materiales_master)")
  col_mat = [c[1] for c in cursor.fetchall()]
  if "rol_material" not in col_mat:
    try:
      cursor.execute(
          "ALTER TABLE materiales_master ADD COLUMN rol_material TEXT DEFAULT"
          " 'Principal'"
      )
    except Exception:
      pass

  cursor.execute("SELECT COUNT(*) FROM materiales_master")
  if cursor.fetchone()[0] == 0:
    materiales_semilla = [
        (
            "MAT-ELE-001",
            "Cable EVA 2.5mm² Rojo",
            "Conductores",
            "Principal",
            "m",
            650,
            5.0,
        ),
        (
            "MAT-ELE-002",
            "Cable EVA 2.5mm² Blanco",
            "Conductores",
            "Principal",
            "m",
            650,
            5.0,
        ),
        (
            "MAT-ELE-003",
            "Cable EVA 2.5mm² Verde",
            "Conductores",
            "Principal",
            "m",
            650,
            5.0,
        ),
        (
            "MAT-ELE-004",
            "Módulo Enchufe Doble 10A/16A + Placa",
            "Aparatos",
            "Principal",
            "un",
            3800,
            2.0,
        ),
        (
            "MAT-ELE-005",
            "Downlight LED 18W Embutido Borde Blanco",
            "Luminarias",
            "Principal",
            "un",
            6900,
            2.0,
        ),
        (
            "MAT-ELE-006",
            "Tubo PVC Conduit 20mm x 3m",
            "Canalizaciones",
            "Secundario",
            "un",
            1850,
            5.0,
        ),
        (
            "MAT-ELE-007",
            "Caja Chuqui Plástica Embutir",
            "Cajas y Accesorios",
            "Accesorio",
            "un",
            450,
            3.0,
        ),
        (
            "MAT-ELE-008",
            "Interruptor Termomagnético 1x16A 6kA Legrand",
            "Tableros",
            "Principal",
            "un",
            5200,
            0.0,
        ),
        (
            "MAT-ELE-009",
            "Interruptor Diferencial 2x25A 30mA Legrand",
            "Tableros",
            "Principal",
            "un",
            14900,
            0.0,
        ),
        (
            "MAT-ELE-010",
            "Cinta Aislante Vinílica 3M Super 33+",
            "Consumibles",
            "Consumible",
            "un",
            2400,
            0.0,
        ),
        (
            "MAT-ELE-011",
            "Set Tarugos y Tornillos Volcanita/Concreto 6mm",
            "Fijaciones",
            "Fijación",
            "gl",
            1200,
            10.0,
        ),
        (
            "MO-ELE-001",
            "H.H. Maestro Eléctrico SEC Clase F/G",
            "Mano de Obra",
            "Mano de Obra",
            "HH",
            8500,
            0.0,
        ),
    ]
    cursor.executemany(
        """
            INSERT INTO materiales_master (codigo, nombre, categoria, rol_material, unidad, precio_unitario, porcentaje_perdida)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        materiales_semilla,
    )

  # 1.5 Partidas APU y Plantillas EETT
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas_apu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_partida TEXT NOT NULL,
            nombre_partida TEXT NOT NULL,
            unidad_medida TEXT NOT NULL,
            categoria TEXT NOT NULL,
            eett_plantilla TEXT
        )
    """)

  cursor.execute("SELECT COUNT(*) FROM partidas_apu")
  if cursor.fetchone()[0] == 0:
    partidas_semilla = [
        (
            "PAR-ELE-01",
            "Punto de Enchufe Doble 16A Embutido",
            "punto",
            "Electricidad",
            (
                "Instalación de punto de enchufe doble 10/16A embutido en"
                " caja plástica. Incluye canalización conduit PVC 20mm,"
                " conductores de cobre libre de halógenos EVA 2.5mm² (fase,"
                " neutro, tierra), conexiones, pruebas de polaridad y"
                " aislamiento bajo norma RIC N°10."
            ),
        ),
        (
            "PAR-ELE-02",
            "Punto Centro Alumbrado LED Embutido",
            "punto",
            "Electricidad",
            (
                "Suministro e instalación de centro de iluminación embutido con"
                " panel LED 18W. Incluye tubería conduit PVC, cableado EVA 1.5"
                " / 2.5 mm², caja de derivación, interruptor de comando y"
                " verificación de niveles de iluminancia bajo norma RIC N°10."
            ),
        ),
        (
            "PAR-ELE-03",
            "Provisión y Montaje Tablero TDA 12 Módulos",
            "un",
            "Electricidad",
            (
                "Suministro, armado y montaje de Tablero de Distribución"
                " Alumbrado (TDA) de 12 módulos embutido/sobrepuesto en gabinete"
                " autoextinguible. Incluye disyuntor general, protectores"
                " diferenciales de 30mA, barra a tierra, peineta y rotulación"
                " según pliego RIC N°02."
            ),
        ),
    ]
    cursor.executemany(
        """
            INSERT INTO partidas_apu (codigo_partida, nombre_partida, unidad_medida, categoria, eett_plantilla)
            VALUES (?, ?, ?, ?, ?)
        """,
        partidas_semilla,
    )

  # 1.6 Receta APU
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
        # Punto Enchufe
        (1, 4, 1.0),
        (1, 7, 1.0),
        (1, 6, 1.0),
        (1, 1, 3.5),
        (1, 2, 3.5),
        (1, 3, 3.5),
        (1, 10, 0.1),
        (1, 11, 0.2),
        (1, 12, 0.40),
        # Centro Alumbrado
        (2, 5, 1.0),
        (2, 7, 1.0),
        (2, 6, 1.0),
        (2, 1, 3.0),
        (2, 2, 3.0),
        (2, 3, 3.0),
        (2, 10, 0.1),
        (2, 11, 0.2),
        (2, 12, 0.35),
        # Tablero TDA
        (3, 8, 3.0),
        (3, 9, 1.0),
        (3, 10, 0.5),
        (3, 11, 1.0),
        (3, 12, 2.00),
    ]
    cursor.executemany(
        """
            INSERT INTO apu_receta (partida_id, material_id, rendimiento)
            VALUES (?, ?, ?)
        """,
        recetas_semilla,
    )

  # 1.7 Historial de Cotizaciones
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


# Ejecutar inicialización de BD
init_db()

# ==========================================
# 2. NAVEGACIÓN Y PANEL LATERAL
# ==========================================
st.sidebar.image(
    "https://img.icons8.com/color/96/lightning-bolt.png", width=60
)
st.sidebar.title("ECOLUZ v2.5")
st.sidebar.caption("Inspector Técnico Inteligente & Presupuestos SEC")

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
st.sidebar.subheader("📌 Proyecto en Inspección")

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
menu_opcion = st.sidebar.radio(
    "Flujo del Inspector Técnico",
    [
        "📌 1. Información General y Sistemas Transversales",
        "📊 2. Inspección en Terreno (Recintos y Patologías)",
        "🔍 3. Motor de Auditoría y Alertas RIC/SEC",
        "📄 4. Generador de EETT, Informes y Cotización (PDF / Excel)",
        "💰 5. Módulo APU y Administración de Materiales",
        "🏷️ 6. Historial Comercial y Versionado",
    ],
)

proy_id = st.session_state.get("proyecto_id")

# ==========================================
# MÓDULO 1: INFORMACIÓN GENERAL Y SISTEMAS TRANSVERSALES
# ==========================================
if "📌 1. Información General" in menu_opcion:
  st.title("📌 Información General del Proyecto y Sistemas Transversales")

  tab_nuevo, tab_fact_elec, tab_fact_gen = st.tabs([
      "➕ Registrar Nuevo Proyecto / Obra",
      "⚡ Inspección de Sistemas Transversales (Red/Empalme/TDA/Tierra)",
      "🏗️ Factibilidad Urbana y Permisos DOM",
  ])

  with tab_nuevo:
    st.subheader("Registrar Ficha de Obra e Inspección")
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
                "Inspección Técnica Diagnóstica",
            ],
        )

      if st.form_submit_button("Crear Proyecto"):
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

    with tab_fact_elec:
      st.markdown(
          "### ⚡ Diagnóstico de Infraestructura y Sistemas Transversales"
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
          st.subheader("2. Potencia y Tablero TDA")
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
              "¿Tablero TDA cumple norma vigente (RIC N°02)?",
              value=bool(row_f["tablero_conforme"]) if row_f else True,
          )

        with c_fe3:
          st.subheader("3. Malla Tierra & SEC")
          puesta_t = st.checkbox(
              "¿Existe Malla/Puesta a Tierra probada?",
              value=bool(row_f["puesta_tierra"]) if row_f else False,
          )
          res_malla = st.number_input(
              "Resistencia Medida Malla Tierra (Ohms):",
              value=float(row_f["resistencia_malla"]) if row_f else 0.0,
              step=0.5,
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

        if st.form_submit_button("💾 Guardar Sistemas Transversales"):
          conn = get_connection()
          conn.execute(
              """
              UPDATE factibilidad SET
                  suministro_elec=?, empalme_elec=?, tipo_empalme=?, requiere_nuevo_empalme=?, empresa_distribuidora=?,
                  potencia_disponible=?, potencia_requerida=?, aumento_capacidad=?, medidor_existente=?, tablero_conforme=?,
                  puesta_tierra=?, resistencia_malla=?, certificado_sec=?, requiere_proyecto_sec=?, requiere_declaracion_sec=?
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
                  res_malla,
                  cert_sec,
                  req_proj,
                  req_te1,
                  proy_id,
              ),
          )
          conn.commit()
          conn.close()
          st.success(
              "✅ Inspección de Sistemas Transversales actualizada correctamente."
          )

    with tab_fact_gen:
      st.markdown("### 🏗️ Factibilidad Urbana y Permisos DOM")
      with st.form("form_fact_gen"):
        cg1, cg2 = st.columns(2)
        with cg1:
          p_dom = st.checkbox(
              "Permiso de Edificación DOM",
              value=bool(row_f["permiso_dom"]) if row_f else False,
          )
          r_fin = st.checkbox(
              "Recepción Final DOM",
              value=bool(row_f["recepcion_final"]) if row_f else False,
          )
          f_agu = st.checkbox(
              "Factibilidad Agua Potable",
              value=bool(row_f["fact_agua"]) if row_f else True,
          )
          f_alc = st.checkbox(
              "Factibilidad Alcantarillado",
              value=bool(row_f["alcantarillado"]) if row_f else True,
          )
        with cg2:
          r_arq = st.checkbox(
              "Requiere Proyecto Arquitectura",
              value=bool(row_f["requiere_arqui"]) if row_f else False,
          )
          r_cal = st.checkbox(
              "Requiere Cálculo Estructural",
              value=bool(row_f["requiere_calculo"]) if row_f else False,
          )
          r_top = st.checkbox(
              "Requiere Levantamiento Topográfico",
              value=bool(row_f["requiere_topografia"]) if row_f else False,
          )
          r_sue = st.checkbox(
              "Requiere Estudio de Suelos",
              value=bool(row_f["requiere_suelos"]) if row_f else False,
          )

        if st.form_submit_button("💾 Guardar Factibilidad Urbana"):
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
          st.success("✅ Factibilidad urbana guardada.")

# ==========================================
# MÓDULO 2: INSPECCIÓN EN TERRENO (RECINTOS Y PATOLOGÍAS)
# ==========================================
elif "📊 2. Inspección en Terreno" in menu_opcion:
  st.title("📊 Inspección Espacial: Recintos, Elementos y Patologías")

  if not proy_id:
    st.warning("⚠️ Selecciona un proyecto activo en el panel lateral.")
  else:
    tab_ingreso_rec, tab_resumen_cub = st.tabs([
        "📝 Levantamiento Diagnóstico por Recinto",
        "📋 Resumen Consolidado de Inspección y Cubicación",
    ])

    conn = get_connection()

    with tab_ingreso_rec:
      st.subheader(
          "📍 Diagnóstico de Elementos Constructivos y Prescripción Técnica"
      )
      with st.form("form_recinto"):
        cr1, cr2 = st.columns(2)
        with cr1:
          nombre_rec = st.selectbox(
              "Recinto / Espacio Físico:",
              [
                  "Cocina (Zona Húmeda)",
                  "Estar / Comedor",
                  "Dormitorio Principal",
                  "Dormitorio 2",
                  "Dormitorio 3",
                  "Baño Principal (Zona Húmeda)",
                  "Baño Visitas",
                  "Pasillo / Acceso",
                  "Exterior / Fachada",
                  "Zona de Servicio / Logia",
                  "Oficina / Taller",
                  "Otro Recinto",
              ],
          )
          elem_constructivo = st.selectbox(
              "Elemento Constructivo Evaluado:",
              [
                  "Instalación Eléctrica - Enchufes",
                  "Instalación Eléctrica - Iluminación",
                  "Tablero Eléctrico Secundario",
                  "Tabiquería / Muros",
                  "Cielo Falso / Aislación",
                  "Pisos / Revestimientos",
              ],
          )
          diag_estado = st.selectbox(
              "Diagnóstico ITO / Estado Actual:",
              [
                  "Conforme / Normalizado",
                  "No Conforme (Falta Protección Diferencial)",
                  "No Conforme (Conductores de Tela/Aluminio Fuera de Norma)",
                  "Canalización Incompleta o Expuesta",
                  "Sin Instalación / Obra Gruesa",
                  "Deterioro por Humedad / Filtración",
              ],
          )
          patologia_txt = st.text_input(
              "Descripción de la Patología o Deficiencia Observada:",
              placeholder="Ej: Circuito de cocina sin tierra de protección y"
              " enchufes sobrecargados.",
          )

        with cr2:
          num_enchufes = st.number_input(
              "Puntos de Enchufes Necesarios/Intervenir:",
              min_value=0,
              value=2,
              step=1,
          )
          num_centros = st.number_input(
              "Centros de Alumbrado Necesarios/Intervenir:",
              min_value=0,
              value=1,
              step=1,
          )
          num_interruptores = st.number_input(
              "Interruptores:", min_value=0, value=1, step=1
          )
          num_fuerza = st.number_input(
              "Líneas Dedicadas / Fuerza / Clima:",
              min_value=0,
              value=0,
              step=1,
          )
          est_canal = st.selectbox(
              "Estado de Canalizaciones:",
              [
                  "Conforme / Canalización Rígida Conduits",
                  "Requiere Cambio de Conductores",
                  "Canalización Incompleta",
                  "Sin Canalización (Obra Gruesa)",
              ],
          )

        obs_ito = st.text_area(
            "Observaciones y Prescripción Técnica del ITO:"
        )

        if st.form_submit_button("➕ Registrar Inspección de Recinto"):
          c = conn.cursor()
          c.execute(
              """
                        INSERT INTO recintos_levantamiento 
                        (proyecto_id, nombre_recinto, elemento_constructivo, estado_diagnostico, patologia_observada,
                         puntos_enchufes, centros_iluminacion, interruptores, puntos_fuerza_clima, estado_canalizacion, observaciones_ito)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  proy_id,
                  nombre_rec,
                  elem_constructivo,
                  diag_estado,
                  patologia_txt,
                  num_enchufes,
                  num_centros,
                  num_interruptores,
                  num_fuerza,
                  est_canal,
                  obs_ito,
              ),
          )
          conn.commit()
          st.success(f"✅ Inspección de **{nombre_rec}** registrada.")
          st.rerun()

    with tab_resumen_cub:
      st.subheader("📋 Consolidado de Inspección y Cubicación")
      df_recintos = pd.read_sql_query(
          """
                SELECT id, nombre_recinto AS [Recinto], elemento_constructivo AS [Elemento], 
                       estado_diagnostico AS [Diagnóstico ITO], puntos_enchufes AS [Enchufes], 
                       centros_iluminacion AS [Centros], interruptores AS [Interruptores], 
                       puntos_fuerza_clima AS [Fuerza], observaciones_ito AS [Obs]
                FROM recintos_levantamiento WHERE proyecto_id = ?
            """,
          conn,
          params=(proy_id,),
      )

      if df_recintos.empty:
        st.info("ℹ️ No hay recintos o elementos inspeccionados aún.")
      else:
        st.dataframe(
            df_recintos.drop(columns=["id"]),
            use_container_width=True,
            hide_index=True,
        )
        tot_enc = df_recintos["Enchufes"].sum()
        tot_lum = df_recintos["Centros"].sum()
        tot_int = df_recintos["Interruptores"].sum()
        tot_fue = df_recintos["Fuerza"].sum()

        st.markdown("---")
        st.markdown("### 🧮 Total Cubicado para Presupuesto")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Puntos Enchufes", f"{tot_enc} pts")
        k2.metric("Total Centros Alumbrado", f"{tot_lum} pts")
        k3.metric("Total Interruptores", f"{tot_int} pts")
        k4.metric("Total Líneas Fuerza / Clima", f"{tot_fue} pts")

        with st.expander("🗑️ Eliminar Registro de Recinto"):
          rec_del = st.selectbox(
              "Selecciona registro:",
              options=df_recintos["id"].tolist(),
              format_func=lambda x: (
                  f"ID {x} - "
                  f"{df_recintos[df_recintos['id']==x]['Recinto'].values[0]}"
              ),
          )
          if st.button("Eliminar Registro"):
            conn.execute(
                "DELETE FROM recintos_levantamiento WHERE id = ?", (rec_del,)
            )
            conn.commit()
            st.rerun()

    conn.close()

# ==========================================
# MÓDULO 3: MOTOR DE AUDITORÍA Y ALERTAS RIC/SEC
# ==========================================
elif "🔍 3. Motor de Auditoría" in menu_opcion:
  st.title("🔍 Motor de Auditoría Técnica & Alertas de Cumplimiento RIC/SEC")

  if not proy_id:
    st.warning("⚠️ Selecciona un proyecto activo para auditar.")
  else:
    conn = get_connection()
    row_f = conn.execute(
        "SELECT * FROM factibilidad WHERE proyecto_id = ?", (proy_id,)
    ).fetchone()
    df_rec = pd.read_sql_query(
        "SELECT * FROM recintos_levantamiento WHERE proyecto_id = ?",
        conn,
        params=(proy_id,),
    )
    conn.close()

    st.markdown(
        "### ⚡ Evaluación Automática de Normativa Eléctrica Chilena (Pliego"
        " Técnico RIC)"
    )

    alertas_criticas = []
    advertencias = []
    conformidades = []

    if row_f:
      # Regla 1: Potencia Mayor a 10kW requiere Proyecto Firmado e Inscrito TE1
      pot_str = row_f["potencia_requerida"] or "40A"
      try:
        amperes = int("".join(filter(str.isdigit, pot_str)))
      except ValueError:
        amperes = 40

      es_trifasico = row_f["tipo_empalme"] == "Trifásico (3Ф)"
      potencia_kw = (
          (amperes * 220 * 1.732 / 1000)
          if es_trifasico
          else (amperes * 220 / 1000)
      )

      if potencia_kw > 10.0:
        if not row_f["requiere_proyecto_sec"]:
          alertas_criticas.append(
              f"**RIC N°01 / Potencia {potencia_kw:.1f} kW > 10 kW:**"
              " La instalación supera los 10 kW. Es **obligatorio** contar con"
              " Proyecto Eléctrico firmado por Instalador SEC Clase A o B."
          )
        else:
          conformidades.append(
              f"Potencia proyectada ({potencia_kw:.1f} kW) exige Proyecto"
              " Eléctrico Firmado (Configurado correctamente)."
          )

      # Regla 2: Puesta a Tierra y Malla de Protección (RIC N°06)
      if not row_f["puesta_tierra"]:
        alertas_criticas.append(
            "**RIC N°06 / Puesta a Tierra Inexistente:** No se registra puesta"
            " a tierra probada. Toda instalación en Chile debe contar con"
            " electrodo o malla de tierra conforme."
        )
      else:
        res_m = float(row_f["resistencia_malla"] or 0.0)
        if res_m > 20.0 or res_m == 0.0:
          advertencias.append(
              f"**RIC N°06 / Valor de Malla a Tierra ({res_m} Ω):** La"
              " resistencia debe ser medida con telurómetro y garantizar un"
              " valor inferior a 20 Ohms."
          )
        else:
          conformidades.append(
              f"Malla a Tierra con resistencia conforme ({res_m} Ω < 20 Ω)."
          )

      # Regla 3: Cumplimiento de Tableros (RIC N°02)
      if not row_f["tablero_conforme"]:
        alertas_criticas.append(
            "**RIC N°02 / Tablero TDA Fuera de Norma:** El tablero actual no"
            " cumple requisitos normativos (falta protector diferencial,"
            " rotulación o peineta de distribución)."
        )
      else:
        conformidades.append(
            "Tablero Eléctrico TDA reportado en conformidad."
        )

    # Regla 4: Auditoría de Recintos Húmedos (RIC N°10 / RIC N°11)
    if not df_rec.empty:
      recintos_humedos = df_rec[
          df_rec["nombre_recinto"].str.contains(
              "Cocina|Baño|Logia", case=False, regex=True
          )
      ]
      if not recintos_humedos.empty:
        advertencias.append(
            f"**RIC N°11 / Zonas Húmedas Detectadas:** Se identificaron"
            f" {len(recintos_humedos)} recintos húmedos con exigencia de"
            " protección diferencial dedicada (30mA) y grado IP adecuado."
        )

      # Regla 5: Patologías Detectadas
      con_patologia = df_rec[
          df_rec["estado_diagnostico"].str.contains("No Conforme", case=False)
      ]
      if not con_patologia.empty:
        alertas_criticas.append(
            f"**Diagnóstico ITO / Patologías Críticas:** Se registraron"
            f" {len(con_patologia)} elementos con no conformidades graves"
            " que exigen intervención inmediata."
        )

    # Despliegue de Indicadores y Alertas
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Alertas Críticas (Norma SEC)",
        f"{len(alertas_criticas)}",
        delta_color="inverse",
    )
    c2.metric("Advertencias Técnicas", f"{len(advertencias)}")
    c3.metric("Conformidades", f"{len(conformidades)}")

    st.markdown("---")

    if alertas_criticas:
      st.error("🚨 **ALERTAS CRÍTICAS DE INCUMPLIMIENTO NORMATIVO**")
      for ac in alertas_criticas:
        st.markdown(f"- {ac}")

    if advertencias:
      st.warning("⚠️ **OBSERVACIONES Y RECOMENDACIONES TÉCNICAS**")
      for adv in advertencias:
        st.markdown(f"- {adv}")

    if conformidades:
      st.success("✅ **REQUISITOS CUMPLIDOS CON ÉXITO**")
      for conf in conformidades:
        st.markdown(f"- {conf}")

# ==========================================
# MÓDULO 4: GENERACIÓN DE EETT, INFORMES Y COTIZACIONES (PDF / EXCEL)
# ==========================================
elif "📄 4. Generador de EETT" in menu_opcion:
  st.title("📄 Generador de Especificaciones Técnicas (EETT) & Presupuesto")

  if not proy_id:
    st.warning("⚠️ Selecciona un proyecto activo.")
  else:
    conn = get_connection()
    row_p = conn.execute(
        "SELECT * FROM proyectos WHERE id = ?", (proy_id,)
    ).fetchone()
    row_f = conn.execute(
        "SELECT * FROM factibilidad WHERE proyecto_id = ?", (proy_id,)
    ).fetchone()
    df_rec = pd.read_sql_query(
        "SELECT nombre_recinto AS [Recinto], elemento_constructivo AS"
        " [Elemento], estado_diagnostico AS [Diagnóstico], puntos_enchufes AS"
        " [Enchufes], centros_iluminacion AS [Centros], interruptores AS"
        " [Interruptores], observaciones_ito AS [Obs] FROM"
        " recintos_levantamiento WHERE proyecto_id = ?",
        conn,
        params=(proy_id,),
    )

    query_costo = """
            SELECT p.codigo_partida AS [Código], p.nombre_partida AS [Partida], p.unidad_medida AS [Unidad], p.eett_plantilla, p.id AS partida_id,
                   SUM(r.rendimiento * (1 + (m.porcentaje_perdida / 100.0)) * m.precio_unitario) AS [CostoUnitarioDirecto]
            FROM apu_receta r JOIN partidas_apu p ON r.partida_id = p.id JOIN materiales_master m ON r.material_id = m.id GROUP BY p.id
        """
    df_partidas = pd.read_sql_query(query_costo, conn)
    conn.close()

    c_enc = df_rec["Enchufes"].sum() if not df_rec.empty else 1
    c_lum = df_rec["Centros"].sum() if not df_rec.empty else 1
    cant_map = {1: float(c_enc), 2: float(c_lum), 3: 1.0}

    df_partidas["Cantidad"] = df_partidas["partida_id"].map(
        lambda x: cant_map.get(x, 1.0)
    )
    df_partidas["Precio Unitario Venta ($)"] = (
        df_partidas["CostoUnitarioDirecto"] * 1.25
    ).round(0)
    df_partidas["Total Venta ($)"] = (
        df_partidas["Precio Unitario Venta ($)"] * df_partidas["Cantidad"]
    ).round(0)

    tab_eett, tab_pdf_sec, tab_cotiz_cli, tab_export_excel = st.tabs([
        "📋 Especificación Técnica (EETT) Automática",
        "⚡ Ficha de Factibilidad SEC (Imprimible)",
        "💼 Presupuesto Comercial Cliente",
        "📊 Exportación Excel / Datos",
    ])

    # 1. ESPECIFICACIÓN TÉCNICA AUTOMÁTICA
    with tab_eett:
      st.subheader("📋 Especificaciones Técnicas del Proyecto (EETT)")
      st.caption(
          "Construidas dinámicamente a partir del diagnóstico y levantamiento de"
          " terreno."
      )

      st.markdown(
          f"### ESPECIFICACIÓN TÉCNICA - PROYECTO N° {row_p['id']}:"
          f" {row_p['nombre_cliente']}"
      )
      st.markdown(
          f"**Ubicación:** {row_p['direccion']} | **ITO Inspector:**"
          f" {row_p['inspector']}"
      )
      st.markdown("---")

      for idx, p_row in df_partidas.iterrows():
        st.markdown(
            f"#### {idx+1}.0 PARTIDA: {p_row['Partida']} ({p_row['Código']})"
        )
        st.markdown(f"**Unidad de Medida:** {p_row['Unidad']}")
        st.markdown(
            f"**Descripción y Normativa:** {p_row['eett_plantilla'] or 'Sin especificación precargada.'}"
        )
        st.markdown("---")

    # 2. FICHA SEC
    with tab_pdf_sec:
      st.subheader("📄 Ficha de Factibilidad Eléctrica SEC (Vista de Impresión)")
      html_ficha = f"""
            <div style="border: 2px solid #1E3A8A; padding: 25px; border-radius: 8px; font-family: Arial, sans-serif;">
                <h2 style="color: #1E3A8A; text-align: center; margin-bottom: 5px;">ECOLUZ - FICHA TÉCNICA DE FACTIBILIDAD ELÉCTRICA</h2>
                <p style="text-align: center; font-size: 12px; color: #555;">Normativa RIC / SEC - Superintendencia de Electricidad y Combustibles</p>
                <hr>
                <table style="width: 100%; font-size: 14px; margin-bottom: 15px;">
                    <tr><td><b>Cliente:</b> {row_p['nombre_cliente']}</td><td><b>RUT:</b> {row_p['rut']}</td></tr>
                    <tr><td><b>Dirección Obra:</b> {row_p['direccion']}</td><td><b>Fecha:</b> {row_p['fecha_creacion']}</td></tr>
                    <tr><td><b>Inspector ITO:</b> {row_p['inspector']}</td><td><b>Tipo Obra:</b> {row_p['tipo_obra']}</td></tr>
                </table>
                
                <h4 style="background-color: #F3F4F6; padding: 6px; color: #1E3A8A;">1. DIAGNÓSTICO DE INFRAESTRUCTURA TRANSVERSAL</h4>
                <ul style="font-size: 13px; line-height: 1.6;">
                    <li><b>Suministro Activo:</b> {'SÍ' if row_f['suministro_elec'] else 'NO'} | <b>Empalme:</b> {row_f['tipo_empalme']} ({row_f['empresa_distribuidora']})</li>
                    <li><b>Potencia Instalada / Requerida:</b> {row_f['potencia_disponible']} / {row_f['potencia_requerida']}</li>
                    <li><b>Aumento Capacidad Requerido:</b> {'SÍ' if row_f['aumento_capacidad'] else 'NO'}</li>
                    <li><b>Malla Puesta a Tierra:</b> {'SÍ' if row_f['puesta_tierra'] else 'NO'} (Resistencia: {row_f['resistencia_malla']} Ω)</li>
                    <li><b>Proyecto Eléctrico Requerido:</b> {'SÍ' if row_f['requiere_proyecto_sec'] else 'NO'}</li>
                    <li><b>Declaración TE1 SEC:</b> {'SÍ' if row_f['requiere_declaracion_sec'] else 'NO'}</li>
                </ul>

                <br><br>
                <table style="width: 100%; text-align: center; margin-top: 30px; font-size: 13px;">
                    <tr>
                        <td style="width: 50%;">___________________________________<br><b>Firma Inspector Técnico (ITO)</b><br>SEC Reg: ______________</td>
                        <td style="width: 50%;">___________________________________<br><b>Firma / Conformidad Cliente</b><br>RUT: {row_p['rut']}</td>
                    </tr>
                </table>
            </div>
            """
      st.components.v1.html(html_ficha, height=450, scrolling=True)

    # 3. PRESUPUESTO CLIENTE
    with tab_cotiz_cli:
      st.subheader("💼 Presupuesto Comercial (Cliente)")
      df_cliente_view = df_partidas[[
          "Código",
          "Partida",
          "Unidad",
          "Cantidad",
          "Precio Unitario Venta ($)",
          "Total Venta ($)",
      ]]
      st.dataframe(df_cliente_view, use_container_width=True, hide_index=True)

      neto_v = df_cliente_view["Total Venta ($)"].sum()
      iva_v = neto_v * 0.19
      total_v = neto_v + iva_v

      v1, v2, v3 = st.columns(3)
      v1.metric("Monto Neto Venta", f"${neto_v:,.0f}")
      v2.metric("IVA (19%)", f"${iva_v:,.0f}")
      v3.metric("TOTAL PRESUPUESTO BRUTO", f"${total_v:,.0f}")

    # 4. EXPORTAR EXCEL
    with tab_export_excel:
      st.subheader("📊 Exportar Proyecto Completo a Excel")
      output = io.BytesIO()
      with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_cliente_view.to_excel(
            writer, sheet_name="Presupuesto_Comercial", index=False
        )
        if not df_rec.empty:
          df_rec.to_excel(
              writer, sheet_name="Levantamiento_Recintos", index=False
          )

      excel_data = output.getvalue()
      st.download_button(
          label="📥 Descargar Presupuesto y Cubicación en Excel (.xlsx)",
          data=excel_data,
          file_name=f"Presupuesto_ECOLUZ_Proyecto_{proy_id}.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
      )

# ==========================================
# MÓDULO 5: ANÁLISIS DE PRECIOS UNITARIOS (APU) Y MATERIALES
# ==========================================
elif "💰 5. Módulo APU" in menu_opcion:
  st.title("💰 Módulo APU y Catálogo de Materiales con Clasificación de Roles")

  tab_mat, tab_apu_read, tab_resumen = st.tabs([
      "🛠️ Base de Datos Insumos (Roles y Pérdidas)",
      "🔍 Análisis APU por Partida",
      "📊 Resumen de Costos Directos y Márgenes",
  ])

  conn = get_connection()

  with tab_mat:
    st.subheader("📦 Base de Datos Centralizada de Insumos")
    df_materiales = pd.read_sql_query(
        "SELECT id, codigo, nombre, categoria, rol_material, unidad,"
        " precio_unitario, porcentaje_perdida FROM materiales_master",
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
            "rol_material": st.column_config.SelectboxColumn(
                "Rol en Obra",
                options=[
                    "Principal",
                    "Secundario",
                    "Accesorio",
                    "Consumible",
                    "Fijación",
                    "Mano de Obra",
                ],
                required=True,
            ),
            "precio_unitario": st.column_config.NumberColumn(
                "Precio Base ($)", min_value=0, step=100, format="$%d"
            ),
            "porcentaje_perdida": st.column_config.NumberColumn(
                "% Pérdida / Mermas",
                min_value=0.0,
                max_value=25.0,
                format="%.1f %%",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    if st.button("💾 Actualizar Catálogo de Insumos"):
      cursor = conn.cursor()
      for _, row in edited_df.iterrows():
        cursor.execute(
            """
                UPDATE materiales_master SET rol_material = ?, precio_unitario = ?, porcentaje_perdida = ? WHERE id = ?
            """,
            (
                row["rol_material"],
                row["precio_unitario"],
                row["porcentaje_perdida"],
                row["id"],
            ),
        )
      conn.commit()
      st.success("✅ Precios y roles de insumos actualizados.")
      st.rerun()

  with tab_apu_read:
    query_apu_detalle = """
        SELECT p.codigo_partida AS [Cód Partida], p.nombre_partida AS [Partida], m.nombre AS [Material / Insumo],
               m.rol_material AS [Rol Insumo], m.unidad AS [Unidad], r.rendimiento AS [Rendimiento], m.porcentaje_perdida AS [% Mermas],
               m.precio_unitario AS [Precio Base $],
               ROUND(r.rendimiento * (1 + (m.porcentaje_perdida / 100.0)) * m.precio_unitario, 0) AS [Subtotal $]
        FROM apu_receta r JOIN partidas_apu p ON r.partida_id = p.id JOIN materiales_master m ON r.material_id = m.id
        ORDER BY p.id ASC
    """
    st.dataframe(
        pd.read_sql_query(query_apu_detalle, conn),
        use_container_width=True,
        hide_index=True,
    )

  with tab_resumen:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
      pct_gg = st.number_input("% Gastos Generales", value=15.0, step=1.0)
    with col_g2:
      pct_util = st.number_input("% Utilidad", value=10.0, step=1.0)

    query_costo_partidas = """
        SELECT p.id AS partida_id, p.codigo_partida AS [Código], p.nombre_partida AS [Partida], p.unidad_medida AS [Unidad],
               SUM(r.rendimiento * (1 + (m.porcentaje_perdida / 100.0)) * m.precio_unitario) AS [Costo Unitario Directo]
        FROM apu_receta r JOIN partidas_apu p ON r.partida_id = p.id JOIN materiales_master m ON r.material_id = m.id GROUP BY p.id
    """
    df_partidas = pd.read_sql_query(query_costo_partidas, conn)

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

    costo_directo_total = df_partidas["Total Directo $"].sum()
    monto_gg = costo_directo_total * (pct_gg / 100.0)
    monto_utilidad = costo_directo_total * (pct_util / 100.0)
    monto_neto = costo_directo_total + monto_gg + monto_utilidad
    monto_iva = monto_neto * 0.19
    monto_bruto = monto_neto + monto_iva

    m1, m2, m3 = st.columns(3)
    m1.metric("Costo Directo Total", f"${costo_directo_total:,.0f}")
    m2.metric(f"GG ({pct_gg}%)", f"${monto_gg:,.0f}")
    m3.metric(f"Utilidad ({pct_util}%)", f"${monto_utilidad:,.0f}")

    m4, m5, m6 = st.columns(3)
    m4.metric("Subtotal Neto", f"${monto_neto:,.0f}")
    m5.metric("IVA (19%)", f"${monto_iva:,.0f}")
    m6.metric("TOTAL PRESUPUESTO BRUTO", f"${monto_bruto:,.0f}")

  conn.close()

# ==========================================
# MÓDULO 6: COTIZACIÓN COMERCIAL Y VERSIONADO
# ==========================================
else:
  st.title("🏷️ Cotización Comercial y Historial de Versiones")

  if not proy_id:
    st.warning("⚠️ Selecciona un proyecto activo.")
  else:
    conn = get_connection()
    st.subheader(f"📌 Gestión de Versiones - Proyecto ID {proy_id}")

    with st.form("form_guardar_version"):
      nom_ver = st.text_input(
          "Nombre / Etiqueta de la Versión:",
          value="V1 - Inspección Inicial en Terreno",
      )
      costo_tot = st.number_input("Monto Directo Estimado ($):", value=1500000)
      if st.form_submit_button("💾 Guardar Versión de Cotización"):
        conn.execute(
            """
                    INSERT INTO cotizaciones_versiones (proyecto_id, version, costo_directo, pct_gg, pct_utilidad, monto_total, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
            (
                proy_id,
                nom_ver,
                costo_tot,
                15.0,
                10.0,
                costo_tot * 1.25 * 1.19,
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ),
        )
        conn.commit()
        st.success("✅ Versión congelada y guardada correctamente.")
        st.rerun()

    df_versiones = pd.read_sql_query(
        "SELECT version AS [Versión], costo_directo AS [Costo Directo $],"
        " monto_total AS [Total Bruto $], fecha AS [Fecha Registro] FROM"
        " cotizaciones_versiones WHERE proyecto_id = ? ORDER BY id DESC",
        conn,
        params=(proy_id,),
    )
    conn.close()

    if not df_versiones.empty:
      st.markdown("### 📜 Historial de Cotizaciones Registradas")
      st.dataframe(df_versiones, use_container_width=True, hide_index=True)
    else:
      st.info("ℹ️ No hay historial de cotizaciones guardado para esta obra.")
