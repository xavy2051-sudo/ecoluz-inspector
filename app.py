import pandas as pd
import streamlit as st

st.set_page_config(
    page_title='ECOLUZ - Cerebro Inspector Técnico', layout='wide'
)

st.title('🏗️ ECOLUZ - Cerebro Inspector Técnico')
st.markdown(
    'Levantamiento, Cubicaciones, Registro Fotográfico y Cotizador Comercial'
    ' Exprés'
)

# ----------------- MENÚ LATERAL (MÓDULO DE TRABAJO) -----------------
st.sidebar.title('📋 Módulo de Trabajo')
modulo = st.sidebar.radio(
    'Seleccione Fase:',
    [
        '1. Levantamiento y Cubicaciones',
        '2. Registro Fotográfico y Planos',
        '3. Especificaciones Técnicas (ET)',
        '4. Análisis de Precios Unitarios (APU)',
        '5. Cierre Económico y Presupuesto',
    ],
)

if 'partidas_recintos' not in st.session_state:
  st.session_state['partidas_recintos'] = {}

# ----------------- MÓDULO 1 -----------------
if modulo == '1. Levantamiento y Cubicaciones':
  st.subheader('📐 Módulo 1: Geometría y Asignación de Partidas')
  recinto_actual = st.selectbox(
      'Seleccionar Recinto',
      [
          'Baño Principal',
          'Cocina',
          'Dormitorio Principal',
          'Estar-Comedor',
          'Pasillo',
          'Exterior',
      ],
  )

  col1, col2 = st.columns(2)
  with col1:
    largo = st.number_input('Largo (m)', value=3.70, step=0.01, key='l_m1')
    ancho = st.number_input('Ancho (m)', value=1.85, step=0.01, key='a_m1')
  with col2:
    alto = st.number_input('Alto (m)', value=2.40, step=0.01, key='h_m1')

  area_piso = largo * ancho
  perimetro = 2 * (largo + ancho)
  area_muros = perimetro * alto

  st.markdown(
      f'**Resumen Métrico:** Área Piso: `{area_piso:.2f} m²` | Perímetro:'
      f' `{perimetro:.2f} m` | Área Muros Bruta: `{area_muros:.2f} m²`'
  )

  st.markdown('---')
  st.subheader('🛠️ Asignación de Partidas y Materiales')

  col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
  with col_p1:
    partida_seleccionada = st.selectbox(
        'Partida / Revestimiento / Insumo',
        [
            'Radier de Hormigón H-20',
            'Estructura Metalcom C 90x0.85 (Tabiques)',
            'Placa Yeso Cartón Volcanita RH 12.5mm',
            'Cerámico Muro 30x60',
            'Porcelanato Piso 60x60',
            'Adhesivo Cerámico (25kg)',
            'Frague Flexible (1kg)',
            'Pintura Esmalte al Agua (Cielo)',
            'Tubería PVC Sanitaria 110mm / 50mm',
            'Red Hidráulica PPR / Cobre',
        ],
    )
  with col_p2:
    cantidad_ingresada = st.number_input(
        'Cantidad / Rendimiento', min_value=0.01, value=1.0, step=0.1
    )
  with col_p3:
    precio_ingresado = st.number_input(
        'Precio Unitario ($)', min_value=0.0, value=12500.0, step=500.0
    )

  if st.button('➕ Agregar Partida al Resumen del Recinto'):
    if recinto_actual not in st.session_state['partidas_recintos']:
      st.session_state['partidas_recintos'][recinto_actual] = []
    st.session_state['partidas_recintos'][recinto_actual].append({
        'Partida': partida_seleccionada,
        'Cantidad': cantidad_ingresada,
        'Precio Unit.': precio_ingresado,
        'Costo Total': cantidad_ingresada * precio_ingresado,
    })
    st.success(f'Partida agregada exitosamente a **{recinto_actual}**.')

  st.markdown(f'### 📋 Desglose Técnico y Económico: {recinto_actual}')
  if (
      recinto_actual in st.session_state['partidas_recintos']
      and st.session_state['partidas_recintos'][recinto_actual]
  ):
    df_partidas = pd.DataFrame(
        st.session_state['partidas_recintos'][recinto_actual]
    )
    st.dataframe(df_partidas, use_container_width=True)
    if st.button('🗑️ Limpiar partidas de este recinto'):
      st.session_state['partidas_recintos'][recinto_actual] = []
      st.rerun()
  else:
    st.info(
        f'Aún no hay partidas asignadas para {recinto_actual}. Selecciona y'
        ' agrega los materiales arriba.'
    )

