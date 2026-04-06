# ============================================================
#  RetailPro | Daily Loader — Cargador diario automático
#  Genera ventas e inventario del día actual
#  Detecta alertas de stock y envía reporte por email
#  Autor: Ezequiel Díaz | GitHub: ediaz850
#
#  CÓMO USAR:
#  - Manual:    python 05_daily_loader.py
#  - Automático: Programador de tareas de Windows, cada día 11:00 PM
#
#  REQUISITOS:
#  - Haber ejecutado 01 → 04 primero (carga histórica)
#  - Configurar EMAIL_ORIGEN y EMAIL_DESTINO abajo
# ============================================================

import random
import smtplib
import pandas as pd
from datetime import date, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import (
    get_connection,
    FERIADOS_PANAMA, TEMPORADAS,
    MULTIPLICADOR_TEMPORADA,
    MULTIPLICADOR_FINDE,
    MULTIPLICADOR_FERIADO,
    IDS_TIENDA
)

# ============================================================
#  CONFIGURACIÓN DE EMAIL
#  Cambia estos valores por los tuyos
#  Usa una contraseña de aplicación de Gmail (no tu contraseña normal)
#  Gmail: Cuenta → Seguridad → Verificación en 2 pasos → Contraseñas de app
# ============================================================

EMAIL_ORIGEN  = "tu_correo@gmail.com"       # cambia esto
EMAIL_DESTINO = "ezequiel.diazperez@outlook.com"
EMAIL_PASSWORD = "tu_contraseña_de_app"     # contraseña de app Gmail

ENVIAR_EMAIL = False   # Cambia a True cuando configures el email

# ============================================================
#  PARÁMETROS (mismos que script 03 y 04)
# ============================================================

VOLUMEN_BASE_TIENDA = {
    1: 120, 2: 85, 3: 45, 4: 90, 5: 75
}

PCT_ARTICULOS_ACTIVOS = {
    1: 0.85, 2: 0.75, 3: 0.55, 4: 0.78, 5: 0.72
}

ROTACION_CATEGORIA = {
    1: 2.5,  2: 2.0,  3: 1.5,  4: 1.3,  5: 1.8,
    6: 1.6,  7: 3.0,  8: 1.2,  9: 2.2,  10: 2.0,
    11: 1.8, 12: 1.4, 13: 2.0, 14: 1.8, 15: 1.3,
    16: 2.5, 17: 1.5, 18: 1.8, 19: 2.0, 20: 2.2,
    21: 1.8, 22: 1.5, 23: 1.6, 24: 1.5, 25: 1.8,
    26: 1.6, 27: 2.0, 28: 1.8, 29: 1.5, 30: 3.5,
    31: 2.5, 32: 2.8, 33: 1.5, 34: 2.0, 35: 1.2,
    36: 1.8, 37: 1.5, 38: 1.6, 39: 1.4, 40: 1.2,
    41: 1.8, 42: 1.5, 43: 1.2, 44: 1.3, 45: 1.2,
    46: 1.8, 47: 0.8
}

STOCK_MINIMO_CATEGORIA = {
    1: 50,  2: 40,  3: 30,  4: 25,  5: 35,
    6: 30,  7: 80,  8: 25,  9: 50,  10: 45,
    11: 40, 12: 30, 13: 45, 14: 40, 15: 25,
    16: 50, 17: 25, 18: 35, 19: 40, 20: 45,
    21: 40, 22: 30, 23: 35, 24: 30, 25: 35,
    26: 30, 27: 40, 28: 35, 29: 25, 30: 80,
    31: 60, 32: 70, 33: 30, 34: 40, 35: 20,
    36: 35, 37: 30, 38: 40, 39: 35, 40: 25,
    41: 40, 42: 30, 43: 25, 44: 30, 45: 25,
    46: 35, 47: 20
}

NOMBRES_TIENDA = {
    1: 'RetailPro Marbella',
    2: 'RetailPro La Chorrera',
    3: 'RetailPro Arraiján',
    4: 'RetailPro David',
    5: 'RetailPro Santiago'
}

# ============================================================
#  FUNCIONES DE SOPORTE
# ============================================================

def get_multiplicador_dia(fecha_str, fecha_obj):
    mes       = fecha_obj.month
    dia       = fecha_obj.day
    es_finde  = fecha_obj.weekday() >= 5
    es_feriado= fecha_str in FERIADOS_PANAMA
    temporada = TEMPORADAS[mes]

    if dia in (14, 15, 29, 30) and temporada == 'Normal':
        temporada = 'Quincena'

    mult = MULTIPLICADOR_TEMPORADA.get(temporada, 1.0)
    if es_finde:
        mult *= MULTIPLICADOR_FINDE
    if es_feriado:
        mult *= MULTIPLICADOR_FERIADO
    mult *= random.uniform(0.92, 1.08)
    return mult, temporada, es_finde, es_feriado

