import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ECOLUZ - Cerebro Inspector Técnico", layout="wide"
)

st.title("🏗️ ECOLUZ - Cerebro Inspector Técnico & Listado de Ejecución")
st.markdown(
    "Levantamiento, Configuración Técnica por Especialidad, Cubicaciones,"
    " Especificaciones Técnicas (E.T.) y Presupuesto Comercial"
)

# ----------------- FUNCIONES AUXILIARES DE EXPORTACIÓN -----------------
def generar_excel_presupuesto(df_items, c_directo, gg_util, subtotal, iva, total):
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    # Hoja 1: Desglose de Partidas
    df_items.to_excel(writer, index=False, sheet_name="Detalle_Partidas")

    # Hoja 2: Resumen Financiero
    df_resumen = pd.DataFrame({
        "Concepto": [
            "Costo Directo Total",
            "Gastos Generales y Utilidad (25%)",
            "Subtotal Neto",
            "IVA (19%)",
            "TOTAL PRESUPUESTO",
        ],
        "Monto ($ CLP)": [c_directo, gg_util, subtotal, iva, total],
    })
    df_resumen.to_excel(writer, index=False, sheet_name="Resumen_Económico")

  return output.getvalue()


# ----------------- MENÚ LATERAL -----------------
st.sidebar.title("📋 Módulo de Trabajo")
modulo = st.sidebar.radio(
    "Seleccione Fase:",
    [
        "1. Configuración Técnica y Cubicaciones",
        "2. Registro Fotográfico y Planos",
        "3. Especificaciones Técnicas Detalladas (E.T.)",
        "4. Análisis de Precios Unitarios (APU)",
        "5. Cierre Económico y Presupuesto",
    ],
)

if "partidas_recintos" not in st.session_state:
  st.session_state["partidas_recintos"] = {}

if "detalles_tecnicos" not in st.session_state:
  st.session_state["detalles_tecnicos"] = {}

lista_recintos_especialidades = [
    "⚡ Electricidad",
    "🎨 Pintura",
    "🪵 Carpintería",
    "🧱 Revestimientos",
    "📐 Terminaciones",
    "🌿 Paisajismo",
    "🔋 Generadores y Equipos",
    "🚿 Baño Principal / Zonas Húmedas",
    "🍳 Cocina / Logia",
    "🛋️ Estar-Comedor / General",
]

