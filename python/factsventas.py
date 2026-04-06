# ============================================================
#  RetailPro | Generador fact.ventas
#  Ventas diarias consolidadas por tienda y artículo
#  Período histórico:  2025-01-01 → 2026-04-06
#  Autor: Ezequiel Díaz | GitHub: ediaz850
#  Datos 100% sintéticos generados para portfolio profesional
# ============================================================

import random
import pandas as pd
from datetime import date
from config import (
    get_connection,
    FECHA_INICIO, FECHA_FIN_HIST,
    FERIADOS_PANAMA, TEMPORADAS,
    MULTIPLICADOR_TEMPORADA,
    MULTIPLICADOR_FINDE,
    MULTIPLICADOR_FERIADO,
    IDS_TIENDA
)

random.seed(42)

# ============================================================
#  PARÁMETROS DE VENTA POR TIENDA
#  Cada tienda tiene un volumen base distinto según su formato
#  Flagship > Supertienda > Express
# ============================================================

VOLUMEN_BASE_TIENDA = {
    1: 120,   # RP-001 Marbella    — Flagship, mayor volumen
    2: 85,    # RP-002 La Chorrera — Supertienda
    3: 45,    # RP-003 Arraiján    — Express, menor volumen
    4: 90,    # RP-004 David       — Supertienda
    5: 75,    # RP-005 Santiago    — Supertienda
}

# Porcentaje de artículos activos por día por tienda
# No todos los artículos se venden todos los días
PCT_ARTICULOS_ACTIVOS = {
    1: 0.85,  # Flagship vende casi todo
    2: 0.75,
    3: 0.55,  # Express tiene menor variedad
    4: 0.78,
    5: 0.72,
}

# ============================================================
#  PATRONES DE ROTACIÓN POR CATEGORÍA
#  Qué tan rápido rota cada tipo de producto
# ============================================================

ROTACION_CATEGORIA = {
    # id_categoria: multiplicador de rotación
    1:  2.5,   # Leche entera — alta rotación
    2:  2.0,   # Leche descremada
    3:  1.5,   # Queso blanco
    4:  1.3,   # Queso amarillo
    5:  1.8,   # Yogur natural
    6:  1.6,   # Yogur con frutas
    7:  3.0,   # Arroz blanco — muy alta rotación
    8:  1.2,   # Arroz integral
    9:  2.2,   # Frijoles negros
    10: 2.0,   # Frijoles rojos
    11: 1.8,   # Carne molida
    12: 1.4,   # Bistec
    13: 2.0,   # Pechuga
    14: 1.8,   # Muslo
    15: 1.3,   # Chuleta
    16: 2.5,   # Pan blanco
    17: 1.5,   # Pan integral
    18: 1.8,   # Galletas saladas
    19: 2.0,   # Galletas dulces
    20: 2.2,   # Atún en agua
    21: 1.8,   # Atún en aceite
    22: 1.5,   # Sardinas
    23: 1.6,   # Aceite soya
    24: 1.5,   # Aceite maíz
    25: 1.8,   # Salsa tomate
    26: 1.6,   # Mayonesa
    27: 2.0,   # Jugo naranja
    28: 1.8,   # Jugo piña
    29: 1.5,   # Néctar mango
    30: 3.5,   # Agua 500ml — muy alta rotación
    31: 2.5,   # Agua 1500ml
    32: 2.8,   # Cola regular
    33: 1.5,   # Cola light
    34: 2.0,   # Fanta naranja
    35: 1.2,   # Energizante
    36: 1.8,   # Desinfectante
    37: 1.5,   # Cloro
    38: 1.6,   # Detergente polvo
    39: 1.4,   # Detergente líquido
    40: 1.2,   # Suavizante
    41: 1.8,   # Jabón baño
    42: 1.5,   # Shampoo normal
    43: 1.2,   # Shampoo anticaspa
    44: 1.3,   # Desodorante spray
    45: 1.2,   # Desodorante roll-on
    46: 1.8,   # Pasta dental
    47: 0.8,   # Cepillo dental — baja rotación
}

# ============================================================
#  FUNCIONES DE SOPORTE
# ============================================================

def get_multiplicador_dia(fecha_str, fecha_obj):
    """Calcula el multiplicador total de ventas para un día."""
    mes       = fecha_obj.month
    dia       = fecha_obj.day
    es_finde  = fecha_obj.weekday() >= 5
    es_feriado= fecha_str in FERIADOS_PANAMA
    temporada = TEMPORADAS[mes]

    # Efecto quincena
    if dia in (14, 15, 29, 30) and temporada == 'Normal':
        temporada = 'Quincena'

    mult = MULTIPLICADOR_TEMPORADA.get(temporada, 1.0)

    if es_finde:
        mult *= MULTIPLICADOR_FINDE

    if es_feriado:
        mult *= MULTIPLICADOR_FERIADO

    # Ruido aleatorio diario ±8% para naturalidad
    mult *= random.uniform(0.92, 1.08)

    return mult

def get_articulos_del_dia(df_articulos, id_tienda):
    """Selecciona los artículos que se venden hoy en esta tienda."""
    pct = PCT_ARTICULOS_ACTIVOS[id_tienda]
    n   = int(len(df_articulos) * pct)
    return df_articulos.sample(n=n, random_state=random.randint(1, 9999))

