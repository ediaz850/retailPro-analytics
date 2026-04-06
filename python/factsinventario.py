# ============================================================
#  RetailPro | Generador fact.inventario
#  Snapshot diario de stock por tienda y artículo
#  Período histórico:  2025-01-01 → 2026-04-06
#  Autor: Ezequiel Díaz | GitHub: ediaz850
#  Datos 100% sintéticos generados para portfolio profesional
# ============================================================

import random
import pandas as pd
from config import (
    get_connection,
    FECHA_INICIO, FECHA_FIN_HIST,
    IDS_TIENDA
)

random.seed(42)

# ============================================================
#  PARÁMETROS DE INVENTARIO POR TIENDA
#  Stock inicial realista según formato de tienda
# ============================================================

STOCK_INICIAL_BASE = {
    1: 500,   # RP-001 Marbella    — Flagship, mayor capacidad
    2: 350,   # RP-002 La Chorrera — Supertienda
    3: 180,   # RP-003 Arraiján    — Express
    4: 370,   # RP-004 David       — Supertienda
    5: 300,   # RP-005 Santiago    — Supertienda
}

# Stock mínimo por categoría (umbral de alerta)
STOCK_MINIMO_CATEGORIA = {
    1:  50,   # Leche entera        — alta rotación, stock mínimo alto
    2:  40,
    3:  30,
    4:  25,
    5:  35,
    6:  30,
    7:  80,   # Arroz               — muy alta rotación
    8:  25,
    9:  50,
    10: 45,
    11: 40,   # Carnes
    12: 30,
    13: 45,
    14: 40,
    15: 25,
    16: 50,   # Pan
    17: 25,
    18: 35,
    19: 40,
    20: 45,   # Atún
    21: 40,
    22: 30,
    23: 35,
    24: 30,
    25: 35,
    26: 30,
    27: 40,   # Jugos
    28: 35,
    29: 25,
    30: 80,   # Agua 500ml          — muy alta rotación
    31: 60,
    32: 70,   # Cola
    33: 30,
    34: 40,
    35: 20,
    36: 35,   # Limpieza
    37: 30,
    38: 40,
    39: 35,
    40: 25,
    41: 40,   # Personal
    42: 30,
    43: 25,
    44: 30,
    45: 25,
    46: 35,
    47: 20,
}

# Frecuencia de reposición por categoría (cada cuántos días)
DIAS_REPOSICION = {
    1:  3,    # Lácteos — reposición frecuente
    2:  3,
    3:  4,
    4:  4,
    5:  3,
    6:  3,
    7:  5,    # Granos
    8:  7,
    9:  5,
    10: 5,
    11: 2,    # Carnes — reposición casi diaria
    12: 2,
    13: 2,
    14: 2,
    15: 3,
    16: 3,    # Panadería
    17: 4,
    18: 7,
    19: 7,
    20: 7,    # Enlatados — menor frecuencia
    21: 7,
    22: 10,
    23: 10,
    24: 10,
    25: 7,
    26: 7,
    27: 5,    # Bebidas
    28: 5,
    29: 7,
    30: 3,    # Agua — alta frecuencia
    31: 4,
    32: 4,
    33: 5,
    34: 5,
    35: 10,
    36: 7,    # Limpieza
    37: 7,
    38: 10,
    39: 10,
    40: 14,
    41: 7,    # Personal
    42: 10,
    43: 10,
    44: 10,
    45: 10,
    46: 7,
    47: 14,
}

# ============================================================
#  GENERADOR PRINCIPAL
# ============================================================