# ----------------- MÓDULO 1 -----------------
if modulo == "1. Configuración Técnica y Cubicaciones":
  st.subheader(
      "📐 Módulo 1: Preguntas Técnicas Específicas por Especialidad y Desglose"
  )

  recinto_actual = st.selectbox(
      "Seleccionar Especialidad o Recinto a Cotizar",
      lista_recintos_especialidades,
  )

  col1, col2 = st.columns(2)
  with col1:
    largo = st.number_input(
        "Largo / Frente (m)", value=4.00, step=0.10, key="l_m1"
    )
    ancho = st.number_input(
        "Ancho / Profundidad (m)", value=3.00, step=0.10, key="a_m1"
    )
  with col2:
    alto = st.number_input(
        "Alto / Elevación (m)", value=2.40, step=0.10, key="h_m1"
    )

  area_piso = largo * ancho
  perimetro = 2 * (largo + ancho)
  area_muros = perimetro * alto

  st.info(
      f"📏 **Métricas Base:** Área Superficie: `{area_piso:.2f} m²` | Perímetro"
      f" Línea Base: `{perimetro:.2f} m` | Área Muros Bruta: `{area_muros:.2f} m²`"
  )

  st.markdown("---")
  st.markdown(f"### ⚙️ Cuestionario Técnico Específico: **{recinto_actual}**")

  nuevos_items = []
  datos_et = {}

  # ==========================================
  # ⚡ 1. ELECTRICIDAD
  # ==========================================
  if "Electricidad" in recinto_actual:
    with st.expander(
        "🔌 Parámetros de la Instalación Eléctrica", expanded=True
    ):
      c_empalme = st.selectbox(
          "Tipo de Empalme / Suministro:",
          [
              "Monofásico 220V (Aéreo)",
              "Monofásico 220V (Subterráneo)",
              "Trifásico 380V (Aéreo)",
              "Trifásico 380V (Subterráneo)",
          ],
      )
      c_cable = st.selectbox(
          "Tipo de Conductor / Cableado:",
          [
              "EVA Libre de Halógeno (1.5mm² alumbrado / 2.5mm² enchufes)",
              "THHN / THWN (Cu)",
              "NYA Roscado / Alumbrado Básico",
          ],
      )
      c_tubo = st.selectbox(
          "Canalización / Tuberías:",
          [
              "Tubo Conduit PVC Rígido Heavy Duty",
              "Tubo Metálico EMT / Galvanizado",
              "Canaleta PVC Legrand sobremuro",
          ],
      )
      c_tablero = st.selectbox(
          "Tablero Eléctrico y Protecciones:",
          [
              (
                  "Tablero Sobremuro 8 Polos + Diferencial + Automáticos"
                  " 10A/16A"
              ),
              (
                  "Tablero Embutido 12 Polos + Diferencial + Automáticos"
                  " 10A/16A/25A"
              ),
              "Tablero Trifásico Comercial Industrial",
          ],
      )
      c_puntos = st.number_input(
          "Cantidad Total de Puntos (Centros / Enchufes / Interruptores):",
          value=8,
          step=1,
      )

    datos_et = {
        "Empalme": c_empalme,
        "Cableado": c_cable,
        "Canalización": c_tubo,
        "Tablero": c_tablero,
        "Puntos": c_puntos,
        "Normativa": "Pliegos Técnicos Normativos RIC N°01 a N°19 (SEC Chile)",
    }

    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      nuevos_items = [
          {
              "Partida": f"Conductor Eléctrico {c_cable} (rollo 100m)",
              "Cantidad": max(1.0, round(c_puntos / 4.0, 1)),
              "Precio Unit.": 38000.0,
          },
          {
              "Partida": f"Canalización {c_tubo} (tira 3m)",
              "Cantidad": max(2.0, round(c_puntos * 1.5, 0)),
              "Precio Unit.": 3800.0,
          },
          {
              "Partida": (
                  "Cajas de Derivación / Conexión + Coplas y Curvas (gl)"
              ),
              "Cantidad": 1.0,
              "Precio Unit.": 18500.0,
          },
          {
              "Partida": (
                  "Módulos Enchufes e Interruptores Dobles / Placas (unidad)"
              ),
              "Cantidad": float(c_puntos),
              "Precio Unit.": 4500.0,
          },
          {
              "Partida": f"{c_tablero} (kit completo)",
              "Cantidad": 1.0,
              "Precio Unit.": 68000.0,
          },
          {
              "Partida": (
                  "Accesorios de Fijación (Abrazaderas, Cintas, Terminales) (gl)"
              ),
              "Cantidad": 1.0,
              "Precio Unit.": 12500.0,
          },
      ]

  # ==========================================
  # 🎨 2. PINTURA
  # ==========================================
  elif "Pintura" in recinto_actual:
    with st.expander(
        "🖌️ Parámetros de Pintura y Preparación de Superficie", expanded=True
    ):
      p_tipo = st.selectbox(
          "Tipo de Pintura Principal:",
          [
              "Esmalte al Agua Antihongo (Semibrillo / Mate)",
              "Óleo Opaco Sintético",
              "Óleo Brillante",
              "Látex Extra Cubriente interior",
          ],
      )
      p_estado = st.selectbox(
          "Estado de la Superficie / Preparación:",
          [
              "Superficie Nueva (Volcanita / Yeso limpio)",
              "Superficie Existente con Grietas / Requiere Empaste Completo",
              (
                  "Estuco Vivo / Hormigón (Requiere Sellador Acrílico"
                  " neutralizador)"
              ),
          ],
      )
      p_manos = st.selectbox(
          "Número de Manos de Aplicación:",
          [
              "2 Manos directas",
              "1 Mano Imprimante + 2 Manos Terminación",
              "3 Manos para cambio fuerte de color",
          ],
      )
      p_diluyente = (
          "Agua Limpia"
          if "Agua" in p_tipo or "Látex" in p_tipo
          else "Aguarrás Mineral / Diluyente Sintético"
      )

    datos_et = {
        "Pintura": p_tipo,
        "Preparación": p_estado,
        "Manos": p_manos,
        "Diluyente": p_diluyente,
        "Normativa": "NCh 331 - Pinturas y Barnices / Especificaciones Manuales de Fabricante",
    }

    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      cant_sup = area_muros + area_piso
      nuevos_items = [
          {
              "Partida": f"Pintura {p_tipo} (tineta 4g / galones)",
              "Cantidad": max(1.0, round(cant_sup / 35.0, 1)),
              "Precio Unit.": 44000.0,
          },
          {
              "Partida": (
                  f"Imprimante / Sellador de Fijación ({p_diluyente}) (galón)"
              ),
              "Cantidad": max(1.0, round(cant_sup / 45.0, 1)),
              "Precio Unit.": 24000.0,
          },
          {
              "Partida": (
                  f"Empaste Muros / Pasta Muro ({p_estado}) (saco/tarro)"
              ),
              "Cantidad": max(1.0, round(cant_sup / 20.0, 1)),
              "Precio Unit.": 13500.0,
          },
          {
              "Partida": f"Diluyente / Insumo Limpieza ({p_diluyente}) (litros)",
              "Cantidad": 2.0 if "Aguarrás" in p_diluyente else 0.0,
              "Precio Unit.": 4500.0,
          },
          {
              "Partida": (
                  "Kit Lijas de Muro, Cinta Masking, Plástico Protector (gl)"
              ),
              "Cantidad": 1.0,
              "Precio Unit.": 16000.0,
          },
          {
              "Partida": "Rodillos Antigota, Brochas y Extensor Telescópico (gl)",
              "Cantidad": 1.0,
              "Precio Unit.": 15000.0,
          },
      ]

  # ==========================================
  # 🪵 3. CARPINTERÍA
  # ==========================================
  elif "Carpintería" in recinto_actual:
    with st.expander(
        "🪵 Parámetros de Estructura y Carpintería", expanded=True
    ):
      car_madera = st.selectbox(
          "Tipo y Calidad de Madera / Estructura:",
          [
              "Pino Radiata Calibrado Seco en Cámara",
              "Pino Oregón 2x3 / 2x4",
              "MDF Prepintado / Terciado Estructural",
              "Madera Nativa / Roble",
          ],
      )
      car_fijaciones = st.selectbox(
          "Tipo de Fijaciones y Ensambles:",
          [
              "Tornillos Spax / CRS Cincados + Tarugos",
              "Clavos Estructurales de Impacto + Perno Anclaje",
              "Adhesivo Montaje Profesional + Escuadras Metálicas",
          ],
      )
      car_acabado = st.selectbox(
          "Protección / Acabado Final:",
          [
              "Protector Lasure / Impregnante Antimanchas",
              "Barniz Marino de Alto Brillo",
              "Sello Primario / Oleo Base",
              "Sin Tratamiento (Obra Gruesa)",
          ],
      )

    datos_et = {
        "Madera": car_madera,
        "Fijaciones": car_fijaciones,
        "Acabado": car_acabado,
        "Normativa": "NCh 1198 (Cálculo de Estructuras en Madera) y NCh 1989",
    }

    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      nuevos_items = [
          {
              "Partida": f"Estructura Madera {car_madera} (m² / ml)",
              "Cantidad": round(area_muros, 2),
              "Precio Unit.": 13500.0,
          },
          {
              "Partida": f"Fijaciones y Ensambles {car_fijaciones} (caja/pack)",
              "Cantidad": 2.0,
              "Precio Unit.": 8500.0,
          },
          {
              "Partida": "Adhesivo de Carpintería / Cola Fría Madera HD (kg)",
              "Cantidad": 1.0,
              "Precio Unit.": 6200.0,
          },
          {
              "Partida": f"Protector / Acabado {car_acabado} (galón)",
              "Cantidad": max(1.0, round(area_muros / 25.0, 1)),
              "Precio Unit.": 26000.0,
          },
          {
              "Partida": (
                  "Consumibles Carpintería (Brocas, Hojas Sierra, Lijas) (gl)"
              ),
              "Cantidad": 1.0,
              "Precio Unit.": 12000.0,
          },
      ]

  # ==========================================
  # 🧱 4. REVESTIMIENTOS
  # ==========================================
  elif "Revestimientos" in recinto_actual:
    with st.expander("🧱 Parámetros de Revestimiento", expanded=True):
      rev_tipo = st.selectbox(
          "Tipo de Revestimiento:",
          [
              "Cerámico Muro 30x60",
              "Porcelanato Piso/Muro 60x60",
              "Siding Fibrocemento / PVC",
              "Paletas WPC / Compuesto Madera-Plástico",
          ],
      )
      rev_pegamento = st.selectbox(
          "Tipo de Adhesivo:",
          [
              "Bekron AC (Cerámico Estándar)",
              "Bekron ACI (Sustrato Rígido/Exterior)",
              "Bekron Flex (Porcelanato/Zona Húmeda)",
              "Mortero / Adhesivo Montaje",
          ],
      )
      rev_junta = st.selectbox(
          "Fragüe / Terminación de Junta:",
          [
              "Fragüe Flexible Antihongo",
              "Fragüe Epóxico Industrial",
              "Sellador Poliuretano",
          ],
      )

    datos_et = {
        "Revestimiento": rev_tipo,
        "Adhesivo": rev_pegamento,
        "Junta": rev_junta,
        "Normativa": "NCh 353 (Cubicación de Obras) y Manuales Técnicos Bekron / Weber",
    }

    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      cant_r = area_muros
      nuevos_items = [
          {
              "Partida": f"Revestimiento {rev_tipo} (m²)",
              "Cantidad": round(cant_r * 1.08, 2),
              "Precio Unit.": 24000.0,
          },
          {
              "Partida": f"Adhesivo {rev_pegamento} (saco 25kg)",
              "Cantidad": max(1.0, round(cant_r / 3.8, 1)),
              "Precio Unit.": 10500.0,
          },
          {
              "Partida": f"{rev_junta} (kg)",
              "Cantidad": max(1.0, round(cant_r * 0.35, 1)),
              "Precio Unit.": 4800.0,
          },
          {
              "Partida": "Sistema Niveladores, Cuñas y Crucetas (kit)",
              "Cantidad": max(1.0, round(cant_r / 8.0, 1)),
              "Precio Unit.": 8500.0,
          },
          {
              "Partida": (
                  "Perfiles Esquinero PVC / Alum. + Silicona Sanitaria (gl)"
              ),
              "Cantidad": 1.0,
              "Precio Unit.": 12000.0,
          },
      ]

  # ==========================================
  # 📐 5. TERMINACIONES
  # ==========================================
  elif "Terminaciones" in recinto_actual:
    with st.expander("📐 Parámetros de Terminaciones Finas", expanded=True):
      ter_elementos = st.multiselect(
          "Elementos a Considerar:",
          [
              "Guardapolvos",
              "Junquillos",
              "Cornisas",
              "Tapajuntas",
              "Burletes de Puerta",
          ],
          default=["Guardapolvos", "Junquillos"],
      )
      ter_material = st.selectbox(
          "Materialidad de Terminaciones:",
          [
              "MDF Prepintado Blanco",
              "Madera Nativa Finger Joint",
              "PVC Resistente al Agua",
          ],
      )
      ter_fijacion = st.selectbox(
          "Método de Fijación:",
          [
              "Adhesivo Montaje Clavo Líquido + Clavo de Impacto",
              "Tornillos Fijos con Tapita",
              "Silicona Neutra",
          ],
      )

    datos_et = {
        "Elementos": ", ".join(ter_elementos),
        "Material": ter_material,
        "Fijación": ter_fijacion,
        "Normativa": "Especificaciones de Arquitectura y Tolerancias NCh 353",
    }

    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      cant_l = perimetro
      nuevos_items = [
          {
              "Partida": (
                  f"Terminación {ter_material} ({', '.join(ter_elementos)}) (ml)"
              ),
              "Cantidad": round(cant_l, 2),
              "Precio Unit.": 4500.0,
          },
          {
              "Partida": f"Fijación {ter_fijacion} + Clavo Líquido (cartuchos)",
              "Cantidad": max(2.0, round(cant_l / 7.0, 1)),
              "Precio Unit.": 6500.0,
          },
          {
              "Partida": "Masilla Retoque, Esquinas y Silicona Terminación (gl)",
              "Cantidad": 1.0,
              "Precio Unit.": 8900.0,
          },
      ]

  # ==========================================
  # 🌿 6. PAISAJISMO
  # ==========================================
  elif "Paisajismo" in recinto_actual:
    with st.expander(
        "🌿 Parámetros de Paisajismo y Obras Exteriores", expanded=True
    ):
      pai_cobertera = st.selectbox(
          "Tipo de Cobertera Vegetal / Decorativa:",
          [
              "Pasto en Palmetas (Tepe) Alto Tráfico",
              "Siembra de Césped",
              "Gravilla Decorativa / Chip de Madera",
          ],
      )
      pai_riego = st.selectbox(
          "Sistema de Riego:",
          [
              "Riego Automático por Aspersión / Goteo con Programador",
              "Riego Manual por Llave de Jardín",
              "Sin Riego",
          ],
      )
      pai_tierra = st.selectbox(
          "Acondicionamiento de Terreno:",
          [
              "Tierra Vegetal Cernida + Compost (10cm espesor)",
              "Nivelación Simple con Rodillo",
          ],
      )

    datos_et = {
        "Cobertera": pai_cobertera,
        "Riego": pai_riego,
        "Terreno": pai_tierra,
        "Normativa": "Especificaciones de Paisajismo y Conservación de Suelos",
    }

    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      cant_j = area_piso
      nuevos_items = [
          {
              "Partida": f"Tierra Vegetal / Substrato ({pai_tierra}) (m³)",
              "Cantidad": max(1.0, round(cant_j * 0.1, 1)),
              "Precio Unit.": 28000.0,
          },
          {
              "Partida": f"Cobertera {pai_cobertera} (m²)",
              "Cantidad": round(cant_j * 1.05, 2),
              "Precio Unit.": 6800.0,
          },
          {
              "Partida": f"{pai_riego} (kit materiales/tuberías)",
              "Cantidad": 1.0,
              "Precio Unit.": 75000.0,
          },
          {
              "Partida": "Solerillas / Delimitadores de Jardín (ml)",
              "Cantidad": round(perimetro, 2),
              "Precio Unit.": 4200.0,
          },
      ]

  # ==========================================
  # 🔋 7. GENERADORES Y EQUIPOS
  # ==========================================
  elif "Generadores" in recinto_actual:
    with st.expander(
        "⚡ Parámetros de Generador y Grupo Electrógeno", expanded=True
    ):
      gen_kva = st.selectbox(
          "Potencia Nominal del Equipo:",
          [
              "5 kVA (Monofásico)",
              "8 kVA (Monofásico)",
              "12 kVA (Trifásico)",
              "20 kVA (Trifásico Industrial)",
          ],
      )
      gen_tta = st.selectbox(
          "Sistema de Transferencia:",
          [
              "Tablero de Transferencia Automática (TTA)",
              "Conmutador Manual de Red/Generador",
          ],
      )
      gen_tipo = st.selectbox(
          "Tipo de Gabinete / Insonorización:",
          ["Insonorizado Silent Cabin", "Gabinete Abierto sobre Chasis"],
      )

    datos_et = {
        "Potencia": gen_kva,
        "Transferencia": gen_tta,
        "Gabinete": gen_tipo,
        "Normativa": (
            "RIC N°08 (Sistemas de Respaldo) / SEC y Normas Ambientales de"
            " Ruido"
        ),
    }

    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      nuevos_items = [
          {
              "Partida": f"Grupo Electrógeno {gen_kva} ({gen_tipo}) (unidad)",
              "Cantidad": 1.0,
              "Precio Unit.": 1250000.0,
          },
          {
              "Partida": f"{gen_tta} (unidad)",
              "Cantidad": 1.0,
              "Precio Unit.": 380000.0,
          },
          {
              "Partida": "Alimentadores Principales de Fuerza y Control (m)",
              "Cantidad": 15.0,
              "Precio Unit.": 8500.0,
          },
          {
              "Partida": (
                  "Kit Puesta a Tierra Dedicada (Barra Cooperweld, Conector, Gel)"
              ),
              "Cantidad": 1.0,
              "Precio Unit.": 65000.0,
          },
          {
              "Partida": (
                  "Protecciones Eléctricas Adicionales e Insumos Montaje (gl)"
              ),
              "Cantidad": 1.0,
              "Precio Unit.": 4500.0,
          },
      ]

  # ==========================================
  # 🚿 OTROS RECINTOS
  # ==========================================
  else:
    st.write(
        "Recinto general. Se cargará el kit estándar de Tabiquería y"
        " Terminación."
    )
    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      nuevos_items = [
          {
              "Partida": "Estructura Metalcom C90x0.85 (m²)",
              "Cantidad": round(area_muros, 2),
              "Precio Unit.": 14200.0,
          },
          {
              "Partida": "Placa Volcanita RH 12.5mm (m²)",
              "Cantidad": round(area_muros, 2),
              "Precio Unit.": 9800.0,
          },
          {
              "Partida": "Fijaciones, Masilla, Cinta y Consumibles (gl)",
              "Cantidad": 1.0,
              "Precio Unit.": 22000.0,
          },
      ]

  # GUARDAR DATOS SI SE GENERARON
  if nuevos_items:
    st.session_state["partidas_recintos"][recinto_actual] = nuevos_items
    st.session_state["detalles_tecnicos"][recinto_actual] = datos_et
    st.success(
        f"✅ ¡Kit de materiales y parámetros técnicos de **{recinto_actual}**"
        " guardados correctamente!"
    )

  st.markdown("---")
  st.markdown(
      f"### ✏️ Gestor Interactiva de Partidas: **{recinto_actual}** (Edita"
      " Cantidades o Precios)"
  )
  if (
      recinto_actual in st.session_state["partidas_recintos"]
      and st.session_state["partidas_recintos"][recinto_actual]
  ):
    df_actual = pd.DataFrame(
        st.session_state["partidas_recintos"][recinto_actual]
    )

    # TABLA EDITABLE CON DATA_EDITOR
    df_editado = st.data_editor(
        df_actual,
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_{recinto_actual}",
    )

    # ACTUALIZAR SESSION STATE CON CAMBIOS EN TIEMPO REAL
    st.session_state["partidas_recintos"][recinto_actual] = df_editado.to_dict(
        "records"
    )
  else:
    st.info("Aún no se han configurado ítems para esta especialidad.")

