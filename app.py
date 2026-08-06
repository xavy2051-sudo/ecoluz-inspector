import io
import math
import pandas as pd
import streamlit as st

# ReportLab para generación de documentos PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

st.set_page_config(
    page_title="ECOLUZ - Inspector Técnico & APU", layout="wide"
)

st.title("🏗️ ECOLUZ - Cerebro Inspector Técnico & Listado de Ejecución")
st.markdown(
    "Control Interno de Costos (APU), Cubicaciones con Merma, Techumbres,"
    " Barreras Hidrófugas y Presupuestos Dinámicos"
)


# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES DE EXPORTACIÓN (EXCEL Y PDF)
# -----------------------------------------------------------------------------


def generar_excel_presupuesto(df_items, c_directo, gg_util, subtotal, iva, total):
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_items.to_excel(writer, index=False, sheet_name="Cotizacion_Cliente")
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


def generar_pdf_presupuesto(df_items, c_directo, gg_util, subtotal, iva, total):
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer,
      pagesize=letter,
      rightMargin=36,
      leftMargin=36,
      topMargin=36,
      bottomMargin=36,
  )
  elements = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
      "DocTitleClient",
      parent=styles["Heading1"],
      fontSize=18,
      leading=22,
      textColor=colors.HexColor("#1A365D"),
      fontName="Helvetica-Bold",
  )
  subtitle_style = ParagraphStyle(
      "DocSubClient",
      parent=styles["Normal"],
      fontSize=9,
      leading=12,
      textColor=colors.HexColor("#4A5568"),
  )
  cell_style = ParagraphStyle(
      "CellClient",
      parent=styles["Normal"],
      fontSize=8,
      leading=10,
      textColor=colors.HexColor("#2D3748"),
  )
  header_style = ParagraphStyle(
      "HeaderClient",
      parent=styles["Normal"],
      fontSize=8,
      leading=10,
      textColor=colors.white,
      fontName="Helvetica-Bold",
  )

  elements.append(Paragraph("<b>ECOLUZ SpA</b>", title_style))
  elements.append(
      Paragraph(
          "Obras Civiles & Soluciones Constructivas | Concepción, Chile",
          subtitle_style,
      )
  )
  elements.append(Spacer(1, 4))
  elements.append(
      Paragraph(
          "<b>PROPUESTA COMERCIAL Y PRESUPUESTO DE EJECUCIÓN</b>",
          ParagraphStyle(
              "SubC",
              parent=subtitle_style,
              fontSize=11,
              leading=14,
              textColor=colors.HexColor("#2B6CB0"),
              fontName="Helvetica-Bold",
          ),
      )
  )
  elements.append(Spacer(1, 8))
  elements.append(
      HRFlowable(
          width="100%",
          thickness=1.5,
          color=colors.HexColor("#1A365D"),
          spaceAfter=10,
      )
  )

  data_table = [[
      Paragraph("Especialidad", header_style),
      Paragraph("Material / Partida", header_style),
      Paragraph("Cant.", header_style),
      Paragraph("P. Unit ($)", header_style),
      Paragraph("Total Parcial ($)", header_style),
  ]]

  for _, row in df_items.iterrows():
    data_table.append([
        Paragraph(str(row["Especialidad / Recinto"]), cell_style),
        Paragraph(str(row["Material / Insumo"]), cell_style),
        Paragraph(f"{float(row['Cantidad']):.1f}", cell_style),
        Paragraph(f"$ {float(row['Precio Unit. ($)']):,.0f}", cell_style),
        Paragraph(f"$ {float(row['Total Parcial ($)']):,.0f}", cell_style),
    ])

  t = Table(data_table, colWidths=[110, 210, 40, 85, 95])
  t.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
          ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
          (
              "ROWBACKGROUNDS",
              (0, 1),
              (-1, -1),
              [colors.white, colors.HexColor("#F7FAFC")],
          ),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 4),
      ])
  )
  elements.append(t)
  elements.append(Spacer(1, 12))

  resumen_data = [
      [
          Paragraph("Costo Directo Total", cell_style),
          Paragraph(f"$ {c_directo:,.0f}", cell_style),
      ],
      [
          Paragraph("Gastos Generales y Utilidad (25%)", cell_style),
          Paragraph(f"$ {gg_util:,.0f}", cell_style),
      ],
      [
          Paragraph("<b>Subtotal Neto</b>", cell_style),
          Paragraph(f"<b>$ {subtotal:,.0f}</b>", cell_style),
      ],
      [Paragraph("IVA (19%)", cell_style), Paragraph(f"$ {iva:,.0f}", cell_style)],
      [
          Paragraph(
              "<b>TOTAL PRESUPUESTO (CLP)</b>",
              ParagraphStyle(
                  "T1C",
                  parent=cell_style,
                  fontName="Helvetica-Bold",
                  textColor=colors.HexColor("#1A365D"),
              ),
          ),
          Paragraph(
              f"<b>$ {total:,.0f}</b>",
              ParagraphStyle(
                  "T2C",
                  parent=cell_style,
                  fontName="Helvetica-Bold",
                  textColor=colors.HexColor("#1A365D"),
              ),
          ),
      ],
  ]
  resumen_table = Table(resumen_data, colWidths=[340, 200])
  resumen_table.setStyle(
      TableStyle([
          ("ALIGN", (1, 0), (1, -1), "RIGHT"),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
          ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#EDF2F7")),
          ("TOPPADDING", (0, 0), (-1, -1), 4),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
      ])
  )
  elements.append(resumen_table)

  doc.build(elements)
  return buffer.getvalue()


