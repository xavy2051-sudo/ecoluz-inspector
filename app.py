# app.py
# ==============================================================================
# SISTEMA ECOLUZ - INSPECTOR TÉCNICO DE OBRA Y MOTOR DE CUBICACIÓN APU
# ==============================================================================

import io
import json
import sqlite3
from biblioteca_tecnica import (
    CONFIGURACION_PARTIDAS,
    calcular_cubicacion_y_apu,
    get_connection,
    inicializar_fase1_db,
)
import pandas as pd
import streamlit as st

# Configuración de página Streamlit
st.set_page_config(
    page_title="ECOLUZ - Inspector Técnico de Obra",
    page_icon="🏗️",
    layout="wide",
)

# Inicializar Base de Datos Relacional
inicializar_fase1_db()

# Encabezado Principal
st.title("🏗️ ECOLUZ — Inspector Técnico y Cubicador APU")
st.caption(
    "Plataforma Integrada de Inspección en Terreno, Cubicaciones, Presupuesto y"
    " Auditoría RIC/SEC"
)

# Sidebar: Configuración de Proyecto y Navegación
st.sidebar.header("⚙️ Configuración de Trabajo")

if "proyecto_activo" not in st.session_state:
  st.session_state["proyecto_activo"] = "PROY-001"

proyecto_id_activo = st.sidebar.text_input(
    "ID del Proyecto Activo:", value=st.session_state["proyecto_activo"]
)
st.session_state["proyecto_activo"] = proyecto_id_activo

st.sidebar.markdown("---")

modulo = st.sidebar.radio(
    "Selecciona el Módulo:",
    [
        "📁 1. Gestión de Proyectos",
        "📋 2. Levantamiento e Inspección en Terreno",
        "🔍 3. Motor de Auditoría y Alertas RIC/SEC",
        "💰 4. Presupuesto Consolidado y APU Total",
        "📊 5. Reportes y Exportación",
    ],
)


# ==============================================================================
# MÓDULO 1: GESTIÓN DE PROYECTOS
# ==============================================================================
if modulo == "📁 1. Gestión de Proyectos":
  st.header("📁 Gestión de Proyectos e Inspecciones")
  st.write(f"**Proyecto Activo:** `{proyecto_id_activo}`")

  conn = get_connection()
  df_recintos = pd.read_sql_query(
      """
        SELECT id, nombre_recinto, elemento_constructivo, estado_diagnostico, fecha_registro 
        FROM recintos_levantamiento 
        WHERE proyecto_id = ? 
        ORDER BY fecha_registro DESC
    """,
      conn,
      params=(proyecto_id_activo,),
  )
  conn.close()

  st.metric("Total Inspecciones Registradas", len(df_recintos))

  if not df_recintos.empty:
    st.dataframe(df_recintos, use_container_width=True)
  else:
    st.info(
        "No hay registros guardados para este proyecto. Pasa al Módulo 2 para"
        " iniciar el levantamiento."
    )


# ==============================================================================
# MÓDULO 2: LEVANTAMIENTO E INSPECCIÓN EN TERRENO
# ==============================================================================
elif modulo == "📋 2. Levantamiento e Inspección en Terreno":
  st.header("📋 Inspección y Cubicación por Recinto")

  col1, col2 = st.columns(2)
  with col1:
    recinto = st.text_input("Nombre del Recinto:", "Baño Principal")
  with col2:
    partida = st.selectbox(
        "Selecciona Partida / Especialidad:", list(CONFIGURACION_PARTIDAS.keys())
    )

  st.markdown("---")
  st.subheader(f"⚙️ Configuración Técnica: {partida}")

  config_partida = CONFIGURACION_PARTIDAS[partida]
  respuestas = {}

  # Generación dinámicas de inputs
  for preg in config_partida["preguntas"]:
    cid = preg["campo_id"]
    label = preg["etiqueta"]
    tipo = preg["tipo_input"]

    if tipo == "number":
      respuestas[cid] = st.number_input(
          label,
          value=float(preg["valor_default"]),
          step=float(preg.get("step_val", 0.1)),
      )
    elif tipo == "select":
      respuestas[cid] = st.selectbox(label, preg["opciones"])

  st.markdown("---")
  col_obs1, col_obs2 = st.columns(2)
  with col_obs1:
    estado_diag = st.selectbox(
        "Estado / Diagnóstico ITO:",
        ["Aceptado", "Observado / Rechazado", "Pendiente de Ejecución"],
    )
  with col_obs2:
    patologia = st.text_area(
        "Observaciones / Patología Detectada:", "Sin observaciones técnicas."
    )

  # Cálculo instantáneo de APU
  resultado_calc = calcular_cubicacion_y_apu(partida, respuestas)
  apu = resultado_calc["apu"]
  mat = resultado_calc["materiales"]

  st.subheader("📊 Resultado Estimado de la Partida")
  c_m1, c_m2, c_m3 = st.columns(3)
  c_m1.metric("Costo Materiales", f"${apu['costo_materiales_clp']:,} CLP")
  c_m2.metric("Costo Mano de Obra", f"${apu['costo_mano_obra_clp']:,} CLP")
  c_m3.metric(
      "Total Directo Partida", f"${apu['costo_directo_total_clp']:,} CLP"
  )

  if st.button("💾 Guardar Inspección y Cubicación en BD", type="primary"):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO recintos_levantamiento 
        (proyecto_id, nombre_recinto, elemento_constructivo, estado_diagnostico, patologia_observada, datos_tecnicos_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            proyecto_id_activo,
            recinto,
            partida,
            estado_diag,
            patologia,
            json.dumps(respuestas, ensure_ascii=False),
        ),
    )
    conn.commit()
    conn.close()
    st.success(
        f"✅ Inspección registrada exitosamente para `{recinto}` en la partida"
        f" `{partida}`."
    )


