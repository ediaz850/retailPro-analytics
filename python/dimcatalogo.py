# ============================================================
#  RetailPro | Generador de dimensiones del catálogo
#  Pobla: dim.categoria, dim.articulo, dim.empleado, dim.cliente
#  Autor: Ezequiel Díaz | GitHub: ediaz850
#  Datos 100% sintéticos generados para portfolio profesional
# ============================================================

import random
import pandas as pd
from faker import Faker
from config import get_connection, IDS_TIENDA

fake = Faker('es_MX')
random.seed(42)

# ============================================================
#  1. CATEGORÍAS — árbol real de supermercado panameño
# ============================================================

ARBOL_CATEGORIAS = [
    # (seccion, departamento, categoria, subcategoria)
    # ALIMENTOS
    ('Alimentos', 'Lácteos',       'Leches',          'Leche entera'),
    ('Alimentos', 'Lácteos',       'Leches',          'Leche descremada'),
    ('Alimentos', 'Lácteos',       'Quesos',           'Queso blanco'),
    ('Alimentos', 'Lácteos',       'Quesos',           'Queso amarillo'),
    ('Alimentos', 'Lácteos',       'Yogures',          'Yogur natural'),
    ('Alimentos', 'Lácteos',       'Yogures',          'Yogur con frutas'),
    ('Alimentos', 'Granos',        'Arroz',            'Arroz blanco'),
    ('Alimentos', 'Granos',        'Arroz',            'Arroz integral'),
    ('Alimentos', 'Granos',        'Frijoles',         'Frijoles negros'),
    ('Alimentos', 'Granos',        'Frijoles',         'Frijoles rojos'),
    ('Alimentos', 'Carnes',        'Res',              'Carne molida'),
    ('Alimentos', 'Carnes',        'Res',              'Bistec de res'),
    ('Alimentos', 'Carnes',        'Pollo',            'Pechuga de pollo'),
    ('Alimentos', 'Carnes',        'Pollo',            'Muslo de pollo'),
    ('Alimentos', 'Carnes',        'Cerdo',            'Chuleta de cerdo'),
    ('Alimentos', 'Panadería',     'Pan',              'Pan de molde'),
    ('Alimentos', 'Panadería',     'Pan',              'Pan integral'),
    ('Alimentos', 'Panadería',     'Galletas',         'Galletas saladas'),
    ('Alimentos', 'Panadería',     'Galletas',         'Galletas dulces'),
    ('Alimentos', 'Enlatados',     'Atún',             'Atún en agua'),
    ('Alimentos', 'Enlatados',     'Atún',             'Atún en aceite'),
    ('Alimentos', 'Enlatados',     'Sardinas',         'Sardinas en salsa'),
    ('Alimentos', 'Aceites',       'Aceite vegetal',   'Aceite de soya'),
    ('Alimentos', 'Aceites',       'Aceite vegetal',   'Aceite de maíz'),
    ('Alimentos', 'Condimentos',   'Salsas',           'Salsa de tomate'),
    ('Alimentos', 'Condimentos',   'Salsas',           'Mayonesa'),
    # BEBIDAS
    ('Bebidas',   'Jugos',         'Jugos naturales',  'Jugo de naranja'),
    ('Bebidas',   'Jugos',         'Jugos naturales',  'Jugo de piña'),
    ('Bebidas',   'Jugos',         'Néctares',         'Néctar de mango'),
    ('Bebidas',   'Aguas',         'Agua purificada',  'Agua 500ml'),
    ('Bebidas',   'Aguas',         'Agua purificada',  'Agua 1500ml'),
    ('Bebidas',   'Gaseosas',      'Cola',             'Cola regular'),
    ('Bebidas',   'Gaseosas',      'Cola',             'Cola light'),
    ('Bebidas',   'Gaseosas',      'Sabores',          'Naranja'),
    ('Bebidas',   'Energizantes',  'Energizantes',     'Bebida energética'),
    # LIMPIEZA
    ('Limpieza',  'Hogar',         'Desinfectantes',   'Líquido multiusos'),
    ('Limpieza',  'Hogar',         'Desinfectantes',   'Cloro'),
    ('Limpieza',  'Hogar',         'Detergentes',      'Detergente en polvo'),
    ('Limpieza',  'Hogar',         'Detergentes',      'Detergente líquido'),
    ('Limpieza',  'Hogar',         'Suavizantes',      'Suavizante de ropa'),
    # CUIDADO PERSONAL
    ('Personal',  'Higiene',       'Jabones',          'Jabón de baño'),
    ('Personal',  'Higiene',       'Shampoo',          'Shampoo normal'),
    ('Personal',  'Higiene',       'Shampoo',          'Shampoo anticaspa'),
    ('Personal',  'Higiene',       'Desodorantes',     'Desodorante spray'),
    ('Personal',  'Higiene',       'Desodorantes',     'Desodorante roll-on'),
    ('Personal',  'Dental',        'Pastas',           'Pasta dental'),
    ('Personal',  'Dental',        'Cepillos',         'Cepillo dental'),
]