def verificar_dia_ya_cargado(cursor, id_tiempo):
    """Verifica si el día ya fue cargado para evitar duplicados."""
    cursor.execute(
        "SELECT COUNT(*) FROM fact.ventas WHERE id_tiempo = ?",
        id_tiempo
    )
    return cursor.fetchone()[0] > 0

# ============================================================
#  CARGA DIARIA DE VENTAS
# ============================================================

def cargar_ventas_hoy(conn, cursor, fecha_hoy, id_tiempo):
    df_articulos = pd.read_sql(
        "SELECT id_articulo, id_categoria, precio_base FROM dim.articulo WHERE activo = 1",
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

    id_clientes    = df_clientes['id_cliente'].tolist()
    emp_por_tienda = {
        t: df_empleados[df_empleados['id_tienda'] == t]['id_empleado'].tolist()
        for t in IDS_TIENDA
    }

    fecha_str = fecha_hoy.isoformat()
    mult_dia, temporada, es_finde, es_feriado = get_multiplicador_dia(
        fecha_str, fecha_hoy
    )

    sql_insert = """
        INSERT INTO fact.ventas (
            id_tiempo, id_tienda, id_articulo, id_empleado,
            id_cliente, id_promocion,
            cantidad, precio_unitario, descuento_pct, puntos_generados
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """

    resumen_tiendas = {}
    batch = []

    for id_tienda in IDS_TIENDA:
        vol_base   = VOLUMEN_BASE_TIENDA[id_tienda]
        pct        = PCT_ARTICULOS_ACTIVOS[id_tienda]
        n_arts     = int(len(df_articulos) * pct)
        arts_hoy   = df_articulos.sample(n=n_arts)
        emp_tienda = emp_por_tienda.get(id_tienda, [1])

        monto_tienda = 0
        uds_tienda   = 0

        for _, art in arts_hoy.iterrows():
            id_art   = int(art['id_articulo'])
            id_cat   = int(art['id_categoria'])
            precio   = float(art['precio_base'])
            rot      = ROTACION_CATEGORIA.get(id_cat, 1.0)
            cantidad = max(1, int(
                vol_base * rot * mult_dia * random.uniform(0.5, 1.5)
            ))

            # Descuento ocasional
            descuento = 0.0
            if (es_finde or es_feriado) and random.random() < 0.15:
                descuento = float(random.choice([5.0, 10.0, 15.0, 20.0]))
            elif random.random() < 0.05:
                descuento = float(random.choice([5.0, 10.0]))

            id_cliente = random.choice(id_clientes) if random.random() < 0.30 else None
            id_emp     = random.choice(emp_tienda)
            monto_neto = cantidad * precio * (1 - descuento / 100)
            puntos     = int(monto_neto) if id_cliente else 0

            monto_tienda += monto_neto
            uds_tienda   += cantidad

            batch.append((
                id_tiempo, id_tienda, id_art, id_emp,
                id_cliente, None,
                cantidad, round(precio, 2), descuento, puntos
            ))

        resumen_tiendas[id_tienda] = {
            'monto': round(monto_tienda, 2),
            'unidades': uds_tienda
        }

    cursor.executemany(sql_insert, batch)
    conn.commit()

    return resumen_tiendas, temporada, es_finde, es_feriado

# ============================================================
#  ACTUALIZACIÓN DE INVENTARIO
# ============================================================

def actualizar_inventario_hoy(conn, cursor, fecha_hoy, id_tiempo):
    df_articulos = pd.read_sql(
        "SELECT id_articulo, id_categoria FROM dim.articulo WHERE activo = 1",
        conn
    )

    # Stock final del día anterior por tienda/artículo
    ayer_id = int(
        (fecha_hoy.replace(day=fecha_hoy.day) -
         __import__('datetime').timedelta(days=1)
        ).strftime('%Y%m%d')
    )

    df_stock_ayer = pd.read_sql(
        f"""SELECT id_tienda, id_articulo, stock_final
            FROM fact.inventario
            WHERE id_tiempo = {ayer_id}""",
        conn
    )

    stock_ayer_idx = df_stock_ayer.set_index(
        ['id_tienda', 'id_articulo']
    )['stock_final'].to_dict()

    # Ventas de hoy
    df_ventas_hoy = pd.read_sql(
        f"""SELECT id_tienda, id_articulo, SUM(cantidad) as vendido
            FROM fact.ventas
            WHERE id_tiempo = {id_tiempo}
            GROUP BY id_tienda, id_articulo""",
        conn
    )
    ventas_hoy_idx = df_ventas_hoy.set_index(
        ['id_tienda', 'id_articulo']
    )['vendido'].to_dict()

    sql_inv = """
        INSERT INTO fact.inventario (
            id_tiempo, id_tienda, id_articulo,
            stock_inicial, unidades_vendidas, unidades_recibidas,
            stock_final, stock_minimo
        ) VALUES (?,?,?,?,?,?,?,?)
    """

    alertas  = []
    batch    = []

    for id_tienda in IDS_TIENDA:
        for _, art in df_articulos.iterrows():
            id_art  = int(art['id_articulo'])
            id_cat  = int(art['id_categoria'])

            stock_min = STOCK_MINIMO_CATEGORIA.get(id_cat, 25)
            stock_ini = int(stock_ayer_idx.get((id_tienda, id_art), stock_min * 3))
            vendido   = int(ventas_hoy_idx.get((id_tienda, id_art), 0))

            # Reposición si stock bajo
            recibido = 0
            if stock_ini - vendido <= stock_min:
                recibido = int(stock_min * random.uniform(3, 5))

            stock_fin = max(0, stock_ini - vendido + recibido)

            if stock_fin <= stock_min:
                alertas.append({
                    'tienda'  : NOMBRES_TIENDA[id_tienda],
                    'id_art'  : id_art,
                    'stock'   : stock_fin,
                    'minimo'  : stock_min
                })

            batch.append((
                id_tiempo, id_tienda, id_art,
                stock_ini, vendido, recibido,
                stock_fin, stock_min
            ))

    cursor.executemany(sql_inv, batch)
    conn.commit()

    return alertas

# ============================================================
#  REPORTE POR EMAIL
# ============================================================

def generar_html_reporte(fecha_hoy, resumen_tiendas, alertas,
                          temporada, es_finde, es_feriado):
    total_monto = sum(v['monto'] for v in resumen_tiendas.values())
    total_uds   = sum(v['unidades'] for v in resumen_tiendas.values())
    n_alertas   = len(alertas)

    contexto = []
    if es_feriado:
        contexto.append("🎉 Día feriado")
    if es_finde:
        contexto.append("📅 Fin de semana")
    if temporada != 'Normal':
        contexto.append(f"📊 Temporada: {temporada}")
    contexto_str = " · ".join(contexto) if contexto else "Día normal"

    filas_tiendas = ""
    for id_t, datos in resumen_tiendas.items():
        filas_tiendas += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #eee;">
                {NOMBRES_TIENDA[id_t]}
            </td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">
                ${datos['monto']:,.2f}
            </td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">
                {datos['unidades']:,}
            </td>
        </tr>"""

    filas_alertas = ""
    if alertas:
        for a in alertas[:10]:  # máximo 10 alertas en el email
            filas_alertas += f"""
            <tr>
                <td style="padding:6px;color:#cc0000;">{a['tienda']}</td>
                <td style="padding:6px;">Artículo #{a['id_art']}</td>
                <td style="padding:6px;text-align:right;">{a['stock']}</td>
                <td style="padding:6px;text-align:right;">{a['minimo']}</td>
            </tr>"""
        if len(alertas) > 10:
            filas_alertas += f"""
            <tr>
                <td colspan="4" style="padding:6px;color:#999;">
                    ... y {len(alertas)-10} alertas más
                </td>
            </tr>"""

    alertas_section = ""
    if alertas:
        alertas_section = f"""
        <h3 style="color:#cc0000;">⚠️ Alertas de stock bajo ({n_alertas})</h3>
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
            <tr style="background:#fff0f0;">
                <th style="padding:6px;text-align:left;">Tienda</th>
                <th style="padding:6px;text-align:left;">Artículo</th>
                <th style="padding:6px;text-align:right;">Stock actual</th>
                <th style="padding:6px;text-align:right;">Stock mínimo</th>
            </tr>
            {filas_alertas}
        </table>"""

    html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;">
        <div style="background:#1a1a2e;color:white;padding:20px;border-radius:8px 8px 0 0;">
            <h2 style="margin:0;">📊 RetailPro — Reporte Diario</h2>
            <p style="margin:5px 0 0;opacity:0.8;">{fecha_hoy.strftime('%A %d de %B, %Y')}</p>
            <p style="margin:5px 0 0;opacity:0.6;font-size:13px;">{contexto_str}</p>
        </div>

        <div style="padding:20px;background:#f9f9f9;">
            <div style="display:flex;gap:20px;margin-bottom:20px;">
                <div style="background:white;padding:15px;border-radius:8px;
                            flex:1;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size:24px;font-weight:bold;color:#1a1a2e;">
                        ${total_monto:,.2f}
                    </div>
                    <div style="color:#666;font-size:13px;">Ventas totales</div>
                </div>
                <div style="background:white;padding:15px;border-radius:8px;
                            flex:1;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size:24px;font-weight:bold;color:#1a1a2e;">
                        {total_uds:,}
                    </div>
                    <div style="color:#666;font-size:13px;">Unidades vendidas</div>
                </div>
                <div style="background:white;padding:15px;border-radius:8px;
                            flex:1;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size:24px;font-weight:bold;
                                color:{'#cc0000' if n_alertas > 0 else '#00aa00'};">
                        {n_alertas}
                    </div>
                    <div style="color:#666;font-size:13px;">Alertas de stock</div>
                </div>
            </div>

            <h3 style="color:#1a1a2e;">🏪 Ventas por tienda</h3>
            <table style="width:100%;border-collapse:collapse;">
                <tr style="background:#1a1a2e;color:white;">
                    <th style="padding:8px;text-align:left;">Tienda</th>
                    <th style="padding:8px;text-align:right;">Ventas ($)</th>
                    <th style="padding:8px;text-align:right;">Unidades</th>
                </tr>
                {filas_tiendas}
            </table>

            {alertas_section}

            <p style="margin-top:20px;color:#999;font-size:12px;">
                Generado automáticamente por RetailPro Analytics Pipeline<br>
                {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
    </body></html>
    """
    return html

def enviar_email(fecha_hoy, resumen_tiendas, alertas,
                 temporada, es_finde, es_feriado):
    if not ENVIAR_EMAIL:
        print("  📧 Email desactivado. Cambia ENVIAR_EMAIL = True para activarlo.")
        return

    try:
        html = generar_html_reporte(
            fecha_hoy, resumen_tiendas, alertas,
            temporada, es_finde, es_feriado
        )
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"RetailPro | Reporte {fecha_hoy.strftime('%d/%m/%Y')} — ${sum(v['monto'] for v in resumen_tiendas.values()):,.0f}"
        msg['From']    = EMAIL_ORIGEN
        msg['To']      = EMAIL_DESTINO
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ORIGEN, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_ORIGEN, EMAIL_DESTINO, msg.as_string())

        print(f"  📧 Reporte enviado a {EMAIL_DESTINO}")

    except Exception as e:
        print(f"  ❌ Error enviando email: {e}")

