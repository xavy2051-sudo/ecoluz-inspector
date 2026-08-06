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
    df_items.to_excel(writer, index=False, sheet_name="Detalle_Partidas")

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
    "🧱 Módulo Completo Metalcom (OSB + Metalsiding + Internit + Cerámicos +"
    " Pintura)",
    "⚡ Electricidad",
    "🎨 Pintura y Cielos",
    "🪵 Carpintería",
    "🧱 Revestimientos Cerámicos y Adhesivos",
    "📐 Terminaciones Finas",
    "🌿 Paisajismo",
    "🔋 Generadores y Equipos",
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
        "Largo / Frente (m)", value=3.70, step=0.10, key="l_m1"
    )
    ancho = st.number_input(
        "Ancho / Profundidad (m)", value=3.70, step=0.10, key="a_m1"
    )
  with col2:
    alto = st.number_input(
        "Alto / Elevación (m)", value=2.40, step=0.10, key="h_m1"
    )

  area_piso = largo * ancho
  perimetro = 2 * (largo + ancho)
  area_muros = perimetro * alto

  st.info(
      f"📏 **Métricas Base:** Área Piso/Cielo: `{area_piso:.2f} m²` | Perímetro"
      f" Línea Base: `{perimetro:.2f} m` | Área Muros Bruta: `{area_muros:.2f} m²`"
  )

  st.markdown("---")
  st.markdown(f"### ⚙️ Cuestionario Técnico Específico: **{recinto_actual}**")

  nuevos_items = []
  datos_et = {}

  # ==========================================
  # 🧱 0. MÓDULO COMPLETO METALCOM MULTICAPA
  # ==========================================
  if "Módulo Completo Metalcom" in recinto_actual:
    with st.expander(
        "🏗️ Parámetros de la Solución Constructiva Multicapa", expanded=True
    ):
      espesor_osb = st.selectbox(
          "Placa Estructural Exterior:",
          ["OSB 11.1 mm", "OSB 9.5 mm", "Terciado Estructural 12 mm"],
      )
      tipo_insul = st.selectbox(
          "Aislación Térmica / Acústica Interior:",
          [
              "Lana de Vidrio 50mm R100",
              "Lana de Vidrio 80mm R188",
              "Lana de Roca 50mm Alta Densidad",
          ],
      )
      tipo_internit = st.selectbox(
          "Revestimiento Interior Muros:",
          [
              "Plancha Internit (Fibrocemento) 6 mm",
              "Plancha Internit (Fibrocemento) 8 mm",
              "Volcanita RH (Resistente Humedad) 12.5 mm",
          ],
      )
      tipo_pegamento = st.selectbox(
          "Adhesivo para Cerámicos:",
          [
              "Bekron Flex (Porcelanato/Sustrito Flexible)",
              "Bekron ACI (Sustrato Rígido/Exterior)",
              "Bekron AC (Estd.)",
          ],
      )
      tipo_pintura_cielo = st.selectbox(
          "Pintura para Cielo:",
          [
              "Esmalte al Agua Antihongo Mate",
              "Látex Antihongo Extra Cubriente",
              "Óleo Opaco",
          ],
      )

    datos_et = {
        "Estructura": "Perfiles Metalcom C90x0.85 y U90x0.85",
        "Exterior": f"{espesor_osb} + Barrera Humedad + Metalsiding",
        "Aislación": tipo_insul,
        "Interior Muros": f"{tipo_internit} + Cerámico",
        "Piso": "Cerámico Antideslizante + Adhesivo",
        "Cielo": f"Yeso-Cartón/Internit + Pintura {tipo_pintura_cielo}",
        "Normativa": "OGUC Art 5.5.1 / NCh 353 / NCh 1071 / Manual Metalcom CINTAC",
    }

    if st.button("➕ Generar Cuadrilla y Materiales Módulo Completo"):
      # Cubicaciones exactas con mermas operativas
      planchas_osb = round((area_muros / 2.976) * 1.10, 1)  # 1.22 x 2.44 m
      planchas_internit = round(
          (area_muros / 2.88) * 1.10, 1
      )  # 1.20 x 2.40 m
      planchas_cielo = round((area_piso / 2.88) * 1.10, 1)

      m2_metalsiding = round(area_muros * 1.08, 2)
      m2_aislacion = round((area_muros + area_piso) * 1.05, 2)

      m2_ceramico_muro = round(area_muros * 1.10, 2)
      m2_ceramico_piso = round(area_piso * 1.10, 2)

      sacos_pegamento = round(
          (area_muros + area_piso) / 3.5, 1
      )  # Rendimiento ~3.5 m² por saco 25kg
      kg_frague = round((area_muros + area_piso) * 0.40, 1)

      tinetas_pintura_cielo = max(1.0, round(area_piso / 35.0, 1))

      nuevos_items = [
          {
              "Partida": (
                  "Estructura Metalcom C90x0.85 y U90x0.85 (Muros y Soleras)"
                  " (m²)"
              ),
              "Cantidad": round(area_muros, 2),
              "Precio Unit.": 14500.0,
          },
          {
              "Partida": (
                  "Tornillos Autoperforantes T1 Lenteja y T2 Broca (caja 500"
                  " un)"
              ),
              "Cantidad": 2.0,
              "Precio Unit.": 9800.0,
          },
          {
              "Partida": f"Placa Estructural {espesor_osb} 1.22x2.44m (planchas)",
              "Cantidad": planchas_osb,
              "Precio Unit.": 12800.0,
          },
          {
              "Partida": (
                  "Fieltro Asfáltico 15 lb / Membrana Barrera de Humedad (rollo"
                  " 40m²)"
              ),
              "Cantidad": max(1.0, round(area_muros / 38.0, 1)),
              "Precio Unit.": 18500.0,
          },
          {
              "Partida": (
                  "Revestimiento Exterior Metalsiding (incluye perfiles j y"
                  " esquineros) (m²)"
              ),
              "Cantidad": m2_metalsiding,
              "Precio Unit.": 21500.0,
          },
          {
              "Partida": (
                  f"Aislación {tipo_insul} para Muros y Cielo (m²)"
              ),
              "Cantidad": m2_aislacion,
              "Precio Unit.": 4200.0,
          },
          {
              "Partida": f"Revestimiento Muros {tipo_internit} (planchas)",
              "Cantidad": planchas_internit,
              "Precio Unit.": 11500.0,
          },
          {
              "Partida": (
                  "Revestimiento Cielo Plancha Yeso-Cartón/Internit 10mm"
                  " (planchas)"
              ),
              "Cantidad": planchas_cielo,
              "Precio Unit.": 8900.0,
          },
          {
              "Partida": "Cerámico Muros Antihongo 30x60 (m²)",
              "Cantidad": m2_ceramico_muro,
              "Precio Unit.": 12500.0,
          },
          {
              "Partida": "Cerámico Piso Antideslizante 45x45 / 60x60 (m²)",
              "Cantidad": m2_ceramico_piso,
              "Precio Unit.": 13800.0,
          },
          {
              "Partida": (
                  f"Adhesivo Pegamento {tipo_pegamento} (saco 25kg)"
              ),
              "Cantidad": sacos_pegamento,
              "Precio Unit.": 11200.0,
          },
          {
              "Partida": "Fragüe Antihongo Impermeable (kg)",
              "Cantidad": kg_frague,
              "Precio Unit.": 2800.0,
          },
          {
              "Partida": (
                  f"Pintura Cielo {tipo_pintura_cielo} (tineta 4gal)"
              ),
              "Cantidad": tinetas_pintura_cielo,
              "Precio Unit.": 38000.0,
          },
          {
              "Partida": (
                  "Pasta Muro, Cinta Junta Fibra de Vidrio, Esquineros y"
                  " Silicona Sanitaria (gl)"
              ),
              "Cantidad": 1.0,
              "Precio Unit.": 26000.0,
          },
      ]

  # ==========================================
  # ⚡ 1. ELECTRICIDAD
  # ==========================================
  elif "Electricidad" in recinto_actual:
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
      ]

  # ==========================================
  # 🎨 2. PINTURA Y CIELOS
  # ==========================================
  elif "Pintura" in recinto_actual:
    with st.expander(
        "🖌️ Parámetros de Pintura y Cielos", expanded=True
    ):
      p_tipo = st.selectbox(
          "Tipo de Pintura Principal:",
          [
              "Esmalte al Agua Antihongo (Semibrillo / Mate)",
              "Óleo Opaco Sintético",
              "Óleo Brillante",
              "Látex Extra Cubriente Cielos",
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

    datos_et = {
        "Pintura": p_tipo,
        "Manos": p_manos,
        "Normativa": "NCh 331 - Pinturas y Barnices",
    }

    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      cant_sup = area_muros + area_piso
      nuevos_items = [
          {
              "Partida": f"Pintura {p_tipo} (tineta 4g)",
              "Cantidad": max(1.0, round(cant_sup / 35.0, 1)),
              "Precio Unit.": 44000.0,
          },
          {
              "Partida": "Pasta Muro / Empaste (saco/tarro)",
              "Cantidad": max(1.0, round(cant_sup / 20.0, 1)),
              "Precio Unit.": 13500.0,
          },
          {
              "Partida": (
                  "Kit Lijas de Muro, Cinta Masking, Plástico Protector (gl)"
              ),
              "Cantidad": 1.0,
              "Precio Unit.": 16000.0,
          },
      ]

  # ==========================================
  # 🚿 OTROS RECINTOS
  # ==========================================
  else:
    st.write(
        "Presiona el botón para cargar partidas estándar de esta especialidad."
    )
    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      nuevos_items = [
          {
              "Partida": "Insumos Varios / Partida Estándar (gl)",
              "Cantidad": 1.0,
              "Precio Unit.": 25000.0,
          },
      ]

  # LÓGICA DE ACUMULACIÓN Y REFRESCO
  if nuevos_items:
    existentes = st.session_state["partidas_recintos"].get(recinto_actual, [])
    st.session_state["partidas_recintos"][recinto_actual] = (
        existentes + nuevos_items
    )
    st.session_state["detalles_tecnicos"][recinto_actual] = datos_et

    key_editor = f"editor_{recinto_actual}"
    if key_editor in st.session_state:
      del st.session_state[key_editor]

    st.success(
        f"✅ ¡Se agregaron {len(nuevos_items)} partidas acumuladas a"
        f" **{recinto_actual}**!"
    )
    st.rerun()

  st.markdown("---")
  col_t1, col_t2 = st.columns([3, 1])
  with col_t1:
    st.markdown(
        f"### ✏️ Gestor Interactivo: **{recinto_actual}** (Edita o modifica"
        " valores)"
    )
  with col_t2:
    if st.button("🗑️ Vaciar este Recinto"):
      st.session_state["partidas_recintos"][recinto_actual] = []
      key_editor = f"editor_{recinto_actual}"
      if key_editor in st.session_state:
        del st.session_state[key_editor]
      st.rerun()

  if (
      recinto_actual in st.session_state["partidas_recintos"]
      and st.session_state["partidas_recintos"][recinto_actual]
  ):
    df_actual = pd.DataFrame(
        st.session_state["partidas_recintos"][recinto_actual]
    )

    df_editado = st.data_editor(
        df_actual,
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_{recinto_actual}",
    )

    st.session_state["partidas_recintos"][recinto_actual] = df_editado.to_dict(
        "records"
    )
  else:
    st.info(
        "Aún no hay partidas cargadas para esta especialidad. Presiona '➕"
        " Generar Materiales' arriba."
    )

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
  st.markdown(
      "**Constructor Responsable:** Constructor Civil - Concepción, Chile"
  )
  st.markdown("---")

  if st.session_state["partidas_recintos"]:
    texto_et_exportar = ""
    for recinto, items in st.session_state["partidas_recintos"].items():
      if items:
        st.markdown(f"### 📌 ESPECIALIDAD / SECTOR: {recinto}")
        texto_et_exportar += f"ESPECIALIDAD / SECTOR: {recinto}\n"

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
