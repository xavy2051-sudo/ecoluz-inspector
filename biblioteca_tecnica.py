# biblioteca_tecnica.py
# ==============================================================================
# CEREBRO CONSTRUCTIVO Y MOTOR DE CUBICACIÓN TÉCNICA - ECOLUZ ITO
# ==============================================================================

import json
import math
import sqlite3

DB_FILE = "ecoluz_database.db"


def get_connection():
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn


# ==============================================================================
# 1. MIGRACIÓN NO DESTRUCTIVA Y CREACIÓN DE TABLAS MAESTRAS
# ==============================================================================
def inicializar_fase1_db():
  """Crea las tablas relacionales para la Biblioteca Técnica sin destruir datos históricos."""
  conn = get_connection()
  c = conn.cursor()

  # A. Mantener o crear la tabla base de recintos
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

  # Verificar adición no destructiva de la columna JSON
  c.execute("PRAGMA table_info(recintos_levantamiento)")
  columns = [row["name"] for row in c.fetchall()]
  if "datos_tecnicos_json" not in columns:
    c.execute(
        "ALTER TABLE recintos_levantamiento ADD COLUMN datos_tecnicos_json"
        " TEXT"
    )

  # B. Tabla Maestra de Partidas
  c.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_partida TEXT UNIQUE NOT NULL,
            nombre_partida TEXT NOT NULL,
            categoria_sistema TEXT NOT NULL,
            unidad_medida TEXT NOT NULL,
            plantilla_eett_base TEXT
        )
    """)

  # C. Tabla Maestra de Preguntas Dinámicas
  c.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_preguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER NOT NULL,
            campo_id TEXT NOT NULL,
            etiqueta TEXT NOT NULL,
            tipo_input TEXT NOT NULL, -- 'number', 'select', 'text', 'boolean'
            opciones_json TEXT,       -- Lista JSON de opciones para select
            valor_default TEXT,
            step_val REAL DEFAULT 1.0,
            help_text TEXT,
            orden INTEGER DEFAULT 0,
            FOREIGN KEY (partida_id) REFERENCES biblioteca_partidas(id)
        )
    """)

  # D. Tabla Maestra de Reglas de Materiales y Dependencias
  c.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_materiales_reglas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER NOT NULL,
            insumo_nombre TEXT NOT NULL,
            unidad TEXT NOT NULL,
            es_dependencia_secundaria INTEGER DEFAULT 0, -- 0: Principal, 1: Dependiente
            formula_cantidad TEXT NOT NULL,               -- Expresión o regla técnica
            porcentaje_merma REAL DEFAULT 0.0,
            FOREIGN KEY (partida_id) REFERENCES biblioteca_partidas(id)
        )
    """)

  # E. Tabla Maestra de APU Base (Estructura de Costos Directos)
  c.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_apu_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER NOT NULL,
            codigo_insumo TEXT NOT NULL,
            tipo_recurso TEXT NOT NULL, -- 'Material', 'Mano_Obra', 'Equipo'
            unidad TEXT NOT NULL,
            rendimiento_unitario REAL NOT NULL,
            precio_unitario_clp REAL NOT NULL,
            FOREIGN KEY (partida_id) REFERENCES biblioteca_partidas(id)
        )
    """)

  conn.commit()
  conn.close()
  poblar_biblioteca_baño()


