# ============================================================
#  RetailPro | Generador dim.tiempo
#  Calendario completo 2025-2026
#  Incluye feriados panameños, temporadas y efecto quincena
#  Autor: Ezequiel Díaz | GitHub: ediaz850
# ============================================================

import pandas as pd
from datetime import date, timedelta
from config import (
    get_connection,
    FECHA_INICIO, FECHA_FIN_PRED,
    TEMPORADAS, FERIADOS_PANAMA
)
from db_utils import insertar_dataframe

NOMBRES_DIA = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles',
    3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}

NOMBRES_MES = {
    1: 'Enero',     2: 'Febrero',   3: 'Marzo',
    4: 'Abril',     5: 'Mayo',      6: 'Junio',
    7: 'Julio',     8: 'Agosto',    9: 'Septiembre',
    10: 'Octubre',  11: 'Noviembre', 12: 'Diciembre'
}

def generar_calendario():
    """
    Genera el calendario completo 2025-2026.
    - Histórico:  2025-01-01 → 2026-04-06
    - Proyectado: 2026-04-07 → 2026-12-31
    """
    filas           = []
    inicio          = date.fromisoformat(FECHA_INICIO)
    fin             = date.fromisoformat(FECHA_FIN_PRED)
    delta           = timedelta(days=1)
    fecha           = inicio
    corte_historico = date(2026, 4, 6)

    while fecha <= fin:
        fecha_str    = fecha.isoformat()
        es_feriado   = 1 if fecha_str in FERIADOS_PANAMA else 0
        nombre_feria = FERIADOS_PANAMA.get(fecha_str, None)
        es_finde     = 1 if fecha.weekday() >= 5 else 0
        temporada    = TEMPORADAS[fecha.month]

        if fecha.day in (14, 15, 29, 30) and temporada == 'Normal':
            temporada = 'Quincena'

        tipo_periodo = 'Histórico' if fecha <= corte_historico else 'Proyectado'

        filas.append({
            'id_tiempo'     : int(fecha_str.replace('-', '')),
            'fecha'         : fecha_str,
            'dia'           : fecha.day,
            'mes'           : fecha.month,
            'anio'          : fecha.year,
            'trimestre'     : (fecha.month - 1) // 3 + 1,
            'semana_anio'   : fecha.isocalendar()[1],
            'nombre_dia'    : NOMBRES_DIA[fecha.weekday()],
            'nombre_mes'    : NOMBRES_MES[fecha.month],
            'es_fin_semana' : es_finde,
            'es_feriado'    : es_feriado,
            'nombre_feriado': nombre_feria,
            'temporada'     : temporada,
            'tipo_periodo'  : tipo_periodo,
        })
        fecha += delta

    return pd.DataFrame(filas)


if __name__ == '__main__':
    print("Generando calendario 2025-2026...")
    df = generar_calendario()

    historico  = df[df['tipo_periodo'] == 'Histórico']
    proyectado = df[df['tipo_periodo'] == 'Proyectado']

    print(f"\n  Total días generados  : {len(df)}")
    print(f"  → Histórico           : {len(historico)} días")
    print(f"  → Proyectado          : {len(proyectado)} días")
    print(f"\n  Feriados totales      : {df['es_feriado'].sum()}")
    print(f"  Fines de semana       : {df['es_fin_semana'].sum()}")
    print(f"  Días de quincena      : {(df['temporada']=='Quincena').sum()}")
    print(f"  Días de Navidad       : {(df['temporada']=='Navidad').sum()}")
    print(f"  Días temporada Alta   : {(df['temporada']=='Alta').sum()}")

    print("\nInsertando en SQL Server...")
    insertar_dataframe(df, 'dim.tiempo', limpiar=True, truncar=True)