def generar_categorias():
    rows = []
    for i, (sec, dep, cat, sub) in enumerate(ARBOL_CATEGORIAS, start=1):
        rows.append({
            'id_categoria': i,
            'seccion':      sec,
            'departamento': dep,
            'categoria':    cat,
            'subcategoria': sub,
            'activa':       1
        })
    return pd.DataFrame(rows)

# ============================================================
#  2. ARTÍCULOS — 200 productos con EAN, SKU, precios reales
# ============================================================

# (nombre_base, marca, costo, precio, unidad, contenido, u_contenido, requiere_frio)
PRODUCTOS_BASE = [
    # Lácteos
    ('Leche La Campiña 1L',       'La Campiña',  0.75, 1.29, 'litro',  1.0,  'lt',  1),
    ('Leche Dos Pinos 1L',        'Dos Pinos',   0.82, 1.45, 'litro',  1.0,  'lt',  1),
    ('Leche Nutrileche 1L',       'Nutrileche',  0.70, 1.19, 'litro',  1.0,  'lt',  1),
    ('Leche descremada 1L',       'La Campiña',  0.80, 1.39, 'litro',  1.0,  'lt',  1),
    ('Queso blanco 500g',         'Chela',       1.80, 3.25, 'unidad', 0.5,  'kg',  1),
    ('Queso amarillo 200g',       'Kraft',       1.50, 2.75, 'unidad', 0.2,  'kg',  1),
    ('Yogur fresa 200g',          'Nestlé',      0.55, 0.99, 'unidad', 0.2,  'kg',  1),
    ('Yogur natural 500g',        'Nestlé',      1.10, 1.99, 'unidad', 0.5,  'kg',  1),
    # Granos
    ('Arroz Gallo 5lb',           'Gallo',       2.10, 3.49, 'unidad', 5.0,  'lb',  0),
    ('Arroz Diana 5lb',           'Diana',       1.95, 3.25, 'unidad', 5.0,  'lb',  0),
    ('Arroz integral 2lb',        'Gallo',       1.50, 2.59, 'unidad', 2.0,  'lb',  0),
    ('Frijoles negros 1lb',       'Polar',       0.85, 1.49, 'unidad', 1.0,  'lb',  0),
    ('Frijoles rojos 1lb',        'Polar',       0.85, 1.49, 'unidad', 1.0,  'lb',  0),
    # Carnes
    ('Carne molida 1lb',          'Res',         2.50, 4.25, 'unidad', 1.0,  'lb',  1),
    ('Bistec de res 1lb',         'Res',         3.20, 5.49, 'unidad', 1.0,  'lb',  1),
    ('Pechuga de pollo 1lb',      'El Gallinero',1.80, 3.25, 'unidad', 1.0,  'lb',  1),
    ('Muslo de pollo 1lb',        'El Gallinero',1.40, 2.49, 'unidad', 1.0,  'lb',  1),
    ('Chuleta de cerdo 1lb',      'Cerdo',       2.10, 3.75, 'unidad', 1.0,  'lb',  1),
    # Panadería
    ('Pan molde blanco',          'Bimbo',       0.90, 1.59, 'unidad', 0.5,  'kg',  0),
    ('Pan molde integral',        'Bimbo',       1.05, 1.85, 'unidad', 0.5,  'kg',  0),
    ('Galletas Ritz',             'Nabisco',     0.75, 1.35, 'unidad', 0.2,  'kg',  0),
    ('Galletas Oreo',             'Nabisco',     0.80, 1.45, 'unidad', 0.154,'kg',  0),
    # Enlatados
    ('Atún Van Camps agua',       'Van Camps',   0.85, 1.49, 'unidad', 0.142,'kg',  0),
    ('Atún Van Camps aceite',     'Van Camps',   0.85, 1.49, 'unidad', 0.142,'kg',  0),
    ('Sardinas Isabel',           'Isabel',      0.70, 1.25, 'unidad', 0.125,'kg',  0),
    # Aceites y condimentos
    ('Aceite Mazola 1L',          'Mazola',      1.85, 3.25, 'litro',  1.0,  'lt',  0),
    ('Aceite Iberia 1L',          'Iberia',      1.70, 2.99, 'litro',  1.0,  'lt',  0),
    ('Salsa de tomate Heinz',     'Heinz',       1.20, 2.15, 'unidad', 0.397,'kg',  0),
    ('Mayonesa Hellmann 200g',    'Hellmann',    0.90, 1.59, 'unidad', 0.2,  'kg',  0),
    # Bebidas
    ('Jugo Del Valle naranja 1L', 'Del Valle',   0.95, 1.79, 'litro',  1.0,  'lt',  0),
    ('Jugo Del Valle piña 1L',    'Del Valle',   0.95, 1.79, 'litro',  1.0,  'lt',  0),
    ('Néctar de mango 1L',        'Kern\'s',     0.85, 1.55, 'litro',  1.0,  'lt',  0),
    ('Agua Cristal 500ml',        'Cristal',     0.25, 0.49, 'unidad', 0.5,  'lt',  0),
    ('Agua Cristal 1500ml',       'Cristal',     0.45, 0.85, 'unidad', 1.5,  'lt',  0),
    ('Coca-Cola 2L',              'Coca-Cola',   1.10, 1.99, 'litro',  2.0,  'lt',  0),
    ('Coca-Cola Light 2L',        'Coca-Cola',   1.10, 1.99, 'litro',  2.0,  'lt',  0),
    ('Fanta Naranja 2L',          'Fanta',       1.05, 1.89, 'litro',  2.0,  'lt',  0),
    ('Red Bull 250ml',            'Red Bull',    1.50, 2.75, 'unidad', 0.25, 'lt',  0),
    # Limpieza
    ('Fabuloso 1L',               'Fabuloso',    0.85, 1.59, 'litro',  1.0,  'lt',  0),
    ('Cloro Clorox 1L',           'Clorox',      0.70, 1.25, 'litro',  1.0,  'lt',  0),
    ('Detergente Ace 1kg',        'Ace',         1.80, 3.25, 'unidad', 1.0,  'kg',  0),
    ('Detergente Ariel 1kg',      'Ariel',       2.10, 3.75, 'unidad', 1.0,  'kg',  0),
    ('Downy 800ml',               'Downy',       2.50, 4.49, 'unidad', 0.8,  'lt',  0),
    # Cuidado personal
    ('Jabón Dove',                'Dove',        0.70, 1.25, 'unidad', 0.135,'kg',  0),
    ('Jabón Palmolive',           'Palmolive',   0.55, 0.99, 'unidad', 0.125,'kg',  0),
    ('Shampoo H&S 375ml',         'H&S',         2.80, 4.99, 'unidad', 0.375,'lt',  0),
    ('Shampoo Pantene 400ml',     'Pantene',     3.10, 5.49, 'unidad', 0.4,  'lt',  0),
    ('Desodorante Axe spray',     'Axe',         2.20, 3.99, 'unidad', 0.15, 'lt',  0),
    ('Desodorante Dove roll-on',  'Dove',        1.80, 3.25, 'unidad', 0.05, 'lt',  0),
    ('Colgate Triple 75ml',       'Colgate',     1.10, 1.99, 'unidad', 0.075,'kg',  0),
    ('Cepillo Oral-B',            'Oral-B',      1.20, 2.15, 'unidad', None, None,  0),
]

