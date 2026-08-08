# biblioteca_tecnica.py
# ==============================================================================
# BIBLIOTECA TÉCNICA Y MOTOR DE CUBICACIÓN PARA ECOLUZ / ITO
# ==============================================================================

import math
import streamlit as st

BIBLIOTECA_TECNICA = {
    "Tabiquería / Muros": {
        "categoria": "Estructuras y Tabiquería",
        "unidad_medida": "m²",
        "preguntas": [
            {
                "id": "largo",
                "label": "Largo del Tabique (m):",
                "tipo": "number",
                "default": 2.5,
                "step": 0.1,
                "help": "Longitud lineal del tabique.",
            },
            {
                "id": "alto",
                "label": "Alto / Altura Comercial (m):",
                "tipo": "number",
                "default": 2.4,
                "step": 0.1,
                "help": "Altura medida desde radier/piso hasta cielo.",
            },
            {
                "id": "tipo_estructura",
                "label": "Estructura Soporte:",
                "tipo": "select",
                "opciones": [
                    "Metalcom Montantes/Soleras 60CA08 (Galvanizado)",
                    "Metalcom Montantes/Soleras 90CA08",
                    "Madera Pino 2x3 pulgadas",
                    "Madera Pino 2x2 pulgadas",
                ],
                "default": "Metalcom Montantes/Soleras 60CA08 (Galvanizado)",
            },
            {
                "id": "separacion_montantes",
                "label": "Distancia entre Montantes / Pies Derechos:",
                "tipo": "select",
                "opciones": ["40 cm (Recomendado Zonas Húmedas)", "60 cm"],
                "default": "40 cm (Recomendado Zonas Húmedas)",
            },
            {
                "id": "tipo_placa",
                "label": "Placa de Revestimiento Interior/Zona Húmeda:",
                "tipo": "select",
                "opciones": [
                    "Volcanita RH 12.5mm (Resistente a Humedad - Verde)",
                    "Volcanita ST 11mm (Estándar)",
                    "Permanit Fibrocemento 6mm",
                    "Glasroc X 12.5mm",
                ],
                "default": "Volcanita RH 12.5mm (Resistente a Humedad - Verde)",
            },
            {
                "id": "aislacion",
                "label": "Aislación Térmica / Acústica Interior:",
                "tipo": "select",
                "opciones": [
                    "Lana de Vidrio Rollo 50mm",
                    "Lana Mineral Panel 50mm",
                    "Poliestireno Expandido (EPS) 50mm",
                    "Sin Aislación",
                ],
                "default": "Lana de Vidrio Rollo 50mm",
            },
            {
                "id": "impermeabilizacion",
                "label": "Membrana / Impermeabilización de Zócalo:",
                "tipo": "select",
                "opciones": [
                    "Membrana Elástica Acrílica + Banda de Refuerzo",
                    "Barrera de Vapor Polietileno 0.1mm",
                    "Sin Impermeabilización",
                ],
                "default": "Membrana Elástica Acrílica + Banda de Refuerzo",
            },
        ],
    },
    "Instalación Eléctrica General": {
        "categoria": "Instalaciones Eléctricas",
        "unidad_medida": "ptos",
        "preguntas": [
            {
                "id": "num_enchufes",
                "label": "Puntos de Enchufes (Doble/Simple 10A/16A):",
                "tipo": "number",
                "default": 2,
                "step": 1,
            },
            {
                "id": "num_centros",
                "label": "Centros de Alumbrado (Cajas de Techo/Pared):",
                "tipo": "number",
                "default": 1,
                "step": 1,
            },
            {
                "id": "num_interruptores",
                "label": "Interruptores (9/12, 9/15, 9/24):",
                "tipo": "number",
                "default": 1,
                "step": 1,
            },
            {
                "id": "num_fuerza",
                "label": "Líneas Dedicadas / Fuerza / Clima (Cargas pesadas):",
                "tipo": "number",
                "default": 0,
                "step": 1,
            },
            {
                "id": "tipo_canalizacion",
                "label": "Tipo de Canalización Predominante:",
                "tipo": "select",
                "opciones": [
                    "Conduit Rígido PVC 20mm (RIC N°04)",
                    "Tubería Flexible Conduit PVC 20mm",
                    "Tubería EMT 3/4 en Superficie",
                    "Cables en Moldura / Cintas libres de halógeno",
                ],
                "default": "Conduit Rígido PVC 20mm (RIC N°04)",
            },
            {
                "id": "tipo_conductor",
                "label": "Tipo de Conductor / Cableado:",
                "tipo": "select",
                "opciones": [
                    "Cable EVA / H07Z1-K 2.5 mm² (Libre de Halógenos)",
                    "Cable NYA 2.5 mm²",
                    "Cable Libre de Halógenos 1.5 mm² (Alumbrado)",
                ],
                "default": "Cable EVA / H07Z1-K 2.5 mm² (Libre de Halógenos)",
            },
        ],
    },
    "Pisos / Revestimientos": {
        "categoria": "Terminaciones de Piso",
        "unidad_medida": "m²",
        "preguntas": [
            {
                "id": "largo_piso",
                "label": "Largo de Piso (m):",
                "tipo": "number",
                "default": 2.0,
                "step": 0.1,
            },
            {
                "id": "ancho_piso",
                "label": "Ancho de Piso (m):",
                "tipo": "number",
                "default": 1.8,
                "step": 0.1,
            },
            {
                "id": "tipo_revestimiento",
                "label": "Tipo de Revestimiento de Piso:",
                "tipo": "select",
                "opciones": [
                    "Cerámica Antideslizante 33x33 / 45x45 cm",
                    "Porcelanato 60x60 cm Zonas Húmedas",
                    "Piso Vinílico SPC 4mm Impresionable",
                ],
                "default": "Cerámica Antideslizante 33x33 / 45x45 cm",
            },
            {
                "id": "tipo_adhesivo",
                "label": "Adhesivo / Bekron:",
                "tipo": "select",
                "opciones": [
                    "Bekron AC (Pasta Alta Adherencia Zonas Húmedas)",
                    "Bekron Standard (Polvo)",
                    "Bekron DA (Porcelanatos)",
                ],
                "default": "Bekron AC (Pasta Alta Adherencia Zonas Húmedas)",
            },
        ],
    },
    "Cielo Falso / Aislación": {
        "categoria": "Cielos y Cubiertas",
        "unidad_medida": "m²",
        "preguntas": [
            {
                "id": "largo_cielo",
                "label": "Largo de Cielo (m):",
                "tipo": "number",
                "default": 2.0,
                "step": 0.1,
            },
            {
                "id": "ancho_cielo",
                "label": "Ancho de Cielo (m):",
                "tipo": "number",
                "default": 1.8,
                "step": 0.1,
            },
            {
                "id": "tipo_placa_cielo",
                "label": "Placa de Cielo Falso:",
                "tipo": "select",
                "opciones": [
                    "Volcanita RH 12.5mm (Zonas Húmedas)",
                    "Volcanita ST 10mm",
                    "Cielo Americano Modular 60x60",
                ],
                "default": "Volcanita RH 12.5mm (Zonas Húmedas)",
            },
            {
                "id": "aislacion_cielo",
                "label": "Aislación sobre Cielo:",
                "tipo": "select",
                "opciones": [
                    "Lana de Vidrio Rollo 80mm",
                    "Lana Mineral 50mm",
                    "Sin Aislación Extra",
                ],
                "default": "Lana de Vidrio Rollo 80mm",
            },
        ],
    },
}


