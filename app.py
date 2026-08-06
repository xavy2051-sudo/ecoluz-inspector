import streamlit as st
import pandas as pd
from database.db_manager import init_db
from core.dependency_engine import MaterialDependencyEngine
from core.audit_engine import AuditEngine

# Configuración inicial de la página
st.set_page_config(page_title="ECOLUZ v2.0 - Inspector Técnico", layout="wide", page_icon="🏗️")

# Inicializar Base de Datos
init_db()

st.title("🏗️ ECOLUZ v2.0 — Inspector Técnico Profesional")
st.caption("Sistema de Inspección, Cubicaciones y Presupuestos | Normativa Chilena")

# Sidebar de Navegación
opcion = st.sidebar.radio("Navegación / Módulos:", [
    "1. Levantamiento y Factibilidad",
    "2. Motor de Cubicaciones y Kits",
    "3. Auditoría Pre-Cotización",
    "4. APU e Historial de Versiones"
])

if opcion == "1. Levantamiento y Factibilidad":
    st.header("📋 Factibilidad Técnica de la Obra")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Edificación y Terreno (DOM)")
        st.checkbox("¿Terreno cuenta con Rol propio?")
        st.checkbox("¿Cuenta con Permiso de Edificación?")
        st.checkbox("¿Requiere Cálculo Estructural?")
    with col2:
        st.subheader("Servicios Eléctricos (SEC)")
        st.selectbox("Tipo de Empalme Existente:", ["Monofásico (1Ф)", "Trifásico (3Ф)", "Sin Empalme"])
        st.checkbox("¿Cuenta con Puesta a Tierra y Tablero?")

elif opcion == "2. Motor de Cubicaciones y Kits":
    st.header("📦 Cálculo Automático de Insumos (BOM)")
    partida = st.selectbox("Seleccione Partida Principal:", ["Cerámica / Porcelanato", "Estructura Metalcom", "Volcanita / Placa Yeso-Cartón"])
    m2 = st.number_input("Superficie a ejecutar (m²):", min_value=1.0, value=20.0)
    
    if st.button("Calcular Kit Completo de Materiales"):
        insumos = MaterialDependencyEngine.obtener_kit_dependiente(partida, m2)
        df = pd.DataFrame(insumos)
        st.success(f"Kit de insumos generado automáticamente para {m2} m² de {partida}:")
        st.dataframe(df, use_container_width=True)

elif opcion == "3. Auditoría Pre-Cotización":
    st.header("🔍 Audit e Inspección Técnica")
    
    # Ejemplo de prueba de auditoría
    datos_ejemplo = {
        "permiso_dom": True,
        "factibilidad_sec": False,
        "zona": "Baño / Zona Húmeda",
        "placa": "Volcanita ST Standard"
    }
    
    completitud, semaforo, alertas = AuditEngine.auditar_proyecto(datos_ejemplo)
    
    col_a, col_b = st.columns(2)
    col_a.metric("Completitud del Levantamiento", f"{completitud}%")
    col_b.metric("Semáforo del Proyecto", semaforo)
    
    st.subheader("Observaciones y Alertas Normativas:")
    for alerta in alertas:
        st.warning(alerta)