# Mapa producto → id_categoria
CATEGORIA_POR_PRODUCTO = {
    'Leche':          1,   # Leche entera
    'descremada':     4,   # Leche descremada
    'Queso blanco':   3,
    'Queso amarillo': 4,
    'Yogur':          5,
    'Arroz':          7,
    'integral':       8,
    'Frijoles negros':9,
    'Frijoles rojos': 10,
    'Carne molida':   11,
    'Bistec':         12,
    'Pechuga':        13,
    'Muslo':          14,
    'Chuleta':        15,
    'Pan molde blanco':16,
    'Pan molde integral':17,
    'Galletas Ritz':  18,
    'Galletas Oreo':  19,
    'Atún':           20,
    'Sardinas':       22,
    'Aceite Mazola':  23,
    'Aceite Iberia':  24,
    'Salsa':          25,
    'Mayonesa':       26,
    'Jugo Del Valle naranja':27,
    'Jugo Del Valle piña':   28,
    'Néctar':         29,
    'Agua Cristal 500ml':    30,
    'Agua Cristal 1500ml':   31,
    'Coca-Cola 2L':   32,
    'Coca-Cola Light':33,
    'Fanta':          34,
    'Red Bull':       35,
    'Fabuloso':       36,
    'Cloro':          37,
    'Detergente Ace': 38,
    'Detergente Ariel':39,
    'Downy':          40,
    'Jabón Dove':     41,
    'Jabón Palmolive':41,
    'Shampoo H&S':    42,
    'Shampoo Pantene':42,
    'Desodorante Axe':44,
    'Desodorante Dove':45,
    'Colgate':        46,
    'Cepillo':        47,
}