def render_formulario_dinamico(elemento_seleccionado):
  """Renderiza dinámicamente en Streamlit las preguntas específicas para el elemento constructivo."""
  config = BIBLIOTECA_TECNICA.get(
      elemento_seleccionado, BIBLIOTECA_TECNICA["Instalación Eléctrica General"]
  )
  respuestas = {}

  st.markdown(
      f"#### ⚙️ Parámetros Técnicos: **{config['categoria']}**"
  )

  for q in config["preguntas"]:
    q_id = q["id"]
    q_label = q["label"]
    q_tipo = q["tipo"]

    if q_tipo == "number":
      respuestas[q_id] = st.number_input(
          label=q_label,
          min_value=0.0 if isinstance(q["default"], float) else 0,
          value=q["default"],
          step=q.get("step", 1),
          help=q.get("help", ""),
          key=f"dyn_{q_id}",
      )
    elif q_tipo == "select":
      respuestas[q_id] = st.selectbox(
          label=q_label,
          options=q["opciones"],
          index=q["opciones"].index(q["default"])
          if q["default"] in q["opciones"]
          else 0,
          help=q.get("help", ""),
          key=f"dyn_{q_id}",
      )
    elif q_tipo == "text":
      respuestas[q_id] = st.text_input(
          label=q_label,
          value=q.get("default", ""),
          help=q.get("help", ""),
          key=f"dyn_{q_id}",
      )

  return respuestas


