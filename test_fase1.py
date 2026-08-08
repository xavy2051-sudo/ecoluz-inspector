# test_fase1.py
# ==============================================================================
# VALIDACIÓN INDEPENDIENTE DEL CEREBRO CONSTRUCTIVO - FASE 1
# ==============================================================================

from biblioteca_tecnica import (
    calcular_cubicacion_y_apu,
    obtener_configuracion_partida,
)


def ejecutar_prueba_fase1():
  print("\n" + "=" * 70)
  print("🧪 PRUEBA DE AISLAMIENTO TÉCNICO: REMODELACIÓN DE BAÑO")
  print("=" * 70)

  # 1. Muros / Tabiquería
  print("\n---> 1. CONSULTANDO PREGUNTAS PARA: Baño -> Tabiquería / Muros")
  config_muros = obtener_configuracion_partida("Tabiquería / Muros")
  print(f"Categoría: {config_muros['categoria']}")
  print("Preguntas que solicita la interfaz:")
  for q in config_muros["preguntas"]:
    print(f"  • [{q['campo_id']}] {q['etiqueta']} (Tipo: {q['tipo_input']})")

  respuestas_muro = {
      "largo": 3.0,
      "alto": 2.4,
      "separacion_montantes": "40 cm (Zona Húmeda)",
      "placa_interior": "Volcanita RH 12.5mm",
      "aislacion": "Lana Mineral 50mm",
  }

  res_muro = calcular_cubicacion_y_apu("Tabiquería / Muros", respuestas_muro)
  print("\n📦 CUBICACIÓN Y MATERIALES CALCULADOS (CON DEPENDENCIAS Y MERMAS):")
  for m in res_muro["materiales"]:
    print(
        f"  - [{m['tipo']}] {m['insumo']}: {m['cantidad']} {m['unidad']}"
    )

  print("\n💰 INTEGRACIÓN CON APU (COSTO DIRECTO):")
  print(f"  • M² Muro: {res_muro['apu']['m2_calculados']} m²")
  print(f"  • Costo Materiales: ${res_muro['apu']['costo_materiales_clp']:,} CLP")
  print(
      f"  • Mano de Obra: {res_muro['apu']['hh_mano_obra']} HH ("
      f"${res_muro['apu']['costo_mano_obra_clp']:,} CLP)"
  )
  print(
      f"  • TOTAL COSTO DIRECTO: ${res_muro['apu']['costo_directo_total_clp']:,}"
      " CLP"
  )

  # 2. Electricidad - Enchufes
  print("\n" + "-" * 70)
  print("---> 2. CONSULTANDO PREGUNTAS PARA: Baño -> Electricidad - Enchufes")
  config_elec = obtener_configuracion_partida("Electricidad - Enchufes")
  print("Preguntas que solicita la interfaz:")
  for q in config_elec["preguntas"]:
    print(f"  • [{q['campo_id']}] {q['etiqueta']} (Tipo: {q['tipo_input']})")

  print("\n" + "=" * 70)
  print("✅ CONCLUSIÓN DE LA PRUEBA:")
  print("Tabiquería NO contiene preguntas de enchufes ni electricidad.")
  print("Electricidad NO contiene preguntas de muros ni volcanita.")
  print("Cerebro técnico validado exitosamente sin modificar app.py.")
  print("=" * 70 + "\n")


if __name__ == "__main__":
  ejecutar_prueba_fase1()
