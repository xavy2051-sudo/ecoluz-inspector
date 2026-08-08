# biblioteca_tecnica.py
# ==============================================================================
# BIBLIOTECA TÉCNICA Y MOTOR DE CUBICACIÓN / APU - ECOLUZ
# ==============================================================================

import json
import math
import sqlite3

DB_FILE = "ecoluz_database.db"


def get_connection():
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn


# ------------------------------------------------------------------------------
# ESTRUCTURA MAESTRA DE PARTIDAS Y PREGUNTAS
# ------------------------------------------------------------------------------
CONFIGURACION_PARTIDAS = {
    "Tabiquería / Muros": {
        "categoria": "Obra Gruesa / Terminaciones",
        "preguntas": [
            {
                "campo_id": "largo",
                "etiqueta": "Largo del Muro (m):",
                "tipo_input": "number",
                "valor_default": 3.0,
                "step_val": 0.1,
                "help_text": "Longitud lineal del tabique",
            },
            {
                "campo_id": "alto",
                "etiqueta": "Alto del Muro (m):",
                "tipo_input": "number",
                "valor_default": 2.4,
                "step_val": 0.1,
                "help_text": "Altura del piso al cielo",
            },
            {
                "campo_id": "separacion_montantes",
                "etiqueta": "Distancia entre Montantes:",
                "tipo_input": "select",
                "opciones": ["40 cm", "60 cm"],
                "valor_default": "40 cm",
            },
            {
                "campo_id": "placa_interior",
                "etiqueta": "Tipo de Placa Interior:",
                "tipo_input": "select",
                "opciones": [
                    "Volcanita RH 12.5mm",
                    "Volcanita ST 12.5mm",
                    "OSB 9.5mm",
                ],
                "valor_default": "Volcanita RH 12.5mm",
            },
            {
                "campo_id": "aislacion",
                "etiqueta": "Aislación Térmica / Acústica:",
                "tipo_input": "select",
                "opciones": [
                    "Lana Mineral 50mm",
                    "Lana de Vidrio 50mm",
                    "Sin Aislación",
                ],
                "valor_default": "Lana Mineral 50mm",
            },
        ],
    },
    "Piso / Revestimiento Ceramicado": {
        "categoria": "Terminaciones",
        "preguntas": [
            {
                "campo_id": "largo_piso",
                "etiqueta": "Largo del Piso (m):",
                "tipo_input": "number",
                "valor_default": 2.0,
                "step_val": 0.1,
            },
            {
                "campo_id": "ancho_piso",
                "etiqueta": "Ancho del Piso (m):",
                "tipo_input": "number",
                "valor_default": 1.5,
                "step_val": 0.1,
            },
            {
                "campo_id": "tipo_ceramica",
                "etiqueta": "Formato de Cerámica / Porcelanato:",
                "tipo_input": "select",
                "opciones": [
                    "Cerámica 30x30 cm",
                    "Cerámica 45x45 cm",
                    "Porcelanato 60x60 cm",
                ],
                "valor_default": "Cerámica 30x30 cm",
            },
            {
                "campo_id": "adhesivo",
                "etiqueta": "Tipo de Adhesivo:",
                "tipo_input": "select",
                "opciones": ["Bekron AC", "Bekron DA (Pasta)", "Bekron Standard"],
                "valor_default": "Bekron AC",
            },
        ],
    },
    "Electricidad - Enchufes": {
        "categoria": "Instalaciones Eléctricas",
        "preguntas": [
            {
                "campo_id": "puntos_enchufe",
                "etiqueta": "Cantidad de Puntos de Enchufe:",
                "tipo_input": "number",
                "valor_default": 2,
                "step_val": 1,
            },
            {
                "campo_id": "tipo_canalizacion",
                "etiqueta": "Canalización:",
                "tipo_input": "select",
                "opciones": [
                    "Embutida Conduit 20mm",
                    "Sobrepuesta Catenaria/Canaleta",
                ],
                "valor_default": "Embutida Conduit 20mm",
            },
            {
                "campo_id": "proteccion",
                "etiqueta": "Protección Eléctrica:",
                "tipo_input": "select",
                "opciones": ["Automático 16A + Diferencial 2x25A 30mA", "Ninguna"],
                "valor_default": "Automático 16A + Diferencial 2x25A 30mA",
            },
        ],
    },
    "Cielo / Cielo Falso": {
        "categoria": "Terminaciones",
        "preguntas": [
            {
                "campo_id": "largo_cielo",
                "etiqueta": "Largo del Cielo (m):",
                "tipo_input": "number",
                "valor_default": 2.0,
                "step_val": 0.1,
            },
            {
                "campo_id": "ancho_cielo",
                "etiqueta": "Ancho del Cielo (m):",
                "tipo_input": "number",
                "valor_default": 1.5,
                "step_val": 0.1,
            },
            {
                "campo_id": "tipo_placa_cielo",
                "etiqueta": "Tipo de Placa Cielo:",
                "tipo_input": "select",
                "opciones": ["Volcanita ST 10mm", "Volcanita RH 12.5mm"],
                "valor_default": "Volcanita RH 12.5mm",
            },
        ],
    },
    "Pintura / Empaste": {
        "categoria": "Terminaciones",
        "preguntas": [
            {
                "campo_id": "superficie_pintura",
                "etiqueta": "Superficie a Pintar (m²):",
                "tipo_input": "number",
                "valor_default": 14.4,
                "step_val": 0.5,
            },
            {
                "campo_id": "tipo_pintura",
                "etiqueta": "Tipo de Pintura:",
                "tipo_input": "select",
                "opciones": [
                    "Esmalte al Agua RH",
                    "Látex Vinílico",
                    "Óleo Opaco",
                ],
                "valor_default": "Esmalte al Agua RH",
            },
            {
                "campo_id": "manos",
                "etiqueta": "Número de Manos:",
                "tipo_input": "number",
                "valor_default": 2,
                "step_val": 1,
            },
        ],
    },
    "Instalaciones Sanitarias / Artefactos": {
        "categoria": "Instalaciones Sanitarias",
        "preguntas": [
            {
                "campo_id": "puntos_agua",
                "etiqueta": "Cantidad Puntos Agua (WC/Lavamanos/Ducha):",
                "tipo_input": "number",
                "valor_default": 3,
                "step_val": 1,
            },
            {
                "campo_id": "incluye_artefactos",
                "etiqueta": "Suministro Artefactos Sanitarios:",
                "tipo_input": "select",
                "opciones": [
                    "WC + Lavamanos + Monocomando",
                    "Solo WC",
                    "Solo Lavamanos",
                    "Sin Artefactos",
                ],
                "valor_default": "WC + Lavamanos + Monocomando",
            },
        ],
    },
    "Iluminación - Puntos de Luz": {
        "categoria": "Instalaciones Eléctricas",
        "preguntas": [
            {
                "campo_id": "puntos_luz",
                "etiqueta": "Cantidad de Centros de Luz / Focos:",
                "tipo_input": "number",
                "valor_default": 2,
                "step_val": 1,
            },
            {
                "campo_id": "tipo_foco",
                "etiqueta": "Tipo de Luminaria:",
                "tipo_input": "select",
                "opciones": [
                    "Panel LED Empotrado 18W",
                    "Foco Embutido Spot GU10",
                    "Plafón Sobrepuesto",
                ],
                "valor_default": "Panel LED Empotrado 18W",
            },
        ],
    },
    "Puertas y Cerrajería": {
        "categoria": "Terminaciones",
        "preguntas": [
            {
                "campo_id": "cantidad_puertas",
                "etiqueta": "Cantidad de Puertas:",
                "tipo_input": "number",
                "valor_default": 1,
                "step_val": 1,
            },
            {
                "campo_id": "tipo_puerta",
                "etiqueta": "Tipo de Hoja Puerta:",
                "tipo_input": "select",
                "opciones": [
                    "Puerta Masonite/MDF Prepintada",
                    "Puerta Terciado 75x200cm",
                    "Puerta Roble Solida",
                ],
                "valor_default": "Puerta Masonite/MDF Prepintada",
            },
        ],
    },
}