# ----------------- MÓDULO 2 -----------------
elif modulo == '2. Registro Fotográfico y Planos':
  st.subheader('📸 Módulo 2: Registro Fotográfico y Validación de Planos')
  recinto_m2 = st.selectbox(
      'Seleccionar Recinto a Inspeccionar en Plano',
      [
          'Baño Principal',
          'Cocina',
          'Dormitorio Principal',
          'Estar-Comedor',
          'Pasillo',
          'Exterior',
      ],
  )

  col_m2_1, col_m2_2 = st.columns(2)
  with col_m2_1:
    st.markdown('### 📐 Validación de Medidas vs. Plano')
    largo_m1 = st.number_input(
        'Largo Cubicado (m)', value=3.70, step=0.01, key='lm1'
    )
    ancho_m1 = st.number_input(
        'Ancho Cubicado (m)', value=1.85, step=0.01, key='am1'
    )
    largo_plano = st.number_input(
        'Largo según Plano (m)', value=3.70, step=0.01, key='lp'
    )
    ancho_plano = st.number_input(
        'Ancho según Plano (m)', value=1.85, step=0.01, key='ap'
    )

    tolerancia = 0.05
    dif_largo = abs(largo_m1 - largo_plano)
    dif_ancho = abs(ancho_m1 - ancho_plano)

    st.markdown('---')
    if dif_largo > tolerancia or dif_ancho > tolerancia:
      st.error(
          '⚠️ **¡Alerta de Incongruencia Detectada!**\n\nLas medidas difieren'
          f' del plano:\n- **Diferencia Largo:** {dif_largo:.2f}m\n- **Diferencia'
          f' Ancho:** {dif_ancho:.2f}m'
      )
    else:
      st.success('✅ **Medidas Conformes:** Coinciden con las cotas del plano.')

  with col_m2_2:
    st.markdown('### 📷 Evidencia Fotográfica y Plano Adjunto')
    st.file_uploader(
        'Subir Plano del Recinto (Imagen / PDF)',
        type=['png', 'jpg', 'jpeg', 'pdf'],
    )
    st.file_uploader(
        'Subir Fotografías de Inspección',
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
    )

# ----------------- MÓDULO 3 -----------------
elif modulo == '3. Especificaciones Técnicas (ET)':
  st.subheader('📄 ESPECIFICACIONES TÉCNICAS DE CONSTRUCCIÓN')
  st.markdown('---')
  st.markdown('### 🏛️ PROYECTO: ESPECIALIDADES ECOLUZ')
  st.markdown(
      '**Materialidad:** Estructura Metálica / Metalcom / Terminaciones de'
      ' Primera'
  )
  st.markdown('**Constructor:** Constructor Civil - ECOLUZ SpA')
  st.markdown('---')

  if st.session_state['partidas_recintos']:
    for recinto, items in st.session_state['partidas_recintos'].items():
      if items:
        st.markdown(f'#### 📌 Recinto: {recinto}')
        for idx, item in enumerate(items, 1):
          st.markdown(f'**{idx}. {item["Partida"]}**')
          st.markdown(
              f'   - *Descripción Técnica:* Suministro e instalación de'
              f' {item["Partida"]} ejecutado según normativa chilena vigente y'
              ' altos estándares de calidad.'
          )
          st.markdown(
              f'   - *Metrado / Cantidad:* `{item["Cantidad"]}` unidades o'
              ' metros cuadrados asignados.'
          )
        st.markdown('')
  else:
    st.warning(
        '⚠️ Aún no se han registrado partidas en el Módulo 1 para redactar las'
        ' Especificaciones Técnicas.'
    )