def generar_inventario():
    conn   = get_connection()
    cursor = conn.cursor()

    # Cargar dimensiones necesarias
    df_articulos = pd.read_sql(
        """SELECT id_articulo, id_categoria
           FROM dim.articulo
           WHERE activo = 1""",
        conn
    )
    df_tiempo = pd.read_sql(
        f"""SELECT id_tiempo, fecha
            FROM dim.tiempo
            WHERE fecha >= '{FECHA_INICIO}'
            AND fecha <= '{FECHA_FIN_HIST}'
            ORDER BY fecha""",
        conn
    )
    df_ventas = pd.read_sql(
        f"""SELECT id_tiempo, id_tienda, id_articulo,
                   SUM(cantidad) as unidades_vendidas
            FROM fact.ventas
            WHERE id_tiempo IN (
                SELECT id_tiempo FROM dim.tiempo
                WHERE fecha >= '{FECHA_INICIO}'
                AND fecha <= '{FECHA_FIN_HIST}'
            )
            GROUP BY id_tiempo, id_tienda, id_articulo""",
        conn
    )

    # Índice de ventas para lookup rápido
    ventas_idx = df_ventas.set_index(
        ['id_tiempo', 'id_tienda', 'id_articulo']
    )['unidades_vendidas'].to_dict()

    # Categoría por artículo
    cat_art = df_articulos.set_index('id_articulo')['id_categoria'].to_dict()

    # Limpiar fact.inventario
    cursor.execute("DELETE FROM fact.inventario")
    conn.commit()

    sql_insert = """
        INSERT INTO fact.inventario (
            id_tiempo, id_tienda, id_articulo,
            stock_inicial, unidades_vendidas, unidades_recibidas,
            stock_final, stock_minimo
        ) VALUES (?,?,?,?,?,?,?,?)
    """

    # Estado de stock actual por tienda/artículo
    # Inicializado con stock inicial aleatorio
    stock_actual = {}
    for id_tienda in IDS_TIENDA:
        for _, art in df_articulos.iterrows():
            id_art  = int(art['id_articulo'])
            id_cat  = int(art['id_categoria'])
            base    = STOCK_INICIAL_BASE[id_tienda]
            rot_key = STOCK_MINIMO_CATEGORIA.get(id_cat, 30)
            stock_actual[(id_tienda, id_art)] = int(
                base * random.uniform(0.8, 1.5)
            )

    total_filas   = 0
    total_alertas = 0
    batch         = []
    batch_size    = 500
    dias_lista    = df_tiempo.to_dict('records')
    total_dias    = len(dias_lista)

    print(f"  Procesando {total_dias} días × {len(IDS_TIENDA)} tiendas × "
          f"{len(df_articulos)} artículos...")

    for fila_tiempo in dias_lista:
        id_tiempo = int(fila_tiempo['id_tiempo'])
        fecha_str = str(fila_tiempo['fecha'])[:10]
        dia_num   = int(fecha_str.replace('-', ''))

        for id_tienda in IDS_TIENDA:
            for _, art in df_articulos.iterrows():
                id_art  = int(art['id_articulo'])
                id_cat  = int(art['id_categoria'])

                stock_min  = STOCK_MINIMO_CATEGORIA.get(id_cat, 25)
                stock_ini  = stock_actual[(id_tienda, id_art)]

                # Unidades vendidas hoy
                uds_vendidas = int(
                    ventas_idx.get((id_tiempo, id_tienda, id_art), 0)
                )

                # Reposición: llega cada N días según categoría
                dias_rep    = DIAS_REPOSICION.get(id_cat, 7)
                uds_recibidas = 0

                # Reposición programada
                if dia_num % dias_rep == 0:
                    # Cantidad de reposición basada en lo vendido
                    uds_recibidas = int(
                        uds_vendidas * dias_rep * random.uniform(0.9, 1.2)
                    )
                    uds_recibidas = max(uds_recibidas, stock_min * 2)

                # Reposición de emergencia si stock muy bajo
                stock_post_venta = stock_ini - uds_vendidas
                if stock_post_venta <= stock_min:
                    emergencia = int(
                        STOCK_INICIAL_BASE[id_tienda] *
                        random.uniform(0.5, 0.8)
                    )
                    uds_recibidas = max(uds_recibidas, emergencia)

                # Stock final
                stock_fin = max(0, stock_ini - uds_vendidas + uds_recibidas)

                # Actualizar estado para el día siguiente
                stock_actual[(id_tienda, id_art)] = stock_fin

                # Conteo de alertas
                if stock_fin <= stock_min:
                    total_alertas += 1

                batch.append((
                    id_tiempo, id_tienda, id_art,
                    stock_ini, uds_vendidas, uds_recibidas,
                    stock_fin, stock_min
                ))

                if len(batch) >= batch_size:
                    cursor.executemany(sql_insert, batch)
                    conn.commit()
                    total_filas += len(batch)
                    batch = []

    # Último lote
    if batch:
        cursor.executemany(sql_insert, batch)
        conn.commit()
        total_filas += len(batch)

    conn.close()

    print(f"  ✅ fact.inventario: {total_filas:,} filas insertadas.")
    print(f"  ⚠️  Alertas de stock bajo: {total_alertas:,}")
    return total_filas, total_alertas

# ============================================================
#  MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 55)
    print("  RetailPro — Generador fact.inventario")
    print(f"  Período: {FECHA_INICIO} → {FECHA_FIN_HIST}")
    print("=" * 55)

    print("\nGenerando snapshots de inventario...")
    print("  (Este proceso puede tardar 3-5 minutos)\n")

    total, alertas = generar_inventario()

    print(f"\n{'='*55}")
    print(f"  Total filas:       {total:,}")
    print(f"  Alertas stock bajo: {alertas:,}")
    print(f"  % días con alerta:  {alertas/total*100:.1f}%")
    print(f"{'='*55}")
    print("\n✅ fact.inventario generado exitosamente.")
    print("   Siguiente paso: ejecutar 05_daily_loader.py")