# ==============================================================================
# 2. POBLAMIENTO INICIAL: CASO DE PRUEBA REMODELACIÓN DE BAÑO
# ==============================================================================
def poblar_biblioteca_baño():
  """Inserta los esquemas técnicos completos para las partidas del Baño de Prueba."""
  conn = get_connection()
  c = conn.cursor()

  partidas_baño = [
      {
          "codigo": "PAR_TAB_MURO",
          "nombre": "Tabiquería / Muros",
          "categoria": "Estructuras y Tabiques",
          "unidad": "m²",
          "eett": (
              "Suministro e instalación de tabique estructural en perfilería"
              " Metalcom galvanizada Cintas/Montantes 60CA08 a 40cm."
              " Revestimiento en placas Volcanita RH de 12.5mm fijadas con"
              " tornillos trompeta, aislación interna y tratamiento completo"
              " de juntas."
          ),
          "preguntas": [
              {
                  "campo": "largo",
                  "etiqueta": "Largo del Muro/Tabique (m):",
                  "tipo": "number",
                  "val": "2.5",
                  "step": 0.1,
                  "help": "Longitud lineal",
                  "orden": 1,
              },
              {
                  "campo": "alto",
                  "etiqueta": "Alto Comercial (m):",
                  "tipo": "number",
                  "val": "2.4",
                  "step": 0.1,
                  "help": "Altura piso a cielo",
                  "orden": 2,
              },
              {
                  "campo": "tipo_estructura",
                  "etiqueta": "Estructura Soporte:",
                  "tipo": "select",
                  "opciones": [
                      "Metalcom 60CA08 (Galvanizado)",
                      "Metalcom 90CA08",
                      "Pino 2x3 pulgadas",
                  ],
                  "val": "Metalcom 60CA08 (Galvanizado)",
                  "orden": 3,
              },
              {
                  "campo": "separacion_montantes",
                  "etiqueta": "Separación Montantes:",
                  "tipo": "select",
                  "opciones": ["40 cm (Zona Húmeda)", "60 cm"],
                  "val": "40 cm (Zona Húmeda)",
                  "orden": 4,
              },
              {
                  "campo": "placa_interior",
                  "etiqueta": "Placa de Revestimiento:",
                  "tipo": "select",
                  "opciones": [
                      "Volcanita RH 12.5mm",
                      "Permanit Fibrocemento 6mm",
                  ],
                  "val": "Volcanita RH 12.5mm",
                  "orden": 5,
              },
              {
                  "campo": "aislacion",
                  "etiqueta": "Aislación Interna:",
                  "tipo": "select",
                  "opciones": [
                      "Lana Mineral 50mm",
                      "Lana de Vidrio 50mm",
                      "Sin Aislación",
                  ],
                  "val": "Lana Mineral 50mm",
                  "orden": 6,
              },
              {
                  "campo": "impermeabilizacion",
                  "etiqueta": "Impermeabilización Zócalo:",
                  "tipo": "select",
                  "opciones": [
                      "Membrana Elástica Acrílica + Malla",
                      "Sin Impermeabilización",
                  ],
                  "val": "Membrana Elástica Acrílica + Malla",
                  "orden": 7,
              },
          ],
      },
      {
          "codigo": "PAR_PISO_CER",
          "nombre": "Piso / Revestimiento Ceramicado",
          "categoria": "Terminaciones de Piso",
          "unidad": "m²",
          "eett": (
              "Instalación de pavimento cerámico/porcelanato antideslizante para"
              " zonas húmedas, asentado con adhesivo impermeable Bekron AC,"
              " fraguado de alta resistencia y sello perimetral."
          ),
          "preguntas": [
              {
                  "campo": "largo_piso",
                  "etiqueta": "Largo del Piso (m):",
                  "tipo": "number",
                  "val": "2.0",
                  "step": 0.1,
                  "orden": 1,
              },
              {
                  "campo": "ancho_piso",
                  "etiqueta": "Ancho del Piso (m):",
                  "tipo": "number",
                  "val": "1.8",
                  "step": 0.1,
                  "orden": 2,
              },
              {
                  "campo": "tipo_ceramica",
                  "etiqueta": "Tipo de Ceramica/Porcelanato:",
                  "tipo": "select",
                  "opciones": [
                      "Cerámica Antideslizante 33x33",
                      "Porcelanato 60x60",
                  ],
                  "val": "Cerámica Antideslizante 33x33",
                  "orden": 3,
              },
              {
                  "campo": "adhesivo",
                  "etiqueta": "Tipo de Adhesivo:",
                  "tipo": "select",
                  "opciones": [
                      "Bekron AC (Pasta Zona Húmeda)",
                      "Bekron Standard",
                  ],
                  "val": "Bekron AC (Pasta Zona Húmeda)",
                  "orden": 4,
              },
          ],
      },
      {
          "codigo": "PAR_ELE_ENCHUFE",
          "nombre": "Electricidad - Enchufes",
          "categoria": "Instalación Eléctrica",
          "unidad": "ptos",
          "eett": (
              "Suministro e instalación de puntos de enchufe monofásicos"
              " embutidos, canalizados en tubería conduit rígida 20mm con"
              " conductores EVA 2.5mm² libre de halógenos conforme norma RIC N°04."
          ),
          "preguntas": [
              {
                  "campo": "num_enchufes",
                  "etiqueta": "Cantidad de Puntos de Enchufe Doble:",
                  "tipo": "number",
                  "val": "2",
                  "step": 1.0,
                  "orden": 1,
              },
              {
                  "campo": "canalizacion",
                  "etiqueta": "Canalización:",
                  "tipo": "select",
                  "opciones": [
                      "Conduit Rígido PVC 20mm",
                      "Tubería Flexible 20mm",
                  ],
                  "val": "Conduit Rígido PVC 20mm",
                  "orden": 2,
              },
              {
                  "campo": "conductor",
                  "etiqueta": "Conductor Eléctrico:",
                  "tipo": "select",
                  "opciones": [
                      "Cable EVA H07Z1-K 2.5 mm²",
                      "Cable NYA 2.5 mm²",
                  ],
                  "val": "Cable EVA H07Z1-K 2.5 mm²",
                  "orden": 3,
              },
              {
                  "campo": "proteccion_dif",
                  "etiqueta": "Protección Diferencial:",
                  "tipo": "select",
                  "opciones": [
                      "Interruptor Diferencial 2x25A 30mA",
                      "Existente en Tablero",
                  ],
                  "val": "Interruptor Diferencial 2x25A 30mA",
                  "orden": 4,
              },
          ],
      },
  ]

  for p in partidas_baño:
    c.execute(
        """
            INSERT OR REPLACE INTO biblioteca_partidas 
            (codigo_partida, nombre_partida, categoria_sistema, unidad_medida, plantilla_eett_base)
            VALUES (?, ?, ?, ?, ?)
        """,
        (
            p["codigo"],
            p["nombre"],
            p["categoria"],
            p["unidad"],
            p["eett"],
        ),
    )

    partida_id = c.lastrowid or c.execute(
        "SELECT id FROM biblioteca_partidas WHERE codigo_partida=?",
        (p["codigo"],),
    ).fetchone()[0]

    # Limpiar e insertar preguntas relacionales
    c.execute(
        "DELETE FROM biblioteca_preguntas WHERE partida_id=?", (partida_id,)
    )
    for q in p["preguntas"]:
      opciones_str = json.dumps(q.get("opciones", []))
      c.execute(
          """
                INSERT INTO biblioteca_preguntas 
                (partida_id, campo_id, etiqueta, tipo_input, opciones_json, valor_default, step_val, help_text, orden)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
          (
              partida_id,
              q["campo"],
              q["etiqueta"],
              q["tipo"],
              opciones_str,
              q["val"],
              q.get("step", 1.0),
              q.get("help", ""),
              q["orden"],
          ),
      )

  conn.commit()
  conn.close()


# ==============================================================================
# 3. CONSULTA DINÁMICA DE PREGUNTAS POR PARTIDA
# ==============================================================================
def obtener_configuracion_partida(nombre_o_codigo):
  """Retorna la lista de preguntas relacionales para la partida seleccionada."""
  conn = get_connection()
  c = conn.cursor()

  c.execute(
      """
        SELECT id, codigo_partida, nombre_partida, categoria_sistema, unidad_medida, plantilla_eett_base 
        FROM biblioteca_partidas 
        WHERE nombre_partida = ? OR codigo_partida = ?
    """,
      (nombre_o_codigo, nombre_o_codigo),
  )

  partida = c.fetchone()
  if not partida:
    conn.close()
    return None

  p_id = partida["id"]
  c.execute(
      """
        SELECT campo_id, etiqueta, tipo_input, opciones_json, valor_default, step_val, help_text
        FROM biblioteca_preguntas 
        WHERE partida_id = ? 
        ORDER BY orden ASC
    """,
      (p_id,),
  )

  preguntas_rows = c.fetchall()
  preguntas = []
  for pr in preguntas_rows:
    preguntas.append({
        "campo_id": pr["campo_id"],
        "etiqueta": pr["etiqueta"],
        "tipo_input": pr["tipo_input"],
        "opciones": json.loads(pr["opciones_json"])
        if pr["opciones_json"]
        else [],
        "valor_default": pr["valor_default"],
        "step_val": pr["step_val"],
        "help_text": pr["help_text"],
    })

  conn.close()
  return {
      "id": p_id,
      "codigo": partida["codigo_partida"],
      "nombre": partida["nombre_partida"],
      "categoria": partida["categoria_sistema"],
      "unidad": partida["unidad_medida"],
      "eett_base": partida["plantilla_eett_base"],
      "preguntas": preguntas,
  }


# ==============================================================================
# 4. MOTOR DE CUBICACIÓN TÉCNICA, MATERIALES Y DEPENDENCIAS
# ==============================================================================
def calcular_cubicacion_y_apu(nombre_partida, respuestas_dict):
  """Calcula geométricamente las cantidades reales, mermas, materiales dependientes

  y la matriz APU sin requerir reingreso manual.
  """
  materiales = []
  apu_costo_directo = []

  # A. TABIQUERÍA Y MUROS
  if "Tabiquería" in nombre_partida or "Muros" in nombre_partida:
    largo = float(respuestas_dict.get("largo", 0.0))
    alto = float(respuestas_dict.get("alto", 0.0))
    area_m2 = round(largo * alto, 2)

    sep_cm = 40 if "40" in str(respuestas_dict.get("separacion_montantes")) else 60
    distancia_m = sep_cm / 100.0

    # Soleras (Metros lineales / Tiras 3m) con 5% merma
    ml_soleras = largo * 2
    tiras_soleras = math.ceil((ml_soleras * 1.05) / 3.0)

    # Montantes con 8% merma
    num_montantes = math.ceil(largo / distancia_m) + 1
    tiras_montantes = math.ceil((num_montantes * alto * 1.08) / 3.0)

    # Placas Volcanita RH (2 caras de revestimiento) con 10% merma
    area_placas_total = area_m2 * 2
    planchas_volcanita = math.ceil((area_placas_total * 1.10) / 2.88)

    # Materiales Dependientes (Tornillos, Aislación, Cinta, Masilla)
    tornillos_framing = math.ceil(area_m2 * 15)
    tornillos_volcanita = math.ceil(area_placas_total * 30)
    rollos_lana = math.ceil((area_m2 * 1.05) / 10.0)
    cinta_junta_ml = round(area_m2 * 1.8, 1)
    masilla_kg = round(area_m2 * 1.2, 1)

    materiales = [
        {
            "insumo": "Solera Cintas Galvanizada 60CA08 (3m)",
            "tipo": "Principal",
            "cantidad": tiras_soleras,
            "unidad": "tiras",
        },
        {
            "insumo": "Montante Galvanizado 60CA08 (3m)",
            "tipo": "Principal",
            "cantidad": tiras_montantes,
            "unidad": "tiras",
        },
        {
            "insumo": f"Placa {respuestas_dict.get('placa_interior')} (1.20x2.40m)",
            "tipo": "Principal",
            "cantidad": planchas_volcanita,
            "unidad": "planchas",
        },
        {
            "insumo": "Tornillos Cabeza Lenteja #8x1/2 (Estructura)",
            "tipo": "Dependiente",
            "cantidad": tornillos_framing,
            "unidad": "unidades",
        },
        {
            "insumo": "Tornillos Volcanita Cabeza Trompeta 6x1-5/8",
            "tipo": "Dependiente",
            "cantidad": tornillos_volcanita,
            "unidad": "unidades",
        },
        {
            "insumo": f"Aislación {respuestas_dict.get('aislacion')}",
            "tipo": "Dependiente",
            "cantidad": rollos_lana,
            "unidad": "rollos",
        },
        {
            "insumo": "Cinta Junta Invisible Fibra/Papel",
            "tipo": "Dependiente",
            "cantidad": cinta_junta_ml,
            "unidad": "ml",
        },
        {
            "insumo": "Masilla Junta / Pasta Muro",
            "tipo": "Dependiente",
            "cantidad": masilla_kg,
            "unidad": "kg",
        },
    ]

    # Precios unitarios de referencia para APU en Chile (CLP)
    costo_mat = (
        (tiras_soleras * 3800)
        + (tiras_montantes * 4200)
        + (planchas_volcanita * 11900)
        + (tornillos_framing * 15)
        + (tornillos_volcanita * 20)
        + (rollos_lana * 18500)
    )
    hh_carpintero = round(area_m2 * 0.45, 2)  # 0.45 HH/m²
    costo_mo = hh_carpintero * 7500

    apu_costo_directo = {
        "m2_calculados": area_m2,
        "costo_materiales_clp": costo_mat,
        "hh_mano_obra": hh_carpintero,
        "costo_mano_obra_clp": costo_mo,
        "costo_directo_total_clp": costo_mat + costo_mo,
    }

  # B. PISO CERÁMICO
  elif "Piso" in nombre_partida:
    largo = float(respuestas_dict.get("largo_piso", 0.0))
    ancho = float(respuestas_dict.get("ancho_piso", 0.0))
    area_m2 = round(largo * ancho, 2)

    cajas_ceramica = math.ceil((area_m2 * 1.12) / 1.5)  # 12% merma
    sacos_bekron = math.ceil(area_m2 / 4.0)
    kg_frague = round(area_m2 * 0.5, 1)

    materiales = [
        {
            "insumo": f"{respuestas_dict.get('tipo_ceramica')}",
            "tipo": "Principal",
            "cantidad": cajas_ceramica,
            "unidad": "cajas (~1.5m²)",
        },
        {
            "insumo": f"Adhesivo {respuestas_dict.get('adhesivo')} (25kg)",
            "tipo": "Dependiente",
            "cantidad": sacos_bekron,
            "unidad": "sacos/tinetas",
        },
        {
            "insumo": "Fragüe Impermeable Zonas Húmedas",
            "tipo": "Dependiente",
            "cantidad": kg_frague,
            "unidad": "kg",
        },
        {
            "insumo": "Crucetas Separadoras Plásticas",
            "tipo": "Dependiente",
            "cantidad": 1,
            "unidad": "bolsa(100un)",
        },
    ]

    costo_mat = (cajas_ceramica * 14900) + (sacos_bekron * 11500) + (kg_frague * 2200)
    hh_instalador = round(area_m2 * 0.6, 2)
    costo_mo = hh_instalador * 8000

    apu_costo_directo = {
        "m2_calculados": area_m2,
        "costo_materiales_clp": costo_mat,
        "hh_mano_obra": hh_instalador,
        "costo_mano_obra_clp": costo_mo,
        "costo_directo_total_clp": costo_mat + costo_mo,
    }

  # C. ELECTRICIDAD ENCHUFES
  elif "Electricidad" in nombre_partida or "Enchufes" in nombre_partida:
    ptos = int(respuestas_dict.get("num_enchufes", 0))

    tiras_conduit = math.ceil((ptos * 4.0) / 3.0)
    rollos_cable = math.ceil((ptos * 12.0) / 100.0)

    materiales = [
        {
            "insumo": "Módulos Enchufe Doble 10A/16A + Placa",
            "tipo": "Principal",
            "cantidad": ptos,
            "unidad": "juegos",
        },
        {
            "insumo": f"Tubería {respuestas_dict.get('canalizacion')} (3m)",
            "tipo": "Dependiente",
            "cantidad": tiras_conduit,
            "unidad": "tiras",
        },
        {
            "insumo": f"Conductor {respuestas_dict.get('conductor')}",
            "tipo": "Dependiente",
            "cantidad": rollos_cable,
            "unidad": "rollo(s) 100m",
        },
        {
            "insumo": "Cajas de Embutir Aislantes Condulet",
            "tipo": "Dependiente",
            "cantidad": ptos,
            "unidad": "unidades",
        },
    ]

    costo_mat = (ptos * 4500) + (tiras_conduit * 1800) + (rollos_cable * 32000)
    hh_electricista = round(ptos * 1.2, 2)
    costo_mo = hh_electricista * 9500

    apu_costo_directo = {
        "puntos_calculados": ptos,
        "costo_materiales_clp": costo_mat,
        "hh_mano_obra": hh_electricista,
        "costo_mano_obra_clp": costo_mo,
        "costo_directo_total_clp": costo_mat + costo_mo,
    }

  return {"materiales": materiales, "apu": apu_costo_directo}


# Inicialización automática al cargar el módulo
inicializar_fase1_db()