# ==============================================================================
# MÓDULO 3: MOTOR DE AUDITORÍA Y ALERTAS RIC / SEC / NCH
# ==============================================================================
elif modulo == "🔍 3. Motor de Auditoría y Alertas RIC/SEC":
  st.header("🔍 Motor de Auditoría Técnica y Cumplimiento Normativo")
  st.caption(
      "Evaluación automática de registros según normativa SEC (RIC N°10) y NCh"
      " de edificación."
  )

  conn = get_connection()
  query = """
        SELECT r.id, r.nombre_recinto, r.elemento_constructivo, r.estado_diagnostico, 
               r.patologia_observada, r.datos_tecnicos_json, r.fecha_registro
        FROM recintos_levantamiento r
        WHERE r.proyecto_id = ?
    """
  inspecciones_df = pd.read_sql_query(query, conn, params=(proyecto_id_activo,))
  conn.close()

  if inspecciones_df.empty:
    st.warning(
        "No se han registrado inspecciones para este proyecto. Dirígete al"
        " Módulo 2 para agregar levantamientos."
    )
  else:
    alertas_criticas = []
    advertencias = []
    conformes = []

    for _, row in inspecciones_df.iterrows():
      recinto = row["nombre_recinto"]
      partida = row["elemento_constructivo"]
      datos = (
          json.loads(row["datos_tecnicos_json"])
          if row["datos_tecnicos_json"]
          else {}
      )
      es_zona_humeda = any(
          z in recinto.lower() for z in ["baño", "cocina", "logia"]
      )

      # REGLA 1: RIC N°10 - Electricidad en Zonas Húmedas sin Diferencial
      if partida == "Electricidad - Enchufes":
        proteccion = datos.get("proteccion", "")
        if "Diferencial" not in proteccion and es_zona_humeda:
          alertas_criticas.append({
              "recinto": recinto,
              "norma": "RIC N°10 (SEC) - Protección Eléctrica",
              "detalle": (
                  f"El circuito de enchufes en {recinto} no contempla"
                  " Interruptor Diferencial de 30mA."
              ),
              "accion": (
                  "Obligatorio instalar protector diferencial 2x25A 30mA por"
                  " seguridad de las personas."
              ),
          })
        else:
          conformes.append(
              f"{recinto} - Enchufes: Protección eléctrica conforme a RIC N°10."
          )

      # REGLA 2: NCh 2450 / Volcanita ST en Zonas Húmedas
      if (
          partida in ["Tabiquería / Muros", "Cielo / Cielo Falso"]
          and es_zona_humeda
      ):
        placa_muro = datos.get("placa_interior", "")
        placa_cielo = datos.get("tipo_placa_cielo", "")
        if "ST" in placa_muro or "ST" in placa_cielo:
          alertas_criticas.append({
              "recinto": recinto,
              "norma": "NCh 2450 / EETT Revestimientos",
              "detalle": f"Se seleccionó placa tipo ST (Standard) en {recinto}.",
              "accion": (
                  "Sustituir por Placa RH (Resistente a la Humedad) de 12.5mm"
                  " para evitar disgregación por humedad."
              ),
          })
        else:
          conformes.append(
              f"{recinto} - {partida}: Uso de placa RH verificado"
              " correctamente."
          )

      # REGLA 3: Pinturas no resistentes en Baños/Cocinas
      if partida == "Pintura / Empaste" and es_zona_humeda:
        tipo_p = datos.get("tipo_pintura", "")
        if "Látex" in tipo_p:
          advertencias.append({
              "recinto": recinto,
              "norma": "Buenas Prácticas de Terminaciones / ITO",
              "detalle": f"Uso de Látex Vinílico en {recinto}.",
              "accion": (
                  "Se recomienda cambiar a Esmalte al Agua RH para prevenir"
                  " proliferación de hongos por vapor."
              ),
          })

    col_a1, col_a2, col_a3 = st.columns(3)
    col_a1.metric("🔴 Incumplimientos Normativos", len(alertas_criticas))
    col_a2.metric("🟠 Advertencias de Calidad", len(advertencias))
    col_a3.metric("🟢 Verificaciones Conformes", len(conformes))

    st.markdown("---")

    if alertas_criticas:
      st.subheader("🔴 Alertas Críticas de Cumplimiento (Acción Inmediata)")
      for alt in alertas_criticas:
        with st.expander(f"⚠️ {alt['norma']} — {alt['recinto']}", expanded=True):
          st.error(f"**Hallazgo:** {alt['detalle']}")
          st.info(f"**Instrucción ITO:** {alt['accion']}")

    if advertencias:
      st.subheader("🟠 Advertencias y Observaciones Técnicas")
      for adv in advertencias:
        with st.expander(f"⚡ {adv['norma']} — {adv['recinto']}"):
          st.warning(f"**Hallazgo:** {adv['detalle']}")
          st.caption(f"**Recomendación:** {adv['accion']}")

    if conformes:
      st.subheader("🟢 Partidas Auditadas y Validadas")
      for conf in conformes:
        st.success(conf)


