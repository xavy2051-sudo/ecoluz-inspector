import math
import pandas as pd
import streamlit as st

# ----------------- MÓDULO 4: CONTROL INTERNO Y CUBICACIÓN DE COMPRAS -----------------
elif modulo == "4. Análisis de Precios Unitarios (APU)":
  st.subheader(
      "🛒 Módulo 4: Listado de Compras Reales (Con Merma y Unidades"
      " Comerciales)"
  )
  st.info(
      "💡 Vista de uso exclusivo para el Inspector / Contratista. Modela los"
      " materiales exactos a pedir en bodega/proveedor (redondeados al entero"
      " comercial superior) e incluye el % de merma."
  )

  lista_compras = []

  for rec, items in st.session_state["partidas_recintos"].items():
    for item in items:
      nombre = item["Partida"]
      cant_neta = float(item["Cantidad"])
      precio_total_unit = float(item["Precio Unit."])

      # Definición de reglas comerciales, mermas y formatos de compra
      if "Metalcom" in nombre or "Perfil" in nombre:
        merma = 0.08  # 8% merma en despuntes
        unidad_comercial = "Tiras de 6m"
        # Estimación de tiras de 6m
        cant_comercial = math.ceil((cant_neta * 1.08) / 6.0)
        pu_mat = 13800.0
        pu_mo = 6000.0

      elif "Placa" in nombre or "Internit" in nombre or "Yeso" in nombre:
        merma = 0.10  # 10% merma en cortes de planchas
        unidad_comercial = "Planchas (1.22x2.44m)"
        # 1 plancha = 2.976 m2
        cant_comercial = math.ceil((cant_neta * 1.10) / 2.976)
        pu_mat = precio_total_unit * 0.70
        pu_mo = precio_total_unit * 0.30

      elif "Cerámico" in nombre or "Revestimiento" in nombre:
        merma = 0.10  # 10% merma cerámicos/metalsiding
        unidad_comercial = "m² (Cajas cerradas)"
        cant_comercial = math.ceil(cant_neta * 1.10)
        pu_mat = precio_total_unit * 0.55
        pu_mo = precio_total_unit * 0.45

      elif "Adhesivo" in nombre or "Bekron" in nombre:
        merma = 0.05
        unidad_comercial = "Sacos 25 kg"
        cant_comercial = math.ceil(cant_neta * 1.05)
        pu_mat = precio_total_unit
        pu_mo = 0.0

      else:
        merma = 0.05
        unidad_comercial = "Unidades / Global"
        cant_comercial = math.ceil(cant_neta * 1.05)
        pu_mat = precio_total_unit * 0.60
        pu_mo = precio_total_unit * 0.40

      subtotal_mat = cant_comercial * pu_mat
      subtotal_mo = cant_neta * pu_mo

      lista_compras.append({
          "Especialidad": rec,
          "Material / Partida": nombre,
          "Cant. Neta": cant_neta,
          "% Merma": f"{int(merma*100)}%",
          "Cantidad a Comprar": cant_comercial,
          "Formato Comercial": unidad_comercial,
          "Costo Mat. Un. ($)": pu_mat,
          "Total Material ($)": subtotal_mat,
          "Total M.O. ($)": subtotal_mo,
      })

  if lista_compras:
    df_compras = pd.DataFrame(lista_compras)
    st.dataframe(df_compras, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "📦 Presupuesto Compra Materiales",
        f"$ {df_compras['Total Material ($)'].sum():,.0f}",
    )
    c2.metric(
        "👷 Presupuesto Pago Mano de Obra",
        f"$ {df_compras['Total M.O. ($)'].sum():,.0f}",
    )
    c3.metric(
        "🏗️ Costo Directo Real Obra",
        f"$ {(df_compras['Total Material ($)'].sum() + df_compras['Total M.O. ($)'].sum()):,.0f}",
    )
  else:
    st.warning("No hay partidas configuradas en el Módulo 1.")
