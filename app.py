import pandas as pd
import streamlit as st

st.set_page_config(
    page_title='ECOLUZ - Cerebro Inspector Técnico', layout='wide'
)

st.title('🏗️ ECOLUZ - Cerebro Inspector Técnico & Listado de Ejecución')
st.markdown(
    'Levantamiento, Cubicaciones con Desglose Completo de Materiales, Insumos y'
    ' Consumibles'
)

# ----------------- MENÚ LATERAL (MÓDULO DE TRABAJO) -----------------
st.sidebar.title('📋 Módulo de Trabajo')
modulo = st.sidebar.radio(
    'Seleccione Fase:',
    [
        '1. Levantamiento y Cubicaciones (Desglose Completo)',
        '2. Registro Fotográfico y Planos',
        '3. Especificaciones Técnicas (ET)',
        '4. Análisis de Precios Unitarios (APU)',
        '5. Cierre Económico y Presupuesto',
    ],
)

if 'partidas_recintos' not in st.session_state:
  st.session_state['partidas_recintos'] = {}

# ----------------- MÓDULO 1 -----------------
if modulo == '1. Levantamiento y Cubicaciones (Desglose Completo)':
  st.subheader(
      '📐 Módulo 1: Geometría y Desglose de Materiales para Ejecución en Obra'
  )
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
  st.subheader(
      '🛠️ Selección de Partida Principal (Genera Kit Completo de Materiales y'
      ' Consumibles)'
  )

  # Sistemas constructivos con despliegue técnico profesional chileno
  sistemas_constructivos = [
      'Tabiquería Metalcom Completa (Perfiles + Placas RH + Fijaciones + Juntas)',
      'Revestimiento Cerámico Muro Completo (Cerámica + Adhesivo + Fragüe + Accesorios + Silicona)',
      'Revestimiento Piso Porcelanato Completo (Porcelanato + Adhesivo + Fragüe + Niveladores)',
      'Piso Flotante Completo (Piso + Manta + Guardapolvos + Junquillos)',
      'Radier de Hormigón H-20 Reforzado',
      'Pintura Esmalte al Agua Completa (Pintura + Empaste + Imprimante + Lijas + Protección)',
      'Instalación Sanitaria / Gasfitería Completa (Tuberías PVC/PPR + Codos + Tees + Llaves + Adhesivos)',
      'Instalación Eléctrica Básica (Conduit + Cables + Cajas + Enchufes/Interruptores + Protecciones)',
      'Impermeabilización de Baño / Zona Húmeda (Membrana + Primer + Banda perimetral)',
      'Kit de Consumibles y Aseo de Obra (Discos, Brocas, Sacos escombros, Espuma, Silicona)',
  ]

  partida_maestra = st.selectbox(
      'Seleccione Sistema Constructivo / Partida', sistemas_constructivos
  )

  if st.button(
      '➕ Generar y Agregar Kit Completo de Materiales al Recinto'
  ):
    if recinto_actual not in st.session_state['partidas_recintos']:
      st.session_state['partidas_recintos'][recinto_actual] = []

    nuevos_items = []

    if 'Tabiquería Metalcom Completa' in partida_maestra:
      cant_muros = area_muros
      nuevos_items = [
          {
              'Partida': (
                  'Estructura Perfil C 90x0.85 y Soleras (Metalcom) (m²)'
              ),
              'Cantidad': round(cant_muros, 2),
              'Precio Unit.': 14200.0,
          },
          {
              'Partida': 'Placa Yeso Cartón Volcanita RH 12.5mm (m²)',
              'Cantidad': round(cant_muros, 2),
              'Precio Unit.': 9800.0,
          },
          {
              'Partida': 'Tornillos Punta Broca / Fina (Caja 100un) (unidad)',
              'Cantidad': max(1.0, round(cant_muros / 15.0, 1)),
              'Precio Unit.': 6500.0,
          },
          {
              'Partida': 'Tarugos con Tornillo y Anclajes / Clavos (gl)',
              'Cantidad': max(1.0, round(perimetro / 5.0, 1)),
              'Precio Unit.': 4500.0,
          },
          {
              'Partida': (
                  'Cinta de Juntas (50m) + Masilla Volcanita (Saco 25kg) (gl)'
              ),
              'Cantidad': max(1.0, round(cant_muros / 20.0, 1)),
              'Precio Unit.': 12500.0,
          },
          {
              'Partida': 'Cinta Acústica perimetral (rollo 30m) (gl)',
              'Cantidad': max(1.0, round(perimetro / 15.0, 1)),
              'Precio Unit.': 8900.0,
          },
          {
              'Partida': 'Esquineros Metálicos Galvanizados (barra 3m) (gl)',
              'Cantidad': max(1.0, round(perimetro / 4.0, 1)),
              'Precio Unit.': 3200.0,
          },
      ]

    elif 'Cerámico Muro Completo' in partida_maestra:
      cant_muros = area_muros
      nuevos_items = [
          {
              'Partida': 'Cerámico Muro Formato 30x60 cm (m²)',
              'Cantidad': round(cant_muros * 1.05, 2),
              'Precio Unit.': 22000.0,
          },
          {
              'Partida': 'Adhesivo Cerámico Saco 25kg (saco)',
              'Cantidad': max(1.0, round(cant_muros / 4.0, 1)),
              'Precio Unit.': 8900.0,
          },
          {
              'Partida': 'Frague Flexible Antihongo kg (kg)',
              'Cantidad': max(1.0, round(cant_muros * 0.3, 1)),
              'Precio Unit.': 4500.0,
          },
          {
              'Partida': (
                  'Crucetas (bolsa 100un) + Sistema Niveladores y Cuñas (gl)'
              ),
              'Cantidad': max(1.0, round(cant_muros / 10.0, 1)),
              'Precio Unit.': 7500.0,
          },
          {
              'Partida': 'Perfiles de Terminación / Esquinero PVC (barra) (gl)',
              'Cantidad': max(1.0, round(perimetro / 6.0, 1)),
              'Precio Unit.': 4200.0,
          },
          {
              'Partida': 'Silicona Sanitaria Antihongo (cartucho 300ml) (gl)',
              'Cantidad': max(1.0, round(perimetro / 10.0, 1)),
              'Precio Unit.': 5800.0,
          },
      ]

    elif 'Revestimiento Piso Porcelanato Completo' in partida_maestra:
      cant_piso = area_piso
      nuevos_items = [
          {
              'Partida': 'Porcelanato Piso 60x60 cm (m²)',
              'Cantidad': round(cant_piso * 1.07, 2),
              'Precio Unit.': 28500.0,
          },
          {
              'Partida': 'Adhesivo Especial Porcelanato Saco 25kg (saco)',
              'Cantidad': max(1.0, round(cant_piso / 3.5, 1)),
              'Precio Unit.': 11500.0,
          },
          {
              'Partida': 'Frague para Porcelanato (kg)',
              'Cantidad': max(1.0, round(cant_piso * 0.35, 1)),
              'Precio Unit.': 5200.0,
          },
          {
              'Partida': 'Niveladores y Cuñas para Porcelanato (kit) (gl)',
              'Cantidad': max(1.0, round(cant_piso / 8.0, 1)),
              'Precio Unit.': 9500.0,
          },
      ]

    elif 'Piso Flotante Completo' in partida_maestra:
      cant_piso = area_piso
      nuevos_items = [
          {
              'Partida': 'Piso Flotante 8mm Alto Tráfico (m²)',
              'Cantidad': round(cant_piso * 1.05, 2),
              'Precio Unit.': 16500.0,
          },
          {
              'Partida': 'Manta Polietileno / Acústica bajo piso (m²)',
              'Cantidad': round(cant_piso, 2),
              'Precio Unit.': 1800.0,
          },
          {
              'Partida': 'Guardapolvos MDF 7cm + Junquillos (ml)',
              'Cantidad': round(perimetro, 2),
              'Precio Unit.': 3500.0,
          },
          {
              'Partida': 'Adhesivo montaje, tarugos y tornillos de fijación (gl)',
              'Cantidad': 1.0,
              'Precio Unit.': 6800.0,
          },
      ]

    elif 'Radier de Hormigón H-20' in partida_maestra:
      cant_piso = area_piso
      nuevos_items = [
          {
              'Partida': 'Hormigón H-20 premezclado o cubicación equivalente (m²)',
              'Cantidad': round(cant_piso, 2),
              'Precio Unit.': 18500.0,
          },
          {
              'Partida': 'Polietileno de alta densidad (cancha) (m²)',
              'Cantidad': round(cant_piso * 1.1, 2),
              'Precio Unit.': 1200.0,
          },
          {
              'Partida': 'Malla Acma C-139 para refuerzo radier (m²)',
              'Cantidad': round(cant_piso, 2),
              'Precio Unit.': 6400.0,
          },
      ]

    elif 'Pintura Esmalte al Agua Completa' in partida_maestra:
      cant_sup = area_muros + area_piso
      nuevos_items = [
          {
              'Partida': (
                  'Pintura Esmalte al Agua / Látex Terminación (tineta 4g) (gl)'
              ),
              'Cantidad': max(1.0, round(cant_sup / 35.0, 1)),
              'Precio Unit.': 38000.0,
          },
          {
              'Partida': (
                  'Imprimante / Sellador de muros y Cielos (tineta 4g) (gl)'
              ),
              'Cantidad': max(1.0, round(cant_sup / 45.0, 1)),
              'Precio Unit.': 26000.0,
          },
          {
              'Partida': 'Empaste en saco o tarro para afinado (saco/gl)',
              'Cantidad': max(1.0, round(cant_sup / 20.0, 1)),
              'Precio Unit.': 12000.0,
          },
          {
              'Partida': (
                  'Lijas, Cinta de enmascarar, Plástico y Cartón protección'
                  ' (gl)'
              ),
              'Cantidad': 1.0,
              'Precio Unit.': 15000.0,
          },
          {
              'Partida': 'Rodillos, Brochas y Extensor telescópico (gl)',
              'Cantidad': 1.0,
              'Precio Unit.': 14000.0,
          },
      ]

    elif 'Instalación Sanitaria / Gasfitería Completa' in partida_maestra:
      cant_lin = perimetro
      nuevos_items = [
          {
              'Partida': (
                  'Tubería PVC Sanitaria 110mm / 50mm y PPR Hidráulica (m)'
              ),
              'Cantidad': round(cant_lin * 1.5, 2),
              'Precio Unit.': 12500.0,
          },
          {
              'Partida': (
                  'Codos, Tees, Coplas, Uniones y Reducciones PVC/PPR (gl)'
              ),
              'Cantidad': max(1.0, round(cant_lin / 3.0, 1)),
              'Precio Unit.': 16000.0,
          },
          {
              'Partida': (
                  'Llaves de paso, Adaptadores, Collares y Terminales (gl)'
              ),
              'Cantidad': 2.0,
              'Precio Unit.': 14500.0,
          },
          {
              'Partida': (
                  'Pegamento PVC, Limpiador, Cinta Teflón y Abrazaderas/Soportes'
                  ' (gl)'
              ),
              'Cantidad': 1.0,
              'Precio Unit.': 12800.0,
          },
      ]

    elif 'Instalación Eléctrica Básica' in partida_maestra:
      nuevos_items = [
          {
              'Partida': 'Tubos Conduit, Curvas, Coplas y Cajas de derivación (gl)',
              'Cantidad': 1.0,
              'Precio Unit.': 22000.0,
          },
          {
              'Partida': (
                  'Conductores eléctricos THHN/NYA (rollos/tramos) (gl)'
              ),
              'Cantidad': 1.0,
              'Precio Unit.': 35000.0,
          },
          {
              'Partida': (
                  'Enchufes, Interruptores, Placas y Canaletas PVC (gl)'
              ),
              'Cantidad': 4.0,
              'Precio Unit.': 6500.0,
          },
          {
              'Partida': 'Automáticos, Diferencial y Tablero secundario (gl)',
              'Cantidad': 1.0,
              'Precio Unit.': 48000.0,
          },
      ]

    elif 'Impermeabilización de Baño / Zona Húmeda' in partida_maestra:
      cant_h = area_piso + (area_muros * 0.4)
      nuevos_items = [
          {
              'Partida': 'Membrana Impermeabilizante Líquida / Poliuretano (m²)',
              'Cantidad': round(cant_h, 2),
              'Precio Unit.': 11000.0,
          },
          {
              'Partida': 'Primer / Imprimante para membrana (gl)',
              'Cantidad': 1.0,
              'Precio Unit.': 14500.0,
          },
          {
              'Partida': 'Banda de unión perimetral y sellos para desagües (gl)',
              'Cantidad': 1.0,
              'Precio Unit.': 16000.0,
          },
      ]

    elif 'Kit de Consumibles y Aseo de Obra' in partida_maestra:
      nuevos_items = [
          {
              'Partida': (
                  'Discos de corte, desbaste, brocas y tornillos varios (gl)'
              ),
              'Cantidad': 1.0,
              'Precio Unit.': 18000.0,
          },
          {
              'Partida': (
                  'Espuma expansiva, sellador poliuretano y cinta americana'
                  ' (gl)'
              ),
              'Cantidad': 1.0,
              'Precio Unit.': 14000.0,
          },
          {
              'Partida': (
                  'Bolsas de basura residas y sacos para escombros (pack)'
              ),
              'Cantidad': 2.0,
              'Precio Unit.': 6500.0,
          },
      ]

    for item in nuevos_items:
      st.session_state['partidas_recintos'][recinto_actual].append({
          'Partida': item['Partida'],
          'Cantidad': item['Cantidad'],
          'Precio Unit.': item['Precio Unit.'],
          'Costo Total': item['Cantidad'] * item['Precio Unit.'],
      })

    st.success(
        f'✅ Kit completo de materiales agregado exitosamente a'
        f' **{recinto_actual}**.'
    )

  st.markdown(f'### 📋 Desglose Técnico y Económico Detallado: {recinto_actual}')
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
        ' genera los materiales arriba.'
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
  st.subheader(
      '📄 ESPECIFICACIONES TÉCNICAS Y LISTADO DE EJECUCIÓN PARA MAESTROS'
  )
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
              f'   - *Especificación Técnica:* Suministro, accesorios e'
              f' instalación rigurosa de {item["Partida"]} según normativa'
              ' chilena vigente y estándares constructivos de ECOLUZ SpA.'
          )
          st.markdown(
              f'   - *Cantidad Requerida en Obra:* `{item["Cantidad"]}`'
              ' unidades / metros / sacos asignados.'
          )
        st.markdown('')
  else:
    st.warning(
        '⚠️ Aún no se han registrado partidas en el Módulo 1 para redactar las'
        ' Especificaciones Técnicas.'
    )