def get_categoria(nombre):
    for key, val in CATEGORIA_POR_PRODUCTO.items():
        if key in nombre:
            return val
    return 1  # default

def generar_articulos():
    rows = []
    prefijos = {
        'Alimentos': 'ALI', 'Bebidas': 'BEB',
        'Limpieza': 'LIM', 'Personal': 'PER'
    }
    ean_base = 7400000000001

    for i, (nombre, marca, costo, precio, unidad,
            contenido, u_cont, frio) in enumerate(PRODUCTOS_BASE, start=1):

        id_cat = get_categoria(nombre)
        # Determinar sección desde id_categoria
        if id_cat <= 26:
            pref = 'ALI'
        elif id_cat <= 35:
            pref = 'BEB'
        elif id_cat <= 40:
            pref = 'LIM'
        else:
            pref = 'PER'

        sku = f"{pref}-{str(i).zfill(3)}"
        ean = str(ean_base + i)

        # Variación pequeña en precios entre tiendas (realismo)
        costo_var  = round(costo  * random.uniform(0.97, 1.03), 2)
        precio_var = round(precio * random.uniform(0.98, 1.02), 2)

        rows.append({
            'id_articulo'   : i,
            'sku'           : sku,
            'ean'           : ean,
            'nombre'        : nombre,
            'descripcion'   : f"{nombre} - {marca}",
            'id_categoria'  : id_cat,
            'proveedor'     : f"Distribuidora {marca}",
            'marca'         : marca,
            'unidad_medida' : unidad,
            'contenido_neto': contenido,
            'unidad_contenido': u_cont,
            'costo'         : costo_var,
            'precio_base'   : precio_var,
            'requiere_frio' : frio,
            'activo'        : 1
        })

    return pd.DataFrame(rows)

# ============================================================
#  3. EMPLEADOS — ~4 por tienda con cédulas panameñas
# ============================================================

PUESTOS = ['Cajero', 'Cajero', 'Cajero', 'Supervisor', 'Gerente']
TURNOS  = ['Mañana', 'Tarde', 'Noche', 'Mañana', 'Mañana']