# ==============================================================================
# MÓDULO 4: PRESUPUESTO CONSOLIDADO Y APU TOTAL
# ==============================================================================
elif modulo == "💰 4. Presupuesto Consolidado y APU Total":
  st.header("💰 Presupuesto Consolidado del Proyecto")
  st.caption(
      "Resumen financiero y lista consolidada de compras para"
      f" `{proyecto_id_activo}`"
  )

  conn = get_connection()
  df_insp = pd.read_sql_query(
      """
        SELECT id, nombre_recinto, elemento_constructivo, datos_tecnicos_json 
        FROM recintos_levantamiento 
        WHERE proyecto_id = ?
    """,
      conn,
      params=(proyecto_id_activo,),
  )
  conn.close()

  if df_insp.empty:
    st.warning(
        "No hay partidas registradas para calcular el presupuesto consolidado."
    )
  else:
    totales_por_partida = []
    materiales_consolidados = {}
    costo_total_mat = 0
    costo_total_mo = 0
    hh_totales = 0.0

    for _, row in df_insp.iterrows():
      recinto = row["nombre_recinto"]
      partida = row["elemento_constructivo"]
      datos = (
          json.loads(row["datos_tecnicos_json"])
          if row["datos_tecnicos_json"]
          else {}
      )

      res = calcular_cubicacion_y_apu(partida, datos)
      apu = res["apu"]
      mats = res["materiales"]

      costo_total_mat += apu["costo_materiales_clp"]
      costo_total_mo += apu["costo_mano_obra_clp"]
      hh_totales += apu["hh_mano_obra"]

      totales_por_partida.append({
          "Recinto": recinto,
          "Partida": partida,
          "Materiales (CLP)": apu["costo_materiales_clp"],
          "Mano de Obra (CLP)": apu["costo_mano_obra_clp"],
          "HH Estimadas": apu["hh_mano_obra"],
          "Costo Directo (CLP)": apu["costo_directo_total_clp"],
      })

      # Agrupar materiales por tipo e insumo
      for m in mats:
        key = (m["insumo"], m["unidad"], m["precio_unit_clp"])
        if key not in materiales_consolidados:
          materiales_consolidados[key] = 0
        materiales_consolidados[key] += m["cantidad"]

    total_general = costo_total_mat + costo_total_mo

    # Indicadores Financieros Globales
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Materiales", f"${costo_total_mat:,} CLP")
    m2.metric("Total Mano de Obra", f"${costo_total_mo:,} CLP")
    m3.metric("Horas Hombre (HH)", f"{hh_totales:.1f} HH")
    m4.metric("Costo Directo Total", f"${total_general:,} CLP")

    st.markdown("---")
    st.subheader("📌 Desglose Presupuestario por Recinto y Partida")
    df_presupuesto = pd.DataFrame(totales_por_partida)
    st.dataframe(
        df_presupuesto.style.format({
            "Materiales (CLP)": "${:,.0f}",
            "Mano de Obra (CLP)": "${:,.0f}",
            "Costo Directo (CLP)": "${:,.0f}",
            "HH Estimadas": "{:.2f}",
        }),
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader("🛒 Lista Consolidada de Compras (Insumos Totales)")
    lista_compras = []
    for (insumo, unidad, precio), cant in materiales_consolidados.items():
      subtotal = cant * precio
      lista_compras.append({
          "Insumo / Material": insumo,
          "Cantidad Requerida": cant,
          "Unidad": unidad,
          "Precio Unitario (CLP)": precio,
          "Subtotal Insumo (CLP)": subtotal,
      })

    df_compras = pd.DataFrame(lista_compras)
    st.dataframe(
        df_compras.style.format({
            "Precio Unitario (CLP)": "${:,.0f}",
            "Subtotal Insumo (CLP)": "${:,.0f}",
        }),
        use_container_width=True,
    )


# ==============================================================================
# MÓDULO 5: REPORTES Y EXPORTACIÓN
# ==============================================================================
elif modulo == "📊 5. Reportes y Exportación":
  st.header("📊 Exportación de Informes y Datos Técnicos")
  st.caption(
      f"Generación de archivos descargables para el proyecto `{proyecto_id_activo}`"
  )

  conn = get_connection()
  df_completo = pd.read_sql_query(
      """
        SELECT id, proyecto_id, nombre_recinto, elemento_constructivo, estado_diagnostico, 
               patologia_observada, datos_tecnicos_json, fecha_registro 
        FROM recintos_levantamiento 
        WHERE proyecto_id = ?
    """,
      conn,
      params=(proyecto_id_activo,),
  )
  conn.close()

  if df_completo.empty:
    st.warning("No existen datos registrados para exportar.")
  else:
    st.subheader("📄 Resumen de Registros de Inspección")
    st.dataframe(df_completo, use_container_width=True)

    st.markdown("---")
    st.subheader("📥 Centros de Descarga")

    col_d1, col_d2 = st.columns(2)

    # Exportar CSV de Inspecciones en Terreno
    buffer_csv = io.StringIO()
    df_completo.to_csv(buffer_csv, index=False)
    col_d1.download_button(
        label="⬇️ Descargar Registro de Inspecciones (CSV)",
        data=buffer_csv.getvalue(),
        file_name=f"Inspecciones_{proyecto_id_activo}.csv",
        mime="text/csv",
    )

    # Exportar Presupuesto y APU Consolidado
    filas_presupuesto = []
    for _, r in df_completo.iterrows():
      datos = (
          json.loads(r["datos_tecnicos_json"]) if r["datos_tecnicos_json"] else {}
      )
      res = calcular_cubicacion_y_apu(r["elemento_constructivo"], datos)
      filas_presupuesto.append({
          "Proyecto": r["proyecto_id"],
          "Recinto": r["nombre_recinto"],
          "Partida": r["elemento_constructivo"],
          "Estado ITO": r["estado_diagnostico"],
          "Costo Materiales CLP": res["apu"]["costo_materiales_clp"],
          "Costo Mano Obra CLP": res["apu"]["costo_mano_obra_clp"],
          "HH Estimadas": res["apu"]["hh_mano_obra"],
          "Costo Directo CLP": res["apu"]["costo_directo_total_clp"],
      })

    df_exp_presupuesto = pd.DataFrame(filas_presupuesto)
    buffer_csv_presupuesto = io.StringIO()
    df_exp_presupuesto.to_csv(buffer_csv_presupuesto, index=False)

    col_d2.download_button(
        label="⬇️ Descargar Presupuesto y APU Consolidado (CSV)",
        data=buffer_csv_presupuesto.getvalue(),
        file_name=f"Presupuesto_APU_{proyecto_id_activo}.csv",
        mime="text/csv",
    )

    st.success(
        "🎉 Sistema ECOLUZ 100% operativo y listo para uso profesional en"
        " terreno."
    )
