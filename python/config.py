# ============================================================
#  RetailPro | Configuración central
#  Autor: Ezequiel Díaz | GitHub: ediaz850
#  Datos sintéticos generados para portfolio profesional
#
#  Rango histórico:  Enero 2025 — Abril 2026
#  Rango predictivo: Mayo 2026  — Diciembre 2026
# ============================================================

import pyodbc

# --- Conexión a SQL Server -----------------------------------
# Ajusta SERVER si tu instancia tiene un nombre distinto
# Ejemplo: SERVER = 'DESKTOP-ABC123\\SQLEXPRESS'
SERVER   = 'localhost'
DATABASE = 'retailpro_db'

def get_connection():
    """Retorna una conexión activa a retailpro_db."""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

# --- Parámetros globales del proyecto -----------------------

# Datos históricos simulados (lo que "pasó")
FECHA_INICIO   = '2025-01-01'
FECHA_FIN_HIST = '2026-04-06'   # hasta hoy

# Datos proyectados para análisis predictivo
FECHA_FIN_PRED = '2026-12-31'   # fin del año proyectado

IDS_TIENDA = [1, 2, 3, 4, 5]

# --- Temporadas por mes (comportamiento retail panameño) ----
TEMPORADAS = {
    1:  'Normal',      # Enero    — post navidad, bajo
    2:  'Alta',        # Febrero  — carnaval
    3:  'Normal',      # Marzo
    4:  'Alta',        # Abril    — Semana Santa
    5:  'Normal',      # Mayo
    6:  'Normal',      # Junio
    7:  'Alta',        # Julio    — vacaciones escolares
    8:  'Alta',        # Agosto   — Back-to-School
    9:  'Normal',      # Septiembre
    10: 'Normal',      # Octubre
    11: 'Alta',        # Noviembre — Black Friday
    12: 'Navidad',     # Diciembre — temporada alta máxima
}

# --- Feriados nacionales de Panamá --------------------------
FERIADOS_PANAMA = {
    # 2025
    '2025-01-01': 'Año Nuevo',
    '2025-01-09': 'Día de los Mártires',
    '2025-03-03': 'Lunes de Carnaval',
    '2025-03-04': 'Martes de Carnaval',
    '2025-04-18': 'Viernes Santo',
    '2025-05-01': 'Día del Trabajo',
    '2025-11-02': 'Día de los Difuntos',
    '2025-11-03': 'Separación de Panamá de Colombia',
    '2025-11-04': 'Día de la Bandera',
    '2025-11-10': 'Primer Grito de Independencia',
    '2025-11-28': 'Independencia de España',
    '2025-12-08': 'Día de la Madre',
    '2025-12-25': 'Navidad',
    # 2026
    '2026-01-01': 'Año Nuevo',
    '2026-01-09': 'Día de los Mártires',
    '2026-02-16': 'Lunes de Carnaval',
    '2026-02-17': 'Martes de Carnaval',
    '2026-04-03': 'Viernes Santo',
    '2026-05-01': 'Día del Trabajo',
    '2026-11-02': 'Día de los Difuntos',
    '2026-11-03': 'Separación de Panamá de Colombia',
    '2026-11-04': 'Día de la Bandera',
    '2026-11-10': 'Primer Grito de Independencia',
    '2026-11-28': 'Independencia de España',
    '2026-12-08': 'Día de la Madre',
    '2026-12-25': 'Navidad',
}

# --- Multiplicadores de venta por temporada -----------------
# Usados en fact.ventas para simular patrones reales
MULTIPLICADOR_TEMPORADA = {
    'Normal'   : 1.0,
    'Alta'     : 1.4,
    'Navidad'  : 1.9,
    'Quincena' : 1.3,
}

MULTIPLICADOR_FINDE   = 1.25
MULTIPLICADOR_FERIADO = 1.35

print("✅ Configuración cargada correctamente.")
print(f"   Período histórico:  {FECHA_INICIO} → {FECHA_FIN_HIST}")
print(f"   Período predictivo: 2026-05-01 → {FECHA_FIN_PRED}")