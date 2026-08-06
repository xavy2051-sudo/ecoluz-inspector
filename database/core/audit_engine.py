class AuditEngine:
    @staticmethod
    def auditar_proyecto(datos_levantamiento):
        alertas = []
        campos_requeridos = [
            "permiso_dom", "factibilidad_sec", "tipo_aislacion", 
            "espesor_metalcom", "color_frague", "pendiente_piso"
        ]
        
        completados = sum(1 for campo in campos_requeridos if datos_levantamiento.get(campo))
        porcentaje_completitud = int((completados / len(campos_requeridos)) * 100)
        
        # Validaciones de Incompatibilidad Técnica y Normativa (OGUC / SEC)
        if datos_levantamiento.get("zona") == "Baño / Zona Húmeda" and datos_levantamiento.get("placa") == "Volcanita ST Standard":
            alertas.append("🔴 ALERTA NORMATIVA: En zonas húmedas debe usarse Volcanita RH (Resistente a Humedad) según OGUC.")
            
        if datos_levantamiento.get("partida") == "Cerámica" and not datos_levantamiento.get("adhesivo"):
            alertas.append("⚠️ FALTANTE TÉCNICO: Se definió cerámica pero no se especificó el tipo de adhesivo (Polvo o Pasta).")
            
        if not datos_levantamiento.get("factibilidad_sec"):
            alertas.append("⚠️ FACTIBILIDAD: Falta verificar el estado del empalme eléctrico y tablero SEC.")
            
        # Determinar Semáforo
        if porcentaje_completitud >= 90 and not any("🔴" in a for a in alertas):
            semaforo = "🟢 VERDE"
        elif porcentaje_completitud >= 60:
            semaforo = "🟡 AMARILLO"
        else:
            semaforo = "🔴 ROJO"
            
        return porcentaje_completitud, semaforo, alertas