# ------------------------------------------------------------------------------
# INICIALIZACIÓN DE TABLAS MAESTRAS
# ------------------------------------------------------------------------------
def inicializar_fase1_db():
  conn = get_connection()
  c = conn.cursor()

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
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

  c.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_partida TEXT UNIQUE,
            categoria TEXT,
            config_json TEXT
        )
    """)

  for partida, config in CONFIGURACION_PARTIDAS.items():
    c.execute(
        """
            INSERT OR REPLACE INTO biblioteca_partidas (nombre_partida, categoria, config_json)
            VALUES (?, ?, ?)
        """,
        (partida, config["categoria"], json.dumps(config, ensure_ascii=False)),
    )

  conn.commit()
  conn.close()


def obtener_lista_partidas():
  """Retorna la lista de todas las partidas registradas."""
  return list(CONFIGURACION_PARTIDAS.keys())


def obtener_configuracion_partida(nombre_partida):
  """Retorna la configuración de preguntas de una partida."""
  return CONFIGURACION_PARTIDAS.get(nombre_partida, None)


# ------------------------------------------------------------------------------
# MOTOR GENERAL DE CUBICACIÓN Y CÁLCULO APU
# ------------------------------------------------------------------------------
def calcular_cubicacion_y_apu(nombre_partida, datos_usuario):
  materiales = []
  apu = {
      "costo_materiales_clp": 0,
      "costo_mano_obra_clp": 0,
      "hh_mano_obra": 0.0,
      "costo_directo_total_clp": 0,
  }

  # 1. TABIQUERÍA / MUROS
  if nombre_partida == "Tabiquería / Muros":
    largo = float(datos_usuario.get("largo", 3.0))
    alto = float(datos_usuario.get("alto", 2.4))
    separacion = datos_usuario.get("separacion_montantes", "40 cm")
    placa = datos_usuario.get("placa_interior", "Volcanita RH 12.5mm")
    aislacion = datos_usuario.get("aislacion", "Lana Mineral 50mm")

    area = largo * alto
    dist_m = 0.40 if separacion == "40 cm" else 0.60

    cant_soleras = math.ceil((largo * 2 / 3.0) * 1.05)
    cant_montantes = math.ceil(((largo / dist_m) + 1) * 1.05)
    cant_planchas = math.ceil((area * 2 / (1.2 * 2.4)) * 1.10)
    tornillos_framing = cant_montantes * 12
    tornillos_placa = cant_planchas * 70

    materiales.append({
        "insumo": "Solera Cintas Galvanizada 60CA08 (3m)",
        "tipo": "Principal",
        "cantidad": cant_soleras,
        "unidad": "tiras",
        "precio_unit_clp": 4200,
    })
    materiales.append({
        "insumo": "Montante Galvanizado 60CA08 (3m)",
        "tipo": "Principal",
        "cantidad": cant_montantes,
        "unidad": "tiras",
        "precio_unit_clp": 4500,
    })
    materiales.append({
        "insumo": f"Placa {placa} (1.20x2.40m)",
        "tipo": "Principal",
        "cantidad": cant_planchas,
        "unidad": "planchas",
        "precio_unit_clp": 11500,
    })
    materiales.append({
        "insumo": "Tornillos Cabeza Lenteja #8x1/2 (Estructura)",
        "tipo": "Dependiente",
        "cantidad": tornillos_framing,
        "unidad": "unidades",
        "precio_unit_clp": 25,
    })
    materiales.append({
        "insumo": "Tornillos Volcanita Cabeza Trompeta 6x1-5/8",
        "tipo": "Dependiente",
        "cantidad": tornillos_placa,
        "unidad": "unidades",
        "precio_unit_clp": 30,
    })

    if aislacion != "Sin Aislación":
      rollos = math.ceil(area / 7.2)
      materiales.append({
          "insumo": f"Aislación {aislacion}",
          "tipo": "Dependiente",
          "cantidad": rollos,
          "unidad": "rollos",
          "precio_unit_clp": 18500,
      })

    materiales.append({
        "insumo": "Cinta Junta Invisible Fibra/Papel",
        "tipo": "Dependiente",
        "cantidad": round(area * 1.5, 2),
        "unidad": "ml",
        "precio_unit_clp": 250,
    })
    materiales.append({
        "insumo": "Masilla Junta / Pasta Muro",
        "tipo": "Dependiente",
        "cantidad": round(area * 1.0, 2),
        "unidad": "kg",
        "precio_unit_clp": 1200,
    })

    hh = round(area * 0.38, 2)

  # 2. PISO CERAMICADO
  elif nombre_partida == "Piso / Revestimiento Ceramicado":
    largo = float(datos_usuario.get("largo_piso", 2.0))
    ancho = float(datos_usuario.get("ancho_piso", 1.5))
    tipo_cer = datos_usuario.get("tipo_ceramica", "Cerámica 30x30 cm")
    adhesivo = datos_usuario.get("adhesivo", "Bekron AC")

    area = largo * ancho
    cajas = math.ceil((area * 1.10) / 1.8)  # Rinde ~1.8m2 por caja
    sacos_adhesivo = math.ceil(area / 4.0)  # ~4m2 por saco de 25kg
    frague_kg = round(area * 0.5, 1)

    materiales.append({
        "insumo": f"Caja {tipo_cer}",
        "tipo": "Principal",
        "cantidad": cajas,
        "unidad": "cajas",
        "precio_unit_clp": 14900,
    })
    materiales.append({
        "insumo": f"Adhesivo {adhesivo} 25kg",
        "tipo": "Dependiente",
        "cantidad": sacos_adhesivo,
        "unidad": "sacos",
        "precio_unit_clp": 7800,
    })
    materiales.append({
        "insumo": "Fragüe Impermeable Anti-hongos 1kg",
        "tipo": "Dependiente",
        "cantidad": math.ceil(frague_kg),
        "unidad": "bolsas",
        "precio_unit_clp": 2900,
    })
    materiales.append({
        "insumo": "Crucetas Plásticas 3mm (Bolsa 100un)",
        "tipo": "Dependiente",
        "cantidad": 1,
        "unidad": "bolsa",
        "precio_unit_clp": 1500,
    })

    hh = round(area * 0.5, 2)

  # 3. ELECTRICIDAD ENCHUFES
  elif nombre_partida == "Electricidad - Enchufes":
    puntos = int(datos_usuario.get("puntos_enchufe", 2))
    canal = datos_usuario.get("tipo_canalizacion", "Embutida Conduit 20mm")

    materiales.append({
        "insumo": "Módulo Enchufe Doble 10A/16A con Placa",
        "tipo": "Principal",
        "cantidad": puntos,
        "unidad": "unidades",
        "precio_unit_clp": 4500,
    })
    materiales.append({
        "insumo": "Caja Condulet / Empotrar Rectangular",
        "tipo": "Dependiente",
        "cantidad": puntos,
        "unidad": "unidades",
        "precio_unit_clp": 850,
    })
    materiales.append({
        "insumo": f"Tubería {canal} (3m)",
        "tipo": "Dependiente",
        "cantidad": puntos * 2,
        "unidad": "tiras",
        "precio_unit_clp": 1900,
    })
    materiales.append({
        "insumo": "Cable Alambre EVA 2.5mm² (Rojo/Blanco/Verde)",
        "tipo": "Dependiente",
        "cantidad": puntos * 15,
        "unidad": "metros",
        "precio_unit_clp": 480,
    })

    hh = round(puntos * 1.2, 2)

  # 4. CIELO FALSO
  elif nombre_partida == "Cielo / Cielo Falso":
    largo = float(datos_usuario.get("largo_cielo", 2.0))
    ancho = float(datos_usuario.get("ancho_cielo", 1.5))
    placa = datos_usuario.get("tipo_placa_cielo", "Volcanita RH 12.5mm")

    area = largo * ancho
    planchas = math.ceil((area * 1.10) / (1.2 * 2.4))
    perfiles_omega = math.ceil((largo / 0.5) * (ancho / 3.0))

    materiales.append({
        "insumo": f"Placa {placa} (1.20x2.40m)",
        "tipo": "Principal",
        "cantidad": planchas,
        "unidad": "planchas",
        "precio_unit_clp": 11500,
    })
    materiales.append({
        "insumo": "Perfil Omega Galvanizado (3m)",
        "tipo": "Dependiente",
        "cantidad": max(perfiles_omega, 3),
        "unidad": "tiras",
        "precio_unit_clp": 3800,
    })
    materiales.append({
        "insumo": "Tornillos Volcanita 6x1",
        "tipo": "Dependiente",
        "cantidad": planchas * 50,
        "unidad": "unidades",
        "precio_unit_clp": 25,
    })

    hh = round(area * 0.45, 2)

  # 5. PINTURA / EMPASTE
  elif nombre_partida == "Pintura / Empaste":
    area = float(datos_usuario.get("superficie_pintura", 14.4))
    tipo_p = datos_usuario.get("tipo_pintura", "Esmalte al Agua RH")
    manos = int(datos_usuario.get("manos", 2))

    tinetas = math.ceil((area * manos) / 40.0)  # Rinde ~40m2/tineta 1 galón
    pasta_kg = round(area * 0.8, 1)

    materiales.append({
        "insumo": f"Galón Pintura {tipo_p}",
        "tipo": "Principal",
        "cantidad": max(tinetas, 1),
        "unidad": "galones",
        "precio_unit_clp": 24900,
    })
    materiales.append({
        "insumo": "Pasta Muro Interior (Saco/Pasta 15kg)",
        "tipo": "Dependiente",
        "cantidad": math.ceil(pasta_kg / 15.0),
        "unidad": "tineta/saco",
        "precio_unit_clp": 9500,
    })
    materiales.append({
        "insumo": "Kit Pintor (Rodillo Antigota + Brocha + Bandeja)",
        "tipo": "Dependiente",
        "cantidad": 1,
        "unidad": "set",
        "precio_unit_clp": 6900,
    })

    hh = round(area * 0.25, 2)

  # 6. INSTALACIONES SANITARIAS / ARTEFACTOS
  elif nombre_partida == "Instalaciones Sanitarias / Artefactos":
    puntos = int(datos_usuario.get("puntos_agua", 3))
    artefacto = datos_usuario.get(
        "incluye_artefactos", "WC + Lavamanos + Monocomando"
    )

    materiales.append({
        "insumo": "Punto Agua Potable PPR/PEX + Fitting",
        "tipo": "Principal",
        "cantidad": puntos,
        "unidad": "puntos",
        "precio_unit_clp": 18500,
    })
    materiales.append({
        "insumo": "Punto Desagüe PVC Sanitarias 40/50/110mm",
        "tipo": "Principal",
        "cantidad": puntos,
        "unidad": "puntos",
        "precio_unit_clp": 14200,
    })

    if "WC" in artefacto:
      materiales.append({
          "insumo": "WC Sifónico One-Piece con Flexibles y Llave Paso",
          "tipo": "Artefacto",
          "cantidad": 1,
          "unidad": "unidad",
          "precio_unit_clp": 68000,
      })
    if "Lavamanos" in artefacto:
      materiales.append({
          "insumo": "Lavamanos con Pedestal/Vanitorio + Monocomando",
          "tipo": "Artefacto",
          "cantidad": 1,
          "unidad": "unidad",
          "precio_unit_clp": 45000,
      })

    hh = round(puntos * 2.5, 2)

  # 7. ILUMINACIÓN
  elif nombre_partida == "Iluminación - Puntos de Luz":
    puntos = int(datos_usuario.get("puntos_luz", 2))
    foco = datos_usuario.get("tipo_foco", "Panel LED Empotrado 18W")

    materiales.append({
        "insumo": f"Luminaria {foco}",
        "tipo": "Principal",
        "cantidad": puntos,
        "unidad": "unidades",
        "precio_unit_clp": 7900,
    })
    materiales.append({
        "insumo": "Interruptor 9/12 o 9/15 con Placa",
        "tipo": "Dependiente",
        "cantidad": 1,
        "unidad": "unidad",
        "precio_unit_clp": 3800,
    })
    materiales.append({
        "insumo": "Cable Alambre EVA 1.5mm² (Blanco/Rojo)",
        "tipo": "Dependiente",
        "cantidad": puntos * 10,
        "unidad": "metros",
        "precio_unit_clp": 350,
    })

    hh = round(puntos * 1.0, 2)

  # 8. PUERTAS Y CERRAJERÍA
  else:
    cant = int(datos_usuario.get("cantidad_puertas", 1))
    tipo_p = datos_usuario.get(
        "tipo_puerta", "Puerta Masonite/MDF Prepintada"
    )

    materiales.append({
        "insumo": f"Hoja {tipo_p}",
        "tipo": "Principal",
        "cantidad": cant,
        "unidad": "unidades",
        "precio_unit_clp": 32000,
    })
    materiales.append({
        "insumo": "Marco Puino / MDF 35x70mm Set Completo",
        "tipo": "Dependiente",
        "cantidad": cant,
        "unidad": "sets",
        "precio_unit_clp": 18500,
    })
    materiales.append({
        "insumo": "Cerradura Pomo / Lote Baño-Dormitorio",
        "tipo": "Dependiente",
        "cantidad": cant,
        "unidad": "unidades",
        "precio_unit_clp": 12900,
    })
    materiales.append({
        "insumo": "Bisagras Galvanizadas 3.5x3.5 (Pack x3)",
        "tipo": "Dependiente",
        "cantidad": cant,
        "unidad": "packs",
        "precio_unit_clp": 3500,
    })

    hh = round(cant * 3.0, 2)

  # CÁLCULO FINANCIERO DEL APU
  costo_mat = sum(m["cantidad"] * m["precio_unit_clp"] for m in materiales)
  costo_mo = int(hh * 7500)  # Valor HH promedio $7.500 CLP

  apu["costo_materiales_clp"] = costo_mat
  apu["costo_mano_obra_clp"] = costo_mo
  apu["hh_mano_obra"] = hh
  apu["costo_directo_total_clp"] = costo_mat + costo_mo

  return {"materiales": materiales, "apu": apu}