def calcular_descuento(id_categoria, es_finde, es_feriado):
    """Simula descuentos ocasionales según contexto."""
    # 15% de probabilidad de descuento en finde o feriado
    if (es_finde or es_feriado) and random.random() < 0.15:
        return round(random.choice([5.0, 10.0, 15.0, 20.0]), 2)
    # 5% de probabilidad cualquier día
    if random.random() < 0.05:
        return round(random.choice([5.0, 10.0]), 2)
    return 0.0

def asignar_cliente(id_clientes):
    """30% de ventas asociadas a cliente del club de fidelidad."""
    if random.random() < 0.30:
        return random.choice(id_clientes)
    return None

def asignar_empleado(empleados_tienda):
    """Asigna un empleado cajero o supervisor aleatorio."""
    return random.choice(empleados_tienda)

# ============================================================
#  GENERADOR PRINCIPAL
# ============================================================

def generar_ventas_historicas():
    """
    Genera fact.ventas consolidado diario para el período histórico.
    Una fila = un artículo vendido en una tienda en un día.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    # Cargar dimensiones necesarias
    df_articulos = pd.read_sql(
        "SELECT id_articulo, id_categoria, precio_base, costo FROM dim.articulo WHERE activo = 1",
        conn
    )
    df_empleados = pd.read_sql(
        "SELECT id_empleado, id_tienda FROM dim.empleado WHERE activo = 1",
        conn
    )
    df_clientes = pd.read_sql(
        "SELECT id_cliente FROM dim.cliente WHERE activo = 1",
        conn
    )
    df_tiempo = pd.read_sql(
        f"""SELECT id_tiempo, fecha, es_fin_semana, es_feriado, temporada
            FROM dim.tiempo
            WHERE fecha >= '{FECHA_INICIO}'
            AND fecha <= '{FECHA_FIN_HIST}'""",
        conn
    )

    id_clientes = df_clientes['id_cliente'].tolist()

    # Organizar empleados por tienda
    empleados_por_tienda = {
        t: df_empleados[df_empleados['id_tienda'] == t]['id_empleado'].tolist()
        for t in IDS_TIENDA
    }

    # Limpiar fact.ventas antes de cargar
    cursor.execute("DELETE FROM fact.ventas")
    conn.commit()

    sql_insert = """
        INSERT INTO fact.ventas (
            id_tiempo, id_tienda, id_articulo, id_empleado,
            id_cliente, id_promocion,
            cantidad, precio_unitario, descuento_pct, puntos_generados
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """

    total_filas  = 0
    total_dias   = len(df_tiempo)
    batch_size   = 500
    batch        = []

    print(f"  Procesando {total_dias} días × {len(IDS_TIENDA)} tiendas...")

    for _, fila_tiempo in df_tiempo.iterrows():
        id_tiempo  = int(fila_tiempo['id_tiempo'])
        fecha_str  = str(fila_tiempo['fecha'])[:10]
        fecha_obj  = date.fromisoformat(fecha_str)
        es_finde   = bool(fila_tiempo['es_fin_semana'])
        es_feriado = bool(fila_tiempo['es_feriado'])

        for id_tienda in IDS_TIENDA:
            mult_dia    = get_multiplicador_dia(fecha_str, fecha_obj)
            vol_base    = VOLUMEN_BASE_TIENDA[id_tienda]
            arts_hoy    = get_articulos_del_dia(df_articulos, id_tienda)
            emp_tienda  = empleados_por_tienda.get(id_tienda, [1])

            for _, art in arts_hoy.iterrows():
                id_art    = int(art['id_articulo'])
                id_cat    = int(art['id_categoria'])
                precio    = float(art['precio_base'])

                # Cantidad vendida: volumen base × rotación × multiplicador día
                rot       = ROTACION_CATEGORIA.get(id_cat, 1.0)
                cantidad  = max(1, int(
                    vol_base * rot * mult_dia * random.uniform(0.5, 1.5)
                ))

                descuento = calcular_descuento(id_cat, es_finde, es_feriado)
                id_cliente= asignar_cliente(id_clientes)
                id_emp    = asignar_empleado(emp_tienda)

                # Puntos de fidelidad: 1 punto por cada $1 de compra neta
                monto_neto = cantidad * precio * (1 - descuento/100)
                puntos     = int(monto_neto) if id_cliente else 0

                batch.append((
                    id_tiempo, id_tienda, id_art, id_emp,
                    id_cliente, None,   # id_promocion NULL por ahora
                    cantidad, round(precio, 2), descuento, puntos
                ))

                # Insertar en lotes para eficiencia
                if len(batch) >= batch_size:
                    cursor.executemany(sql_insert, batch)
                    conn.commit()
                    total_filas += len(batch)
                    batch = []

    # Insertar el último lote
    if batch:
        cursor.executemany(sql_insert, batch)
        conn.commit()
        total_filas += len(batch)

    conn.close()
    print(f"  ✅ fact.ventas: {total_filas:,} filas insertadas.")
    return total_filas

# ============================================================
#  MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 55)
    print("  RetailPro — Generador fact.ventas")
    print(f"  Período: {FECHA_INICIO} → {FECHA_FIN_HIST}")
    print("=" * 55)

    print("\nGenerando ventas históricas...")
    total = generar_ventas_historicas()

    print(f"\n{'='*55}")
    print(f"  Total filas generadas: {total:,}")
    print(f"  Aprox. por día:        {total // 461:,}")
    print(f"{'='*55}")
    print("\n✅ fact.ventas generado exitosamente.")
    print("   Siguiente paso: ejecutar 04_generate_fact_inventario.py")