# ----------------- MÓDULO 4 -----------------
elif modulo == '4. Análisis de Precios Unitarios (APU)':
  st.subheader('💰 Módulo 4: Análisis de Precios Unitarios y Consolidado')

  todos_los_datos = []
  for recinto, items in st.session_state['partidas_recintos'].items():
    for item in items:
      fila = item.copy()
      fila['Recinto'] = recinto
      todos_los_datos.append(fila)

  if todos_los_datos:
    df_total = pd.DataFrame(todos_los_datos)
    df_total = df_total[[
        'Recinto',
        'Partida',
        'Cantidad',
        'Precio Unit.',
        'Costo Total',
    ]]
    st.dataframe(df_total, use_container_width=True)

    costo_directo = df_total['Costo Total'].sum()
    st.markdown('---')
    st.markdown(
        f'### 💵 **Costo Directo Total de Obra:** 💲 `{costo_directo:,.0f}`'
    )

    col_apu1, col_apu2 = st.columns(2)
    with col_apu1:
      gg_pct = st.number_input('Gastos Generales (%)', value=10.0, step=1.0)
    with col_apu2:
      util_pct = st.number_input('Utilidad (%)', value=15.0, step=1.0)

    costo_gg = costo_directo * (gg_pct / 100.0)
    costo_util = costo_directo * (util_pct / 100.0)
    subtotal_neto = costo_directo + costo_gg + costo_util
    iva = subtotal_neto * 0.19
    total_presupuesto = subtotal_neto + iva

    st.markdown('---')
    st.markdown('#### 📊 Resumen Financiero Comercial')
    st.markdown(f'- **Costo Directo:** 💲 `{costo_directo:,.0f}`')
    st.markdown(f'- **Gastos Generales ({gg_pct}%):** 💲 `{costo_gg:,.0f}`')
    st.markdown(f'- **Utilidad ({util_pct}%):** 💲 `{costo_util:,.0f}`')
    st.markdown(f'- **Subtotal Neto:** 💲 `{subtotal_neto:,.0f}`')
    st.markdown(f'- **IVA (19%):** 💲 `{iva:,.0f}`')
    st.markdown(
        f'### 🚀 **Presupuesto Total Con IVA:** 💲 `{total_presupuesto:,.0f}`'
    )
  else:
    st.info(
        'ℹ️ No hay partidas cargadas todavía. Completa el Módulo 1 para'
        ' visualizar los APU.'
    )

