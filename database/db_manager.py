import sqlite3
import json
from datetime import datetime

DB_NAME = "database/ecoluz.db"

def init_db():
    """Inicializa las tablas de la base de datos ECOLUZ v2.0."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de Proyectos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            direccion TEXT,
            inspector TEXT,
            fecha_creacion TEXT
        )
    ''')
    
    # Tabla de Versiones de Presupuestos (Versionado V1, V2, V3)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cotizaciones_versiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            version TEXT,
            monto_total REAL,
            detalles_json TEXT,
            observaciones TEXT,
            fecha TEXT,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def guardar_version_cotizacion(proyecto_id, version, monto_total, detalles_dict, observaciones=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO cotizaciones_versiones (proyecto_id, version, monto_total, detalles_json, observaciones, fecha)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (proyecto_id, version, monto_total, json.dumps(detalles_dict), observaciones, fecha_actual))
    
    conn.commit()
    conn.close()
