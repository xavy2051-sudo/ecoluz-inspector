# -----------------------------------------------------------------------------
# MÓDULO 1: CONFIGURACIÓN Y SELECCIÓN DE MATERIALES
# -----------------------------------------------------------------------------
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

  # --- OPCIÓN 1: MÓDULO COMPLETO METALCOM ---
  if "Módulo Completo Metalcom" in recinto_actual:
    with st.expander(
        "🏗️ Parámetros de la Solución Constructiva Multicapa", expanded=True
    ):
      espesor_osb = st.selectbox(
          "Placa Estructural Exterior:",
          ["OSB 11.1 mm", "OSB 9.5 mm", "Terciado Estructural 12 mm"],
      )
      tipo_barrera = st.selectbox(
          "Barrera de Humedad Exterior Muros:",
          [
              "Fieltro Asfáltico 15 lb (Económico)",
              "Membrana Hidrófuga Respirable (Tipo Tyvek / Dorken)",
          ],
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
        "Exterior": f"{espesor_osb} + {tipo_barrera} + Metalsiding",
        "Aislación": tipo_insul,
        "Interior Muros": f"{tipo_internit} + Cerámico",
        "Piso": "Cerámico Antideslizante + Adhesivo",
        "Cielo": f"Yeso-Cartón/Internit + Pintura {tipo_pintura_cielo}",
        "Normativa": (
            "OGUC Art 5.5.1 / NCh 353 / NCh 1071 / Manual Metalcom CINTAC"
        ),
    }

    if st.button(
        "➕ Generar y Agregar Módulo Metalcom", key="btn_metalcom_m1"
    ):
      planchas_osb = round((area_muros / 2.976) * 1.10, 1)
      planchas_internit = round((area_muros / 2.88) * 1.10, 1)
      planchas_cielo = round((area_piso / 2.88) * 1.10, 1)

      m2_metalsiding = round(area_muros * 1.08, 2)
      m2_aislacion = round((area_muros + area_piso) * 1.05, 2)
      m2_ceramico_muro = round(area_muros * 1.10, 2)
      m2_ceramico_piso = round(area_piso * 1.10, 2)

      sacos_pegamento = round((area_muros + area_piso) / 3.5, 1)
      kg_frague = round((area_muros + area_piso) * 0.40, 1)
      tinetas_pintura_cielo = max(1.0, round(area_piso / 35.0, 1))

      if "Fieltro" in tipo_barrera:
        partida_barrera = "Fieltro Asfáltico 15 lb para Muros (rollo 40m²)"
        cant_barrera = max(1.0, round(area_muros / 38.0, 1))
        precio_barrera = 18500.0
      else:
        partida_barrera = (
            "Membrana Hidrófuga Respirable Muros (rollo 50m² - Tyvek/Dorken)"
        )
        cant_barrera = max(1.0, round(area_muros / 48.0, 1))
        precio_barrera = 48000.0

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
              "Partida": partida_barrera,
              "Cantidad": cant_barrera,
              "Precio Unit.": precio_barrera,
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
              "Partida": f"Aislación {tipo_insul} para Muros y Cielo (m²)",
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
              "Partida": f"Adhesivo Pegamento {tipo_pegamento} (saco 25kg)",
              "Cantidad": sacos_pegamento,
              "Precio Unit.": 11200.0,
          },
          {
              "Partida": "Fragüe Antihongo Impermeable (kg)",
              "Cantidad": kg_frague,
              "Precio Unit.": 2800.0,
          },
          {
              "Partida": f"Pintura Cielo {tipo_pintura_cielo} (tineta 4gal)",
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

  # --- OPCIÓN 2: TECHUMBRE Y CUBIERTAS COMPLETA ---
  elif "Techumbre y Cubiertas" in recinto_actual:
    with st.expander(
        "🏠 Parámetros Técnicos de Techumbre y Cubierta", expanded=True
    ):
      pendiente_pct = st.slider("Pendiente del Techo (%):", 15, 60, 30)
      espesor_osb_techo = st.selectbox(
          "Base Estructural Techo (OSB / Terciado):",
          [
              "OSB Estructural Techo 11.1 mm",
              "OSB Estructural Techo 15.0 mm",
              "Terciado Estructural 12 mm",
          ],
      )
      barrera_techo = st.selectbox(
          "Barrera de Humedad e Impermeabilización Techo:",
          [
              "Fieltro Asfáltico 15 lb Techo",
              "Fieltro Asfáltico 30 lb Techo (Reforzado)",
              "Membrana Hidrófuga Respirable de Techo (Especial Techo)",
          ],
      )
      tipo_cubierta = st.selectbox(
          "Cubierta Final de Techo:",
          [
              "Teja Asfáltica Hexagonal / Arquitectónica (m²)",
              "Plancha Zinc-Alum 0.40mm Onda Toledana / 5V (m²)",
              "Plancha Zinc-Alum 0.35mm Estándar (m²)",
              "Teja Gravillada Metálica (m²)",
          ],
      )
      hojalateria_incluida = st.checkbox(
          "Incluir Hojalatería (Caballete Cumbrera, Limahoyas, Forros y"
          " Bajadas PVC)",
          value=True,
      )

    factor_pendiente = math.sqrt(1 + (pendiente_pct / 100.0) ** 2)
    area_techo_real = area_piso * factor_pendiente

    datos_et = {
        "Estructura Techo": "Cerchas y Costaneras Metalcom / Omegas",
        "Base Placa": espesor_osb_techo,
        "Aislante/Barrera": barrera_techo,
        "Cubierta": tipo_cubierta,
        "Aguas Lluvias": (
            "Canaletas PVC / Zinc + Bajadas + Caballetes Cumbrera"
            if hojalateria_incluida
            else "Sin Hojalatería"
        ),
        "Pendiente": f"{pendiente_pct}%",
        "Normativa": "OGUC Art 5.5.3 / NCh 1071",
    }

    if st.button("➕ Generar y Agregar Techumbre", key="btn_techumbre_m1"):
      planchas_osb_t = round((area_techo_real / 2.976) * 1.10, 1)

      if "15 lb" in barrera_techo:
        cant_barrera_t = max(1.0, round(area_techo_real / 38.0, 1))
        p_barrera_t = 18500.0
      elif "30 lb" in barrera_techo:
        cant_barrera_t = max(1.0, round(area_techo_real / 18.0, 1))
        p_barrera_t = 24500.0
      else:
        cant_barrera_t = max(1.0, round(area_techo_real / 48.0, 1))
        p_barrera_t = 52000.0

      if "Teja Asfáltica" in tipo_cubierta:
        pu_cub = 16800.0
      elif "0.40mm" in tipo_cubierta:
        pu_cub = 13500.0
      elif "0.35mm" in tipo_cubierta:
        pu_cub = 10500.0
      else:
        pu_cub = 22000.0

      nuevos_items = [
          {
              "Partida": (
                  "Estructura de Cerchas, Costaneras Omegas y Frontones (m²"
                  " proyección)"
              ),
              "Cantidad": round(area_techo_real, 2),
              "Precio Unit.": 16500.0,
          },
          {
              "Partida": (
                  f"Placa Base {espesor_osb_techo} 1.22x2.44m (planchas)"
              ),
              "Cantidad": planchas_osb_t,
              "Precio Unit.": 13500.0,
          },
          {
              "Partida": f"{barrera_techo} (rollos)",
              "Cantidad": cant_barrera_t,
              "Precio Unit.": p_barrera_t,
          },
          {
              "Partida": f"Cubierta {tipo_cubierta}",
              "Cantidad": round(area_techo_real * 1.08, 2),
              "Precio Unit.": pu_cub,
          },
          {
              "Partida": (
                  "Tornillos Autoperforantes con Golilla Neopreno Hexagonal 2\""
                  " (caja 250 un)"
              ),
              "Cantidad": max(1.0, round(area_techo_real / 25.0, 1)),
              "Precio Unit.": 11800.0,
          },
          {
              "Partida": (
                  "Aislación Lana de Vidrio / Roca R188 para Entrepiso/Techo"
                  " (m²)"
              ),
              "Cantidad": round(area_piso * 1.05, 2),
              "Precio Unit.": 4800.0,
          },
      ]

      if hojalateria_incluida:
        nuevos_items.extend([
            {
                "Partida": (
                    "Caballete Cumbrera Zinc / Asfáltico con Desarrollo 33cm"
                    " (mL)"
                ),
                "Cantidad": round(largo, 2),
                "Precio Unit.": 8500.0,
            },
            {
                "Partida": (
                    "Canaletas de Agua Lluvia PVC / Zinc Desarrollo 33cm (mL)"
                ),
                "Cantidad": round(perimetro, 2),
                "Precio Unit.": 9200.0,
            },
            {
                "Partida": (
                    "Bajadas de Agua Lluvia PVC 75mm / Zinc con Abrazaderas"
                    " (mL)"
                ),
                "Cantidad": round(alto * 2, 2),
                "Precio Unit.": 7800.0,
            },
            {
                "Partida": (
                    "Sellante Hojalatería Poliuretano / Masilla Asfáltica (un)"
                ),
                "Cantidad": 2.0,
                "Precio Unit.": 6900.0,
            },
        ])

  else:
    if st.button("➕ Generar Partida Estándar", key="btn_generico_m1"):
      nuevos_items = [{
          "Partida": "Insumos Varios / Partida Estándar (gl)",
          "Cantidad": 1.0,
          "Precio Unit.": 25000.0,
      }]

  # --- BLOQUE DE ACUMULACIÓN CORREGIDO ---
  if nuevos_items:
    # Usamos un sufijo o almacenamos por separado si se desea, pero para que se sumen
    # en la misma tabla sin sobreescribir, usamos la extensión de la lista existente:
    if recinto_actual not in st.session_state["partidas_recintos"]:
      st.session_state["partidas_recintos"][recinto_actual] = []

    st.session_state["partidas_recintos"][recinto_actual].extend(nuevos_items)
    st.session_state["detalles_tecnicos"][recinto_actual] = datos_et

    key_editor = f"editor_{recinto_actual}"
    if key_editor in st.session_state:
      del st.session_state[key_editor]

    st.success(
        f"✅ ¡Se agregaron {len(nuevos_items)} partidas a"
        f" **{recinto_actual}** de forma acumulada!"
    )
    st.rerun()