# ----------------- MÓDULO 4 -----------------
elif modulo == '4. Análisis de Precios Unitarios (APU)':
  st.subheader(
      '💰 Módulo 4: Análisis de Precios Unitarios y Consolidado de Materiales'
  )

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
  st.subheader(
      '📊 Módulo 5: Cotización Comercial y Listado de Compras para Obra'
  )
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
        '#### 📋 Detalle de Materiales, Insumos y Cubicaciones por Recinto'
    )
    df_cliente = df_cot[
        ['Recinto', 'Partida', 'Cantidad', 'Costo Total']
    ].copy()
    df_cliente.columns = [
        'Recinto',
        'Material / Partida / Accesorio',
        'Cantidad / Unidad',
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
    st.markdown(f'- **Costo Directo de Materiales y Obras:** 💲 `{costo_directo:,.0f}`')
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

    # MENSAJE PARA WHATSAPP
    st.markdown('### 💬 Mensaje Rápido para Enviar por WhatsApp / Chat')
    mensaje_wsp = (
        '🏡 *PROPUESTA Y LISTADO TÉCNICO - ECOLUZ SpA*\n\nEstimado(a) cliente,'
        ' adjunto el detalle completo de materiales e insumos para su'
        ' proyecto:\n\n'
    )
    for index, row in df_cliente.iterrows():
      mensaje_wsp += (
          f'▪️ *{row["Recinto"]}* - {row["Material / Partida / Accesorio"]} '
          f'(Cant: {row["Cantidad / Unidad"]}): ${row["Total Parcial"]:,.0f}\n'
      )
    mensaje_wsp += f'\n🚀 *VALOR TOTAL (CON IVA):* `${total_presupuesto:,.0f}`\n\nForma de Pago: 50% Anticipo - 50% Recepción Conforme.\nQuedamos atentos a sus comentarios. ¡Saludos cordiales!'

    st.text_area(
        'Copia este texto para enviarlo por WhatsApp:',
        value=mensaje_wsp,
        height=180,
    )

    st.markdown('---')

    html_content = f"""
        <html>
        <head>
            <title>Propuesta y Listado de Materiales - ECOLUZ SpA</title>
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
                
                <h3>Detalle Completo de Materiales, Insumos y Cubicaciones</h3>
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
          '✨ ¡Todo listo! Listado completo de materiales y accesorios listo'
          ' para la ejecución en obra.'
      )
  else:
    st.warning(
        '⚠️ No hay información de partidas registradas. Complete primero el'
        ' Módulo 1.'
    )