# ----------------- MÓDULO 5 -----------------
elif modulo == '5. Cierre Económico y Presupuesto':
  st.subheader('📊 Módulo 5: Cotización Comercial Amigable para el Cliente')
  st.markdown('---')
  st.markdown('### 🏢 PROPUESTA ECONÓMICA - ESPECIALIDADES ECOLUZ')

  col_cot1, col_cot2 = st.columns(2)
  with col_cot1:
    st.markdown('**Emitido por:** Constructor Civil / ECOLUZ SpA')
    st.markdown('**Ciudad:** Concepción, Chile')
  with col_cot2:
    st.markdown('**Validez de la Oferta:** 15 Días')
    st.markdown('**Forma de Pago:** 50% Anticipo - 50% Recepción Conforme')

  st.markdown('---')

  todos_los_datos = []
  for recinto, items in st.session_state['partidas_recintos'].items():
    for item in items:
      fila = item.copy()
      fila['Recinto'] = recinto
      todos_los_datos.append(fila)

  if todos_los_datos:
    df_cot = pd.DataFrame(todos_los_datos)

    st.markdown(
        '#### 📋 Detalle de Partidas, Cubicaciones y Valores por Recinto'
    )
    df_cliente = df_cot[
        ['Recinto', 'Partida', 'Cantidad', 'Costo Total']
    ].copy()
    df_cliente.columns = [
        'Recinto',
        'Partida / Revestimiento',
        'Cantidad / m²',
        'Total Parcial',
    ]
    st.dataframe(df_cliente, use_container_width=True)

    costo_directo = df_cot['Costo Total'].sum()
    costo_gg = costo_directo * 0.10
    costo_util = costo_directo * 0.15
    subtotal_neto = costo_directo + costo_gg + costo_util
    iva = subtotal_neto * 0.19
    total_presupuesto = subtotal_neto + iva

    st.markdown('---')
    st.markdown('#### 📊 Resumen Financiero de la Propuesta')
    st.markdown(f'- **Costo Directo de Obras:** 💲 `{costo_directo:,.0f}`')
    st.markdown(
        f'- **Gastos Generales y Utilidad (25%):** 💲'
        f' `{(costo_gg + costo_util):,.0f}`'
    )
    st.markdown(f'- **Subtotal Neto:** 💲 `{subtotal_neto:,.0f}`')
    st.markdown(f'- **IVA (19%):** 💲 `{iva:,.0f}`')
    st.markdown('---')
    st.markdown(
        f'## 💰 **VALOR TOTAL A PAGAR POR EL CLIENTE (CON IVA):** 💲'
        f' `{total_presupuesto:,.0f}`'
    )
    st.markdown('---')

    # SECCIÓN AMIGABLE: MENSAJE PARA WHATSAPP
    st.markdown('### 💬 Mensaje Rápido para Enviar por WhatsApp / Chat')
    mensaje_wsp = (
        '🏡 *PROPUESTA ECONÓMICA - ECOLUZ SpA*\n\nEstimado(a) cliente,'
        ' adjunto el resumen de la propuesta para su proyecto:\n\n'
    )
    for index, row in df_cliente.iterrows():
      mensaje_wsp += (
          f'▪️ *{row["Recinto"]}* - {row["Partida / Revestimiento"]} '
          f'(Cant: {row["Cantidad / m²"]}): ${row["Total Parcial"]:,.0f}\n'
      )
    mensaje_wsp += f'\n🚀 *VALOR TOTAL (CON IVA):* `${total_presupuesto:,.0f}`\n\nForma de Pago: 50% Anticipo - 50% Recepción Conforme.\nQuedamos atentos a sus comentarios. ¡Saludos cordiales!'

    st.text_area(
        'Copia este texto para enviarlo por WhatsApp:',
        value=mensaje_wsp,
        height=180,
    )

    st.markdown('---')

    # DOCUMENTO HTML/PDF MODERNO Y CORPORATIVO
    html_content = f"""
        <html>
        <head>
            <title>Propuesta Comercial - ECOLUZ SpA</title>
            <style>
                body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 40px; color: #333; background-color: #f9f9f9; }}
                .invoice-box {{ background: #fff; padding: 30px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }}
                h1 {{ color: #1f4e78; margin-bottom: 5px; }}
                .subtitle {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #e0e0e0; padding: 12px; text-align: left; font-size: 14px; }}
                th {{ background-color: #1f4e78; color: white; }}
                tr:nth-child(even) {{ background-color: #f8f9fa; }}
                .summary {{ width: 50%; margin-left: auto; font-size: 14px; }}
                .summary td {{ padding: 8px; border: none; }}
                .total-row {{ font-size: 18px; font-weight: bold; color: #1f4e78; border-top: 2px solid #1f4e78; }}
            </style>
        </head>
        <body>
            <div class="invoice-box">
                <h1>ECOLUZ SpA</h1>
                <div class="subtitle">Constructor Civil | Concepción, Chile</div>
                <hr style="border:0; border-top: 1px solid #ddd;">
                
                <h3>Detalle de Partidas y Cubicaciones</h3>
                {df_cliente.to_html(index=False, classes='table')}
                
                <table class="summary">
                    <tr><td><b>Costo Directo:</b></td><td style="text-align: right;">${costo_directo:,.0f}</td></tr>
                    <tr><td><b>GG y Utilidad (25%):</b></td><td style="text-align: right;">${(costo_gg + costo_util):,.0f}</td></tr>
                    <tr><td><b>Subtotal Neto:</b></td><td style="text-align: right;">${subtotal_neto:,.0f}</td></tr>
                    <tr><td><b>IVA (19%):</b></td><td style="text-align: right;">${iva:,.0f}</td></tr>
                    <tr class="total-row"><td>VALOR TOTAL (CON IVA):</td><td style="text-align: right;">${total_presupuesto:,.0f}</td></tr>
                </table>
                <p style="font-size: 12px; color: #777; text-align: center; margin-top: 40px;">Validez de la oferta: 15 días. Forma de pago: 50% anticipo - 50% recepción conforme.</p>
            </div>
        </body>
        </html>
        """

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
      st.download_button(
          label='📥 Descargar Propuesta Formato PDF / HTML',
          data=html_content,
          file_name='Cotizacion_Ecoluz.html',
          mime='text/html',
      )
    with col_btn2:
      st.success(
          '✨ ¡Todo listo! Copia el texto para WhatsApp o descarga el'
          ' documento para imprimir/guardar en PDF.'
      )
  else:
    st.warning(
        '⚠️ No hay información de partidas registradas. Complete primero el'
        ' Módulo 1.'
    )