NOMBRES_M = ['Carlos','José','Miguel','Luis','Roberto','Juan','Ricardo','Alejandro','Fernando','David']
NOMBRES_F = ['María','Ana','Patricia','Laura','Carmen','Rosa','Sandra','Verónica','Diana','Claudia']
APELLIDOS  = ['Herrera','González','Martínez','Rodríguez','López','García','Pérez','Sánchez','Ramírez','Torres',
              'Díaz','Flores','Castro','Vargas','Morales','Reyes','Jiménez','Cruz','Mendoza','Ruiz']

def cedula_panama(i):
    """Genera cédula panameña formato 8-XXX-XXXX."""
    provincia = random.choice(['1','2','3','4','5','6','7','8','9'])
    tomo      = str(random.randint(100, 999))
    asiento   = str(random.randint(1000, 9999))
    return f"{provincia}-{tomo}-{asiento}"

def generar_empleados():
    rows = []
    id_emp = 1
    for id_tienda in IDS_TIENDA:
        n_empleados = random.randint(3, 5)
        for j in range(n_empleados):
            es_mujer = random.random() > 0.5
            nombre   = random.choice(NOMBRES_F if es_mujer else NOMBRES_M)
            apellido = random.choice(APELLIDOS)
            puesto   = PUESTOS[j] if j < len(PUESTOS) else 'Cajero'
            turno    = TURNOS[j]  if j < len(TURNOS)  else 'Tarde'

            rows.append({
                'id_empleado'  : id_emp,
                'cedula'       : cedula_panama(id_emp),
                'nombre'       : nombre,
                'apellido'     : apellido,
                'puesto'       : puesto,
                'id_tienda'    : id_tienda,
                'turno'        : turno,
                'fecha_ingreso': fake.date_between(
                                    start_date='-5y',
                                    end_date='-6m'
                                 ).isoformat(),
                'activo'       : 1
            })
            id_emp += 1

    return pd.DataFrame(rows)

# ============================================================
#  4. CLIENTES — 500 clientes del programa de fidelidad
# ============================================================

SEGMENTOS = {
    'BRONCE'  : (0,    500),
    'PLATA'   : (501,  2000),
    'ORO'     : (2001, 5000),
    'PLATINO' : (5001, 20000),
}

PROVINCIAS_PA = ['Panamá','Panamá Oeste','Chiriquí','Veraguas','Colón',
                 'Coclé','Herrera','Los Santos','Bocas del Toro','Darién']

def generar_clientes(n=500):
    rows = []
    for i in range(1, n + 1):
        # Distribución realista de segmentos
        rand = random.random()
        if rand < 0.60:
            segmento = 'BRONCE'
        elif rand < 0.85:
            segmento = 'PLATA'
        elif rand < 0.96:
            segmento = 'ORO'
        else:
            segmento = 'PLATINO'

        rango = SEGMENTOS[segmento]
        puntos_acum  = random.randint(rango[0], rango[1])
        puntos_canje = int(puntos_acum * random.uniform(0, 0.4))

        es_mujer = random.random() > 0.45
        nombre   = random.choice(NOMBRES_F if es_mujer else NOMBRES_M)
        apellido = random.choice(APELLIDOS)

        rows.append({
            'id_cliente'         : i,
            'codigo_cliente'     : f"CL-{str(i).zfill(6)}",
            'cedula'             : cedula_panama(i) if random.random() > 0.3 else None,
            'nombre'             : nombre,
            'apellido'           : apellido,
            'email'              : f"{nombre.lower()}.{apellido.lower()}{i}@gmail.com",
            'telefono'           : f"6{random.randint(100,999)}-{random.randint(1000,9999)}",
            'fecha_nacimiento'   : fake.date_of_birth(
                                       minimum_age=18,
                                       maximum_age=75
                                   ).isoformat(),
            'genero'             : 'F' if es_mujer else 'M',
            'provincia_residencia': random.choice(PROVINCIAS_PA),
            'fecha_registro'     : fake.date_between(
                                       start_date='2025-01-01',
                                       end_date='2026-04-06'
                                   ).isoformat(),
            'segmento'           : segmento,
            'puntos_acumulados'  : puntos_acum,
            'puntos_canjeados'   : puntos_canje,
            'activo'             : 1
        })

    return pd.DataFrame(rows)