# ============================================================
#  MAIN
# ============================================================

if __name__ == '__main__':
    fecha_hoy = date.today()
    id_tiempo = int(fecha_hoy.strftime('%Y%m%d'))
    fecha_str = fecha_hoy.isoformat()

    print("=" * 55)
    print(f"  RetailPro — Daily Loader")
    print(f"  Fecha: {fecha_hoy.strftime('%A %d de %B, %Y')}")
    print("=" * 55)

    conn   = get_connection()
    cursor = conn.cursor()

    # Verificar que el día existe en dim.tiempo
    cursor.execute(
        "SELECT COUNT(*) FROM dim.tiempo WHERE id_tiempo = ?",
        id_tiempo
    )
    if cursor.fetchone()[0] == 0:
        print(f"\n❌ Error: {fecha_str} no existe en dim.tiempo.")
        print("   Verifica que dim.tiempo cubre hasta {FECHA_FIN_PRED}.")
        conn.close()
        exit(1)

    # Verificar si ya fue cargado hoy
    if verificar_dia_ya_cargado(cursor, id_tiempo):
        print(f"\n⚠️  El día {fecha_str} ya fue cargado.")
        print("   Si quieres recargar, ejecuta primero:")
        print(f"   DELETE FROM fact.ventas WHERE id_tiempo = {id_tiempo}")
        print(f"   DELETE FROM fact.inventario WHERE id_tiempo = {id_tiempo}")
        conn.close()
        exit(0)

    # 1. Cargar ventas del día
    print(f"\n[1/3] Cargando ventas de hoy ({fecha_str})...")
    resumen, temporada, es_finde, es_feriado = cargar_ventas_hoy(
        conn, cursor, fecha_hoy, id_tiempo
    )

    total_dia = sum(v['monto'] for v in resumen.values())
    print(f"       Total ventas: ${total_dia:,.2f}")
    for id_t, datos in resumen.items():
        print(f"       {NOMBRES_TIENDA[id_t]}: ${datos['monto']:,.2f}")

    # 2. Actualizar inventario
    print(f"\n[2/3] Actualizando inventario...")
    alertas = actualizar_inventario_hoy(conn, cursor, fecha_hoy, id_tiempo)
    print(f"       Alertas de stock bajo: {len(alertas)}")

    conn.close()

    # 3. Enviar reporte
    print(f"\n[3/3] Enviando reporte diario...")
    enviar_email(
        fecha_hoy, resumen, alertas,
        temporada, es_finde, es_feriado
    )

    print(f"\n{'='*55}")
    print(f"  ✅ Daily Loader completado: {fecha_str}")
    print(f"  💰 Ventas del día: ${total_dia:,.2f}")
    print(f"  ⚠️  Alertas activas: {len(alertas)}")
    print(f"{'='*55}")