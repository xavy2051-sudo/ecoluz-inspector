import pandas as pd
import streamlit as st

# Inicializar la estructura de partidas por recinto en el session_state
if 'partidas_recintos' not in st.session_state:
  st.session_state['partidas_recintos'] = (
      {}
  )  # Formato: {recinto: [ {partida, cant, unidad, p_unit}, ... ]}

st.subheader('🛠️ Asignación de Partidas y Materiales (Desde SQLite)')

# Selector de recinto activo
recinto_actual = st.selectbox(
    'Seleccionar Recinto para Asignar Partidas',
    [
        'Baño Principal',
        'Cocina',
        'Dormitorio Principal',
        'Estar-Comedor',
        'Pasillo',
        'Exterior',
    ],
)

col_p1, col_p2, col_p3 = st.columns([2, 1, 1])

with col_p1:
  # Lista de partidas típicas (puedes enlazarlo con tu base de datos SQLite)
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
  cant_sugerida = 1.0  # Aquí puedes enlazar la superficie calculada si corresponde (ej: m2 de muros o piso)
  cantidad_ingresada = st.number_input(
      'Cantidad / Rendimiento', min_value=0.01, value=cant_sugerida, step=0.1
  )

with col_p3:
  precio_unitario_sugerido = 12500  # Precio base de SQLite
  precio_ingresado = st.number_input(
      'Precio Unitario ($)',
      min_value=0.0,
      value=float(precio_unitario_sugerido),
      step=500.0,
  )

# Botón para acumular la partida
if st.button('➕ Agregar Partida al Resumen del Recinto'):
  if recinto_actual not in st.session_state['partidas_recintos']:
    st.session_state['partidas_recintos'][recinto_actual] = []

  # Agregar la nueva partida a la lista del recinto
  st.session_state['partidas_recintos'][recinto_actual].append({
      'Partida': partida_seleccionada,
      'Cantidad': cantidad_ingresada,
      'Precio Unit.': precio_ingresado,
      'Costo Total': cantidad_ingresada * precio_ingresado,
  })
  st.success(f'Partida agregada exitosamente a **{recinto_actual}**.')

# Mostrar la tabla acumulada de partidas para el recinto seleccionado
st.markdown(f'### 📋 Desglose Técnico y Económico: {recinto_actual}')

if (
    recinto_actual in st.session_state['partidas_recintos']
    and st.session_state['partidas_recintos'][recinto_actual]
):
  df_partidas = pd.DataFrame(
      st.session_state['partidas_recintos'][recinto_actual]
  )
  st.dataframe(df_partidas, use_container_width=True)

  # Botón para limpiar o eliminar ítems si es necesario
  if st.button('🗑️ Limpiar partidas de este recinto'):
    st.session_state['partidas_recintos'][recinto_actual] = []
    st.rerun()
else:
  st.info(
      f'Aún no hay partidas asignadas para {recinto_actual}. Selecciona y'
      ' agrega los materiales arriba.'
  )
        )