def generar_excel_apu(df_apu):
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_apu.to_excel(writer, index=False, sheet_name="APU_Control_Interno")
  return output.getvalue()


def generar_pdf_apu(df_apu):
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer,
      pagesize=letter,
      rightMargin=20,
      leftMargin=20,
      topMargin=30,
      bottomMargin=30,
  )
  elements = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
      "DocTitleAPU",
      parent=styles["Heading1"],
      fontSize=16,
      leading=20,
      textColor=colors.HexColor("#2C5282"),
      fontName="Helvetica-Bold",
  )
  subtitle_style = ParagraphStyle(
      "DocSubAPU",
      parent=styles["Normal"],
      fontSize=9,
      leading=11,
      textColor=colors.HexColor("#4A5568"),
  )
  cell_style = ParagraphStyle(
      "CellAPU",
      parent=styles["Normal"],
      fontSize=7,
      leading=9,
      textColor=colors.HexColor("#1A202C"),
  )
  header_style = ParagraphStyle(
      "HeaderAPU",
      parent=styles["Normal"],
      fontSize=7,
      leading=9,
      textColor=colors.white,
      fontName="Helvetica-Bold",
  )

  elements.append(Paragraph("<b>ECOLUZ SpA - CONTROL INTERNO DE OBRA</b>", title_style))
  elements.append(
      Paragraph(
          "<b>PLANILLA DE CUBICACIÓN, COMPRAS REALES Y MANO DE OBRA (APU)</b>",
          subtitle_style,
      )
  )
  elements.append(Spacer(1, 6))
  elements.append(
      HRFlowable(
          width="100%",
          thickness=1.5,
          color=colors.HexColor("#2C5282"),
          spaceAfter=8,
      )
  )

  data_table = [[
      Paragraph("Especialidad", header_style),
      Paragraph("Material / Partida", header_style),
      Paragraph("Cant. A Comprar", header_style),
      Paragraph("Formato Comercial", header_style),
      Paragraph("P.U. Mat ($)", header_style),
      Paragraph("Total Mat ($)", header_style),
      Paragraph("Total M.O. ($)", header_style),
  ]]

  for _, row in df_apu.iterrows():
    data_table.append([
        Paragraph(str(row["Especialidad"]), cell_style),
        Paragraph(str(row["Material / Partida"]), cell_style),
        Paragraph(f"{row['Cantidad a Comprar']}", cell_style),
        Paragraph(str(row["Formato Comercial"]), cell_style),
        Paragraph(f"$ {float(row['Costo Mat. Un. ($)']):,.0f}", cell_style),
        Paragraph(f"$ {float(row['Total Material ($)']):,.0f}", cell_style),
        Paragraph(f"$ {float(row['Total M.O. ($)']):,.0f}", cell_style),
    ])

  t = Table(data_table, colWidths=[90, 160, 60, 85, 55, 60, 60])
  t.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C5282")),
          ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
          (
              "ROWBACKGROUNDS",
              (0, 1),
              (-1, -1),
              [colors.white, colors.HexColor("#F7FAFC")],
          ),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
          ("TOPPADDING", (0, 0), (-1, -1), 3),
      ])
  )
  elements.append(t)

  doc.build(elements)
  return buffer.getvalue()


