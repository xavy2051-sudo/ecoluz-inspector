class MaterialDependencyEngine:
    @staticmethod
    def obtener_kit_dependiente(partida_principal, cantidad_m2):
        """
        Retorna la lista de insumos y consumibles necesarios según la partida.
        """
        insumos = []
        
        if partida_principal == "Cerámica / Porcelanato":
            insumos = [
                {"item": "Adhesivo Cerámico (Sacos 25kg)", "cantidad": round(cantidad_m2 / 5.0, 2), "unidad": "saco"},
                {"item": "Fragüe", "cantidad": round(cantidad_m2 / 4.0, 2), "unidad": "kg"},
                {"item": "Crucetas / Niveladores", "cantidad": round(cantidad_m2 * 20, 0), "unidad": "un"},
                {"item": "Silicona Sanitaria Anti-hongos", "cantidad": round(cantidad_m2 / 15.0, 1), "unidad": "tubo"},
                {"item": "Esponja de Limpieza", "cantidad": 2, "unidad": "un"}
            ]
            
        elif partida_principal == "Estructura Metalcom":
            insumos = [
                {"item": "Tornillos Framing 8x1/2 (Caja 500 un)", "cantidad": round((cantidad_m2 * 40) / 500, 1), "unidad": "caja"},
                {"item": "Tornillos Wafer 10x3/4 (Caja 500 un)", "cantidad": round((cantidad_m2 * 25) / 500, 1), "unidad": "caja"},
                {"item": "Aislación Lana de Vidrio R188", "cantidad": round(cantidad_m2 * 1.05, 2), "unidad": "m2"},
                {"item": "Banda Acústica Aislante", "cantidad": round(cantidad_m2 * 0.8, 1), "unidad": "mL"}
            ]
            
        elif partida_principal == "Volcanita / Placa Yeso-Cartón":
            placas = cantidad_m2 / 2.98  # Placa estándar 1.22x2.44m
            insumos = [
                {"item": "Placas Volcanita RH / ST", "cantidad": round(placas, 1), "unidad": "placa"},
                {"item": "Tornillos Drywall 6x1 5/8 (Caja 1000 un)", "cantidad": round((placas * 30) / 1000, 1), "unidad": "caja"},
                {"item": "Masa Junta Lista para Usar (Juntaprop)", "cantidad": round(cantidad_m2 * 1.2, 1), "unidad": "kg"},
                {"item": "Cinta Malla / Papel Junta", "cantidad": round(cantidad_m2 * 1.2, 1), "unidad": "mL"}
            ]
            
        return insumos