# ============================================================
#  INSERCIÓN EN SQL SERVER
# ============================================================

def insertar_dataframe(df, tabla, columnas, sql_insert):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {tabla}")
    for _, row in df.iterrows():
        cursor.execute(sql_insert, tuple(row[c] for c in columnas))
    conn.commit()
    conn.close()
    print(f"✅ {tabla}: {len(df)} filas insertadas.")

def insertar_categorias(df):
    sql = """INSERT INTO dim.categoria
             (id_categoria, seccion, departamento, categoria, subcategoria, activa)
             VALUES (?,?,?,?,?,?)"""
    cols = ['id_categoria','seccion','departamento','categoria','subcategoria','activa']
    insertar_dataframe(df, 'dim.categoria', cols, sql)

def insertar_articulos(df):
    sql = """INSERT INTO dim.articulo
             (id_articulo, sku, ean, nombre, descripcion, id_categoria,
              proveedor, marca, unidad_medida, contenido_neto,
              unidad_contenido, costo, precio_base, requiere_frio, activo)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    cols = ['id_articulo','sku','ean','nombre','descripcion','id_categoria',
            'proveedor','marca','unidad_medida','contenido_neto',
            'unidad_contenido','costo','precio_base','requiere_frio','activo']
    insertar_dataframe(df, 'dim.articulo', cols, sql)

def insertar_empleados(df):
    sql = """INSERT INTO dim.empleado
             (id_empleado, cedula, nombre, apellido, puesto,
              id_tienda, turno, fecha_ingreso, activo)
             VALUES (?,?,?,?,?,?,?,?,?)"""
    cols = ['id_empleado','cedula','nombre','apellido','puesto',
            'id_tienda','turno','fecha_ingreso','activo']
    insertar_dataframe(df, 'dim.empleado', cols, sql)

def insertar_clientes(df):
    sql = """INSERT INTO dim.cliente
             (id_cliente, codigo_cliente, cedula, nombre, apellido,
              email, telefono, fecha_nacimiento, genero,
              provincia_residencia, fecha_registro, segmento,
              puntos_acumulados, puntos_canjeados, activo)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    cols = ['id_cliente','codigo_cliente','cedula','nombre','apellido',
            'email','telefono','fecha_nacimiento','genero',
            'provincia_residencia','fecha_registro','segmento',
            'puntos_acumulados','puntos_canjeados','activo']
    insertar_dataframe(df, 'dim.cliente', cols, sql)

# ============================================================
#  MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 55)
    print("  RetailPro — Generador de catálogo")
    print("=" * 55)

    print("\n[1/4] Generando categorías...")
    df_cat = generar_categorias()
    insertar_categorias(df_cat)

    print("\n[2/4] Generando artículos...")
    df_art = generar_articulos()
    insertar_articulos(df_art)
    print(f"       Artículos con frío: {df_art['requiere_frio'].sum()}")
    print(f"       Margen promedio:    {((df_art['precio_base']-df_art['costo'])/df_art['precio_base']*100).mean():.1f}%")

    print("\n[3/4] Generando empleados...")
    df_emp = generar_empleados()
    insertar_empleados(df_emp)
    print(f"       Total empleados: {len(df_emp)}")

    print("\n[4/4] Generando clientes...")
    df_cli = generar_clientes(500)
    insertar_clientes(df_cli)
    dist = df_cli['segmento'].value_counts()
    print(f"       BRONCE:  {dist.get('BRONCE',0)}")
    print(f"       PLATA:   {dist.get('PLATA',0)}")
    print(f"       ORO:     {dist.get('ORO',0)}")
    print(f"       PLATINO: {dist.get('PLATINO',0)}")

    print("\n✅ Catálogo completo generado y cargado en SQL Server.")