# -----------------------------------------------------------------------------
# MENÚ LATERAL Y ESTADO
# -----------------------------------------------------------------------------
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
    (
        "🧱 Módulo Completo Metalcom (OSB + Metalsiding + Internit + Cerámicos +"
        " Pintura)"
    ),
    (
        "🏠 Techumbre y Cubiertas Completa (Cerchas + OSB Techo + Fieltro/Membrana"
        " + Cubierta + Hojalatería)"
    ),
    "⚡ Electricidad",
    "🎨 Pintura y Cielos",
    "🪵 Carpintería",
    "🧱 Revestimientos Cerámicos y Adhesivos",
    "📐 Terminaciones Finas",
    "🌿 Paisajismo",
    "🔋 Generadores y Equipos",
]


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
              "Bekron Flex (Porcelanato/Sustrato Flexible)",
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

    if st.button("➕ Generar Cuadrilla y Materiales Módulo Completo"):
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

    # Cálculo de superficie real con pendiente
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

    if st.button("➕ Generar Partidas de Techumbre"):
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
    if st.button("➕ Generar Materiales e Integrar a la Cotización"):
      nuevos_items = [{
          "Partida": "Insumos Varios / Partida Estándar (gl)",
          "Cantidad": 1.0,
          "Precio Unit.": 25000.0,
      }]

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
        f"### ✏️ Gestor Interactivo: **{recinto_actual}** (Haz clic en una"
        " celda para modificarla)"
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

# -----------------------------------------------------------------------------
# MÓDULO 2: REGISTRO FOTOGRÁFICO
# -----------------------------------------------------------------------------
elif modulo == "2. Registro Fotográfico y Planos":
  st.subheader("📸 Módulo 2: Registro Fotográfico e Inspección")
  recinto_m2 = st.selectbox(
      "Seleccionar Recinto a Inspeccionar", lista_recintos_especialidades
  )
  st.file_uploader("Subir Plano / Esquema Técnico", type=["png", "jpg", "pdf"])
  st.file_uploader(
      "Subir Fotografías de Avance",
      type=["png", "jpg"],
      accept_multiple_files=True,
  )

# -----------------------------------------------------------------------------
# MÓDULO 3: ESPECIFICACIONES TÉCNICAS
# -----------------------------------------------------------------------------
elif modulo == "3. Especificaciones Técnicas Detalladas (E.T.)":
  st.subheader("📄 ESPECIFICACIONES TÉCNICAS DINÁMICAS Y DETALLADAS (E.T.)")
  st.markdown("---")
  if st.session_state["partidas_recintos"]:
    texto_et_exportar = ""
    for recinto, items in st.session_state["partidas_recintos"].items():
      if items:
        st.markdown(f"### 📌 ESPECIALIDAD / SECTOR: {recinto}")
        texto_et_exportar += f"ESPECIALIDAD / SECTOR: {recinto}\n"
        for idx, item in enumerate(items, 1):
          st.markdown(
              f"  **{idx}. {item['Partida']}** - Cantidad: `{item['Cantidad']}`"
          )
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