# ----------------- MÓDULO 2 -----------------
elif modulo == "2. Registro Fotográfico y Planos":
  st.subheader("📸 Módulo 2: Registro Fotográfico y Inspección")
  recinto_m2 = st.selectbox(
      "Seleccionar Recinto a Inspeccionar", lista_recintos_especialidades
  )
  st.file_uploader("Subir Plano / Esquema Técnico", type=["png", "jpg", "pdf"])
  st.file_uploader(
      "Subir Fotografías de Avance", type=["png", "jpg"], accept_multiple_files=True
  )

# ----------------- MÓDULO 3 -----------------
elif modulo == "3. Especificaciones Técnicas Detalladas (E.T.)":
  st.subheader("📄 ESPECIFICACIONES TÉCNICAS DINÁMICAS Y DETALLADAS (E.T.)")
  st.markdown("---")
  st.markdown("### 🏛️ PROYECTO: ESPECIALIDADES ECOLUZ SpA")
  st.markdown("**Constructor Responsable:** Constructor Civil - Concepción, Chile")
  st.markdown("---")

  if st.session_state["partidas_recintos"]:
    texto_et_exportar = ""
    for recinto, items in st.session_state["partidas_recintos"].items():
      if items:
        st.markdown(f"### 📌 ESPECIALIDAD / SECTOR: {recinto}")
        texto_et_exportar += f"ESPECIALIDAD / SECTOR: {recinto}\n"

        # MOSTRAR CUESTIONARIO TÉCNICO RESPONDIDO
        if (
            recinto in st.session_state["detalles_tecnicos"]
            and st.session_state["detalles_tecnicos"][recinto]
        ):
          st.markdown("  **Parámetros Específicos & Normativa:**")
          for k, v in st.session_state["detalles_tecnicos"][recinto].items():
            st.markdown(f"  - **{k}:** `{v}`")
            texto_et_exportar += f"- {k}: {v}\n"
          st.markdown("")

        st.markdown("  **Desglose de Materiales e Insumos:**")
        for idx, item in enumerate(items, 1):
          st.markdown(f"  **{idx}. {item['Partida']}**")
          st.markdown(
              "     - *Especificación:* Suministro, montaje e instalación de"
              f" {item['Partida']} según especificaciones y normativa"
              " chilena."
          )
          st.markdown(f"     - *Cantidad Requerida:* `{item['Cantidad']}`")
          texto_et_exportar += (
              f"  {idx}. {item['Partida']} - Cantidad: {item['Cantidad']}\n"
          )
        st.markdown("---")

    st.download_button(
        label="📥 Descargar Especificaciones Técnicas (.txt)",
        data=texto_et_exportar,
        file_name="Especificaciones_Tecnicas_ECOLUZ.txt",
        mime="text/plain",
    )
  else:
    st.warning(
        "⚠️ No hay partidas configuradas. Vuelve al Módulo 1 para responder las"
        " preguntas técnicas."
    )