def calcular_materiales_partida(elemento_seleccionado, respuestas):
  """Motor de Cubicación Paramétrico: Transforma las respuestas técnicas

  en una lista detallada de insumos, cantidades, mermas y unidades.
  """
  materiales = []

  # --------------------------------------------------------------------------
  # 1. TABIQUERÍA Y MUROS
  # --------------------------------------------------------------------------
  if elemento_seleccionado == "Tabiquería / Muros":
    largo = float(respuestas.get("largo", 0.0))
    alto = float(respuestas.get("alto", 0.0))
    area_m2 = round(largo * alto, 2)
    perimetro_m = (largo * 2) + (alto * 2)

    sep_cm = 40 if "40" in str(respuestas.get("separacion_montantes")) else 60
    distancia_m = sep_cm / 100.0

    # Soleras (Superior e Inferior)
    ml_soleras = largo * 2
    tiras_soleras = math.ceil((ml_soleras * 1.05) / 3.0)  # Tiras de 3m, 5% merma

    # Montantes
    num_montantes = math.ceil(largo / distancia_m) + 1
    tiras_montantes = math.ceil(
        (num_montantes * alto * 1.08) / 3.0
    )  # 8% merma

    # Placas Volcanita (2 caras de revestimiento)
    area_placas_total = area_m2 * 2
    planchas_volcanita = math.ceil(
        (area_placas_total * 1.10) / 2.88
    )  # Planca 1.2x2.4=2.88m², 10% merma

    # Tornillos
    tornillos_framing = math.ceil(area_m2 * 15)  # Cabeza lenteja p/estructura
    tornillos_volcanita = math.ceil(
        area_placas_total * 30
    )  # Cabeza trompeta 1 5/8"

    # Insumos varios
    rollos_lana = math.ceil((area_m2 * 1.05) / 10.0)  # Rollo de 10m² aprox.
    cinta_junta = round(area_m2 * 1.8, 1)  # Metros de cinta
    masilla_kg = round(area_m2 * 1.2, 1)  # kg de masilla de junta

    materiales = [
        {
            "insumo": "Soleras Cintas Galvanizadas 60CA08 (3m)",
            "cantidad": tiras_soleras,
            "unidad": "tiras",
        },
        {
            "insumo": "Montantes Galvanizados 60CA08 (3m)",
            "cantidad": tiras_montantes,
            "unidad": "tiras",
        },
        {
            "insumo": f"Placas {respuestas.get('tipo_placa')} (1.20x2.40m)",
            "cantidad": planchas_volcanita,
            "unidad": "planchas",
        },
        {
            "insumo": "Tornillos Metalcom Cabeza Lenteja #8x1/2",
            "cantidad": tornillos_framing,
            "unidad": "unidades",
        },
        {
            "insumo": "Tornillos Volcanita Cabeza Trompeta 6x1-5/8",
            "cantidad": tornillos_volcanita,
            "unidad": "unidades",
        },
        {
            "insumo": f"Aislación {respuestas.get('aislacion')}",
            "cantidad": rollos_lana,
            "unidad": "rollos/paquetes",
        },
        {
            "insumo": "Cinta de Fibra de Vidrio / Papel para Juntas",
            "cantidad": cinta_junta,
            "unidad": "ml",
        },
        {
            "insumo": "Masilla Junta Invisible / Pasta Muro",
            "cantidad": masilla_kg,
            "unidad": "kg",
        },
    ]

    if "Membrana" in str(respuestas.get("impermeabilizacion")):
      materiales.append({
          "insumo": "Impermeabilizante Elástico Membrana Acrílica Zócalo (5kg)",
          "cantidad": math.ceil(area_m2 / 4.0),
          "unidad": "tineta(s)",
      })

  # --------------------------------------------------------------------------
  # 2. INSTALACIÓN ELÉCTRICA
  # --------------------------------------------------------------------------
  elif "Eléctrica" in elemento_seleccionado:
    enchufes = int(respuestas.get("num_enchufes", 0))
    centros = int(respuestas.get("num_centros", 0))
    interruptores = int(respuestas.get("num_interruptores", 0))

    tot_puntos = enchufes + centros + interruptores
    tiras_conduit = math.ceil((tot_puntos * 4.0) / 3.0)  # 4m de canaliz/punto
    rollos_cable = math.ceil(
        (tot_puntos * 12.0) / 100.0
    )  # 12m cable/punto en rollos de 100m

    materiales = [
        {
            "insumo": "Cajas de Embutiles Aislantes Condulet/Octogonales",
            "cantidad": tot_puntos,
            "unidad": "unidades",
        },
        {
            "insumo": f"Tubería {respuestas.get('tipo_canalizacion')} (3m)",
            "cantidad": tiras_conduit,
            "unidad": "tiras",
        },
        {
            "insumo": f"Conductor {respuestas.get('tipo_conductor')}",
            "cantidad": rollos_cable,
            "unidad": "rollo(s) 100m",
        },
        {
            "insumo": "Módulos Enchufe Monofásico Doble 10A/16A + Placa",
            "cantidad": enchufes,
            "unidad": "juegos",
        },
        {
            "insumo": "Interruptores Embutidos + Placa",
            "cantidad": interruptores,
            "unidad": "juegos",
        },
        {
            "insumo": "Soquetes / Portalámparas + Cajas de Centro",
            "cantidad": centros,
            "unidad": "unidades",
        },
    ]

  # --------------------------------------------------------------------------
  # 3. PISOS Y REVESTIMIENTOS
  # --------------------------------------------------------------------------
  elif elemento_seleccionado == "Pisos / Revestimientos":
    largo = float(respuestas.get("largo_piso", 0.0))
    ancho = float(respuestas.get("ancho_piso", 0.0))
    area_m2 = round(largo * ancho, 2)

    cajas_ceramica = math.ceil(
        (area_m2 * 1.12) / 1.5
    )  # 12% merma, 1.5m² por caja
    sacos_bekron = math.ceil(area_m2 / 4.0)  # 1 saco 25kg rinde ~4m²
    kg_fragüe = round(area_m2 * 0.5, 1)

    materiales = [
        {
            "insumo": f"Palmetas {respuestas.get('tipo_revestimiento')}",
            "cantidad": cajas_ceramica,
            "unidad": "cajas (~1.5m² c/u)",
        },
        {
            "insumo": f"Adhesivo {respuestas.get('tipo_adhesivo')} (25kg)",
            "cantidad": sacos_bekron,
            "unidad": "sacos/tinetas",
        },
        {
            "insumo": "Fragüe Impresionable para Juntas Zonas Húmedas",
            "cantidad": kg_fragüe,
            "unidad": "kg",
        },
        {
            "insumo": "Crucetas Separadoras Plásticas 2mm / 3mm",
            "cantidad": 1,
            "unidad": "bolsa(100un)",
        },
    ]

  # --------------------------------------------------------------------------
  # 4. CIELOS
  # --------------------------------------------------------------------------
  elif elemento_seleccionado == "Cielo Falso / Aislación":
    largo = float(respuestas.get("largo_cielo", 0.0))
    ancho = float(respuestas.get("ancho_cielo", 0.0))
    area_m2 = round(largo * ancho, 2)

    planchas = math.ceil((area_m2 * 1.10) / 2.88)
    rollos_lana = math.ceil((area_m2 * 1.05) / 10.0)

    materiales = [
        {
            "insumo": f"Placas {respuestas.get('tipo_placa_cielo')} (1.2x2.4m)",
            "cantidad": planchas,
            "unidad": "planchas",
        },
        {
            "insumo": f"Aislación {respuestas.get('aislacion_cielo')}",
            "cantidad": rollos_lana,
            "unidad": "rollos",
        },
        {
            "insumo": "Perfiles Omega / Portantes Galvanizados Cielos (3m)",
            "cantidad": math.ceil((area_m2 * 1.5) / 3.0),
            "unidad": "tiras",
        },
    ]

  return materiales