# -----------------------------------------------------------------------------
# MÓDULO 4: APU Y AJUSTE DE PRECIOS EN TIEMPO REAL
# -----------------------------------------------------------------------------
elif modulo == "4. Análisis de Precios Unitarios (APU)":
  st.subheader(
      "🛒 Módulo 4: Listado de Compras y APU (Ajuste de Precios Editable +"
      " Exportación)"
  )
  st.info(
      "💡 Puedes modificar individualmente cada celda de precio/costo o bien"
      " usar el selector superior de **Ajuste Global (%)** para simular"
      " imprevistos o reajuste de precios de mercado."
  )

  col_a1, col_a2 = st.columns([1, 2])
  with col_a1:
    ajuste_global_apu = st.number_input(
        "Ajuste Global de Precios (%):", value=0.0, step=1.0
    )

  factor_ajuste = 1.0 + (ajuste_global_apu / 100.0)

  lista_compras = []

  for rec, items in st.session_state["partidas_recintos"].items():
    for item in items:
      nombre = item["Partida"]
      cant_neta = float(item["Cantidad"])
      precio_total_unit = float(item["Precio Unit."]) * factor_ajuste

      if "Metalcom" in nombre or "Perfil" in nombre or "Cerchas" in nombre:
        unidad_comercial = "Tiras de 6m / Perfiles"
        cant_comercial = math.ceil((cant_neta * 1.08) / 6.0)
        pu_mat = 13800.0 * factor_ajuste
        pu_mo = 6000.0 * factor_ajuste

      elif (
          "Placa" in nombre
          or "Internit" in nombre
          or "Yeso" in nombre
          or "Membrana" in nombre
          or "Fieltro" in nombre
          or "OSB" in nombre
      ):
        unidad_comercial = "Planchas / Rollos"
        cant_comercial = math.ceil(cant_neta * 1.10)
        pu_mat = round(precio_total_unit * 0.70)
        pu_mo = round(precio_total_unit * 0.30)

      elif (
          "Teja" in nombre or "Zinc" in nombre or "Cubierta" in nombre
      ):
        unidad_comercial = "m² / Planchas / Paquetes"
        cant_comercial = math.ceil(cant_neta * 1.08)
        pu_mat = round(precio_total_unit * 0.65)
        pu_mo = round(precio_total_unit * 0.35)

      elif (
          "Canaleta" in nombre
          or "Bajada" in nombre
          or "Caballete" in nombre
      ):
        unidad_comercial = "Tiras 3m / Metros Líneales"
        cant_comercial = math.ceil(cant_neta * 1.05)
        pu_mat = round(precio_total_unit * 0.60)
        pu_mo = round(precio_total_unit * 0.40)

      elif "Cerámico" in nombre or "Revestimiento" in nombre:
        unidad_comercial = "m² (Cajas)"
        cant_comercial = math.ceil(cant_neta * 1.10)
        pu_mat = round(precio_total_unit * 0.55)
        pu_mo = round(precio_total_unit * 0.45)

      elif "Adhesivo" in nombre or "Bekron" in nombre:
        unidad_comercial = "Sacos 25 kg"
        cant_comercial = math.ceil(cant_neta * 1.05)
        pu_mat = precio_total_unit
        pu_mo = 0.0

      else:
        unidad_comercial = "Unidades / Global"
        cant_comercial = math.ceil(cant_neta * 1.05)
        pu_mat = round(precio_total_unit * 0.60)
        pu_mo = round(precio_total_unit * 0.40)

      subtotal_mat = cant_comercial * pu_mat
      subtotal_mo = cant_neta * pu_mo

      lista_compras.append({
          "Especialidad": rec,
          "Material / Partida": nombre,
          "Cantidad a Comprar": cant_comercial,
          "Formato Comercial": unidad_comercial,
          "Costo Mat. Un. ($)": pu_mat,
          "Total Material ($)": subtotal_mat,
          "Total M.O. ($)": subtotal_mo,
      })

  if lista_compras:
    df_base_apu = pd.DataFrame(lista_compras)

    st.markdown(
        "### ✏️ Tabla APU Interactiva (Edita directamente cualquier valor de la"
        " celda)"
    )
    df_apu_editado = st.data_editor(
        df_base_apu,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_apu_modulo4",
    )

    df_apu_editado["Total Material ($)"] = (
        df_apu_editado["Cantidad a Comprar"] * df_apu_editado["Costo Mat. Un. ($)"]
    )
    tot_mat = df_apu_editado["Total Material ($)"].sum()
    tot_mo = df_apu_editado["Total M.O. ($)"].sum()
    tot_directo = tot_mat + tot_mo

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Presupuesto Compra Materiales", f"$ {tot_mat:,.0f}")
    c2.metric("👷 Presupuesto Pago Mano de Obra", f"$ {tot_mo:,.0f}")
    c3.metric("🏗️ Costo Directo Real Obra", f"$ {tot_directo:,.0f}")

    st.markdown("---")
    col_apu1, col_apu2 = st.columns(2)

    with col_apu1:
      excel_apu_bytes = generar_excel_apu(df_apu_editado)
      st.download_button(
          label="📊 Descargar Excel Control Interno APU (.xlsx)",
          data=excel_apu_bytes,
          file_name="APU_Control_Interno_ECOLUZ.xlsx",
          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          use_container_width=True,
      )

    with col_apu2:
      pdf_apu_bytes = generar_pdf_apu(df_apu_editado)
      st.download_button(
          label="📄 Descargar PDF Control Interno APU (.pdf)",
          data=pdf_apu_bytes,
          file_name="APU_Control_Interno_ECOLUZ.pdf",
          mime="application/pdf",
          use_container_width=True,
      )

  else:
    st.warning(
        "No hay partidas configuradas en el Módulo 1. Configura una"
        " especialidad primero."
    )