# ----------------- MÓDULO 4 -----------------
elif modulo == "4. Análisis de Precios Unitarios (APU)":
  st.subheader("💰 Módulo 4: Consolidado y Análisis Financiero")
  todos = []
  for rec, items in st.session_state["partidas_recintos"].items():
    for item in items:
      f = dict(item).copy()
      f["Especialidad / Recinto"] = rec
      f["Costo Total"] = float(f["Cantidad"]) * float(f["Precio Unit."])
      todos.append(f)

  if todos:
    df_t = pd.DataFrame(todos)
    st.dataframe(
        df_t[[
            "Especialidad / Recinto",
            "Partida",
            "Cantidad",
            "Precio Unit.",
            "Costo Total",
        ]],
        use_container_width=True,
    )
    c_directo = df_t["Costo Total"].sum()
    st.markdown(f"### 💵 Costo Directo Total: 💲 `{c_directo:,.0f}`")
  else:
    st.info("Sin partidas cargadas.")

# ----------------- MÓDULO 5 -----------------
elif modulo == "5. Cierre Económico y Presupuesto":
  st.subheader("📊 Módulo 5: Propuesta Comercial Final")
  todos = []
  for rec, items in st.session_state["partidas_recintos"].items():
    for item in items:
      f = dict(item).copy()
      f["Especialidad / Recinto"] = rec
      f["Costo Total"] = float(f["Cantidad"]) * float(f["Precio Unit."])
      todos.append(f)

  if todos:
    df_cot = pd.DataFrame(todos)
    df_cliente = df_cot[[
        "Especialidad / Recinto",
        "Partida",
        "Cantidad",
        "Precio Unit.",
        "Costo Total",
    ]].copy()
    df_cliente.columns = [
        "Especialidad / Recinto",
        "Material / Insumo",
        "Cantidad",
        "Precio Unit. ($)",
        "Total Parcial ($)",
    ]
    st.dataframe(df_cliente, use_container_width=True)

    costo_directo = df_cot["Costo Total"].sum()
    gg_util = costo_directo * 0.25
    subtotal = costo_directo + gg_util
    iva = subtotal * 0.19
    total = subtotal + iva

    st.markdown("---")
    st.markdown(f"- **Costo Directo:** 💲 `{costo_directo:,.0f}`")
    st.markdown(f"- **GG y Utilidad (25%):** 💲 `{gg_util:,.0f}`")
    st.markdown(f"- **Subtotal Neto:** 💲 `{subtotal:,.0f}`")
    st.markdown(f"- **IVA (19%):** 💲 `{iva:,.0f}`")
    st.markdown(f"## 💰 **TOTAL PROPUESTA (CON IVA):** 💲 `{total:,.0f}`")

    # BOTÓN DE DESCARGA A EXCEL
    excel_bytes = generar_excel_presupuesto(
        df_cliente, costo_directo, gg_util, subtotal, iva, total
    )
    st.download_button(
        label="📊 Descargar Presupuesto Comercial en Excel (.xlsx)",
        data=excel_bytes,
        file_name="Presupuesto_Comercial_ECOLUZ.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
  else:
    st.warning("No hay partidas configuradas.")
