# ============================================================
#  RetailPro | Utilidades de base de datos
#  Funciones reutilizables de inserción para todos los scripts
#  Adaptado del código de trabajo real de Ezequiel Díaz
#  Autor: Ezequiel Díaz | GitHub: ediaz850
# ============================================================

import pyodbc
import pandas as pd
import numpy as np
from config import get_connection


# -----------------------------------------------------------
# 1. Obtener metadata real de SQL Server
# -----------------------------------------------------------
def obtener_columnas_sql(cursor, tabla_sql: str) -> list:
    schema, table = tabla_sql.split('.')
    cursor.execute(f"""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{schema}'
        AND TABLE_NAME = '{table}'
        ORDER BY ORDINAL_POSITION
    """)
    return [row[0] for row in cursor.fetchall()]


def obtener_tipos_columnas_sql(cursor, tabla_sql: str) -> dict:
    schema, table = tabla_sql.split('.')
    cursor.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{schema}'
        AND TABLE_NAME = '{table}'
    """)
    return {row[0]: row[1] for row in cursor.fetchall()}


def obtener_limites_texto(cursor, tabla_sql: str) -> dict:
    schema, table = tabla_sql.split('.')
    cursor.execute(f"""
        SELECT COLUMN_NAME, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{schema}'
        AND TABLE_NAME = '{table}'
        AND DATA_TYPE IN ('varchar','nvarchar','char','nchar')
    """)
    return {row[0]: row[1] for row in cursor.fetchall()}


# -----------------------------------------------------------
# 2. Limpieza por tipo de dato
# -----------------------------------------------------------
def limpiar_dataframe(df: pd.DataFrame, tipos_sql: dict,
                      limites_texto: dict) -> pd.DataFrame:
    for col in df.columns:
        if col not in tipos_sql:
            continue

        tipo = tipos_sql[col]

        # Enteros
        if tipo in ['int', 'bigint', 'smallint', 'tinyint']:
            try:
                df[col] = df[col].replace(
                    ['', ' ', 'null', 'NULL', 'None', 'nan'], np.nan
                )
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip()
                    df[col] = df[col].replace(['nan', 'None', ''], np.nan)
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].round(0)
                df[col] = df[col].fillna(0).astype('Int64')
            except Exception as e:
                print(f"⚠️ Error convirtiendo '{col}' a entero: {e}")
                df[col] = pd.to_numeric(
                    df[col], errors='coerce'
                ).fillna(0).astype('Int64')

        # Decimales
        elif tipo in ['decimal', 'numeric', 'float', 'real']:
            df[col] = df[col].replace(
                ['', ' ', 'null', 'NULL', 'None'], np.nan
            )
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)

        # Fechas
        elif tipo in ['datetime', 'date', 'smalldatetime']:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Texto
        elif tipo in ['varchar', 'nvarchar', 'char', 'nchar', 'text', 'ntext']:
            # Convertir NaN y valores nulos a None
            df[col] = df[col].where(pd.notnull(df[col]), None)
            # Convertir a string solo los que no son None
            df[col] = df[col].apply(
                lambda x: str(x).strip() if x is not None and not isinstance(x, float) else None
            )
            # Limpiar strings vacíos y 'nan'
            df[col] = df[col].replace({'nan': None, '': None})
            # Limitar longitud solo si el valor no es None
            if col in limites_texto and limites_texto[col]:
                limite = limites_texto[col]
                df[col] = df[col].apply(
                    lambda x: x[:limite] if isinstance(x, str) else None
                )

    return df


# -----------------------------------------------------------
# 3. Convertir DataFrame a tuplas limpias
#    NaN → None para que SQL Server acepte NULL correctamente
# -----------------------------------------------------------
def convertir_a_tuplas(df: pd.DataFrame) -> list:
    datos = []
    for _, row in df.iterrows():
        tupla = []
        for val in row:
            if pd.isna(val) if not isinstance(val, str) else False:
                tupla.append(None)
            elif hasattr(val, 'item'):
                tupla.append(val.item())
            elif isinstance(val, pd.Timestamp):
                tupla.append(val.to_pydatetime())
            else:
                tupla.append(val)
        datos.append(tuple(tupla))
    return datos


# -----------------------------------------------------------
# 4. Inserción principal — reutilizable en todos los scripts
# -----------------------------------------------------------
def insertar_dataframe(df: pd.DataFrame, tabla_sql: str,
                       limpiar: bool = True,
                       truncar: bool = False) -> None:
    """
    Inserta un DataFrame en SQL Server de forma segura.

    Parámetros:
    - df         : DataFrame con los datos a insertar
    - tabla_sql  : nombre completo 'schema.tabla' (ej: 'dim.tiempo')
    - limpiar    : True = limpia y convierte tipos automáticamente
    - truncar    : True = hace DELETE de la tabla antes de insertar
    """
    conn   = get_connection()
    cursor = conn.cursor()

    # Obtener metadata de SQL Server
    columnas_sql  = obtener_columnas_sql(cursor, tabla_sql)
    tipos_sql     = obtener_tipos_columnas_sql(cursor, tabla_sql)
    limites_texto = obtener_limites_texto(cursor, tabla_sql)

    # Filtrar columnas calculadas (no se insertan)
    # SQL Server las calcula automáticamente
    columnas_calculadas = {
        'monto_bruto', 'monto_descuento', 'monto_neto',
        'margen_pct', 'puntos_vigentes', 'nombre_completo',
        'alerta_stock', 'dias_cobertura', 'costo_total', 'codigo_cat'
    }
    columnas_sql = [c for c in columnas_sql if c not in columnas_calculadas]

    # Alinear columnas del DataFrame con las de SQL
    cols_disponibles = [c for c in columnas_sql if c in df.columns]
    df = df[cols_disponibles].copy()

    if df.empty:
        print(f"⚠️ No hay datos para insertar en {tabla_sql}")
        conn.close()
        return

    # Limpiar tipos de dato
    if limpiar:
        tipos_filtrados  = {k: v for k, v in tipos_sql.items()
                            if k in cols_disponibles}
        limites_filtrados = {k: v for k, v in limites_texto.items()
                             if k in cols_disponibles}
        df = limpiar_dataframe(df, tipos_filtrados, limites_filtrados)

    # Truncar tabla si se requiere
    if truncar:
        cursor.execute(f"DELETE FROM {tabla_sql}")
        conn.commit()
        print(f"🗑️  {tabla_sql} limpiada.")

    # Construir query dinámicamente
    placeholders  = ', '.join(['?'] * len(cols_disponibles))
    cols_str      = ', '.join([f'[{c}]' for c in cols_disponibles])
    query         = f"INSERT INTO {tabla_sql} ({cols_str}) VALUES ({placeholders})"

    # Convertir a tuplas limpias
    datos = convertir_a_tuplas(df)

    # Insertar con fast_executemany para mayor rendimiento
    try:
        cursor.fast_executemany = True
        cursor.executemany(query, datos)
        conn.commit()
        print(f"✅ {tabla_sql}: {len(df):,} filas insertadas.")
    except Exception as e:
        print(f"❌ Error insertando en {tabla_sql}: {e}")
        print(f"   Query: {query}")
        print(f"   Primera fila: {datos[0] if datos else 'vacío'}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()