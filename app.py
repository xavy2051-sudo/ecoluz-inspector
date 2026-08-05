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

# Inicializar estructura en session_state para partidas múltiples por recinto
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
  st.subheader('🛠️ Asignación de Partidas y Materiales (Desde SQLite)')

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

# ----------------- MÓDULOS RESTANTES -----------------
elif modulo == '3. Especificaciones Técnicas (ET)':
  st.subheader('📄 Módulo 3: Especificaciones Técnicas')
  st.info(
      'Aquí se consolidarán automáticamente todas las partidas ingresadas por'
      ' recinto (Radier, Tabiques Metalcom, Volcanita RH, Cerámicos, etc.).'
  )

elif modulo == '4. Análisis de Precios Unitarios (APU)':
  st.subheader('💰 Módulo 4: Análisis de Precios Unitarios')

elif modulo == '5. Cierre Económico y Presupuesto':
  st.subheader('📊 Módulo 5: Cotización y Cierre Comercial')