# -----------------------------------------------------------------------------
# MÓDULO 5: CIERRE ECONÓMICO Y AJUSTE DE COTIZACIÓN AL CLIENTE
# -----------------------------------------------------------------------------
elif modulo == "5. Cierre Económico y Presupuesto":
  st.subheader("📊 Módulo 5: Propuesta Comercial para Entrega al Cliente")

  col_c1, col_c2 = st.columns([1, 2])
  with col_c1:
    ajuste_global_cli = st.number_input(
        "Ajuste / Descuento Global Cliente (%):", value=0.0, step=1.0
    )

  factor_cli = 1.0 + (ajuste_global_cli / 100.0)

  todos = []
  for rec, items in st.session_state["partidas_recintos"].items():
    for item in items:
      f = dict(item).copy()
      f["Especialidad / Recinto"] = rec
      f["Precio Unit."] = float(f["Precio Unit."]) * factor_cli
      f["Costo Total"] = float(f["Cantidad"]) * f["Precio Unit."]
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

    st.markdown(
        "### ✏️ Cotización Cliente Editable (Modifica precios o cantidades"
        " libremente)"
    )

    df_cliente_editado = st.data_editor(
        df_cliente,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_cliente_modulo5",
    )

    df_cliente_editado["Total Parcial ($)"] = (
        df_cliente_editado["Cantidad"] * df_cliente_editado["Precio Unit. ($)"]
    )

    costo_directo = df_cliente_editado["Total Parcial ($)"].sum()
    gg_util = costo_directo * 0.25
    subtotal = costo_directo + gg_util
    iva = subtotal * 0.19
    total = subtotal + iva

    st.markdown("---")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
      st.markdown(f"- **Costo Directo:** 💲 `{costo_directo:,.0f}`")
      st.markdown(f"- **GG & Utilidad (25%):** 💲 `{gg_util:,.0f}`")
      st.markdown(f"- **Subtotal Neto:** 💲 `{subtotal:,.0f}`")
      st.markdown(f"- **IVA (19%):** 💲 `{iva:,.0f}`")
    with col_r2:
      st.markdown(f"### 💰 **TOTAL PROPUESTA CLIENTE:** 💲 `{total:,.0f}`")

    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
      excel_bytes = generar_excel_presupuesto(
          df_cliente_editado, costo_directo, gg_util, subtotal, iva, total
      )
      st.download_button(
          label="📊 Descargar Excel Cliente (.xlsx)",
          data=excel_bytes,
          file_name="Presupuesto_Comercial_ECOLUZ.xlsx",
          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          use_container_width=True,
      )

    with col_btn2:
      pdf_bytes = generar_pdf_presupuesto(
          df_cliente_editado, costo_directo, gg_util, subtotal, iva, total
      )
      st.download_button(
          label="📄 Descargar PDF Formal Cliente (.pdf)",
          data=pdf_bytes,
          file_name="Presupuesto_Comercial_ECOLUZ.pdf",
          mime="application/pdf",
          use_container_width=True,
      )
  else:
    st.warning(
        "No hay partidas configuradas en el Módulo 1. Agrega ítems para poder"
        " generar la cotización."
    )
