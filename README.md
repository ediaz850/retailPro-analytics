# 🛒 RetailPro Analytics

> Pipeline de Business Intelligence end-to-end para una cadena retail ficticia en Panamá.
> Datos sintéticos generados con Python sobre un modelo dimensional real en SQL Server 2022.

![SQL Server](https://img.shields.io/badge/SQL%20Server-CC2927?style=flat&logo=microsoft-sql-server&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=flat&logo=powerbi&logoColor=black)
![Qlik Sense](https://img.shields.io/badge/Qlik%20Sense-009845?style=flat&logo=qlik&logoColor=white)
![Status](https://img.shields.io/badge/Status-En%20desarrollo-orange?style=flat)

---

## 📌 ¿Qué es este proyecto?

RetailPro Analytics simula el ecosistema de datos de una cadena de 5 tiendas en Panamá.
El objetivo es demostrar competencias en modelado dimensional, generación de pipelines
automatizados, análisis descriptivo, diagnóstico y predictivo — usando herramientas
del stack BI profesional.

**Todos los datos son sintéticos** y fueron generados con Python para fines de portfolio.
Los nombres de provincias, distritos y corregimientos corresponden a la geografía real
de Panamá para habilitar análisis geoespacial.

---

## 🏗️ Arquitectura del proyecto

```
Generadores Python
      │
      ▼
SQL Server 2022 ── Star Schema (dim + fact)
      │
      ├── Power BI  ── Dashboards descriptivos y diagnósticos
      └── Qlik Sense ── Análisis exploratorio avanzado
```

---

## 📊 Modelo de datos — Star Schema

```
dim.categoria ──┐
dim.tiempo    ──┤
dim.tienda    ──┼──► fact.ventas ──► fact.fidelidad
dim.articulo  ──┤
dim.empleado  ──┤
dim.cliente   ──┤
dim.promocion ──┘

dim.tienda   ──┐
dim.articulo ──┼──► fact.inventario
dim.tiempo   ──┘

dim.tienda   ──┐
dim.articulo ──┼──► fact.reposicion
dim.tiempo   ──┘
```

### Dimensiones

| Tabla | Descripción | Filas aprox. |
|---|---|---|
| `dim.categoria` | Árbol: sección → depto → categoría → subcategoría | 47 |
| `dim.articulo` | Productos con EAN, SKU, marca, costos y margen | 51 |
| `dim.tienda` | 5 tiendas en ubicaciones reales de Panamá | 5 |
| `dim.tiempo` | Calendario 2025-2026 con feriados panameños | 731 |
| `dim.empleado` | Vendedores con cédula panameña | ~20 |
| `dim.cliente` | Programa de fidelidad: Bronce, Plata, Oro, Platino | 500 |
| `dim.promocion` | Ofertas con vigencia y tipo | variable |

### Hechos

| Tabla | Descripción | Filas aprox. |
|---|---|---|
| `fact.ventas` | Ventas diarias consolidadas por tienda/artículo | ~480K |
| `fact.inventario` | Snapshot diario de stock con alertas automáticas | ~480K |
| `fact.fidelidad` | Movimientos de puntos por cliente | variable |
| `fact.reposicion` | Órdenes de compra AUTO y MANUAL | variable |

---

## 🗺️ Tiendas RetailPro

| Código | Nombre | Distrito | Provincia | Formato |
|---|---|---|---|---|
| RP-001 | RetailPro Marbella | Panamá | Panamá | Flagship |
| RP-002 | RetailPro La Chorrera | La Chorrera | Panamá Oeste | Supertienda |
| RP-003 | RetailPro Arraiján | Arraiján | Panamá Oeste | Express |
| RP-004 | RetailPro David | David | Chiriquí | Supertienda |
| RP-005 | RetailPro Santiago | Santiago | Veraguas | Supertienda |

---

## 📁 Estructura del repositorio

```
retailpro-analytics/
│
├── README.md
├── .gitignore
│
├── sql/
│   ├── ddl/
│   │   └── retailpro_ddl_v2.sql      # DDL completo — 11 tablas
│   └── inserts/
│       └── insert_tiendas.sql        # INSERT de las 5 tiendas
│
├── python/
│   ├── 00_config.py                  # Configuración central y conexión
│   ├── 01_generate_dim_tiempo.py     # Calendario 2025-2026
│   ├── 02_generate_dim_catalogo.py   # Categorías, artículos, empleados, clientes
│   ├── 03_generate_fact_ventas.py    # Ventas históricas consolidadas
│   ├── 04_generate_fact_inventario.py# Snapshots diarios de inventario
│   └── 05_daily_loader.py            # Cargador diario automático + reporte email
│
├── geojson/
│   ├── panama_provincias.json        # TopoJSON provincias de Panamá
│   └── panama_distritos.json         # TopoJSON distritos de Panamá
│
├── powerbi/                          # Dashboards Power BI (.pbix) — próximamente
└── docs/
    └── modelo_datos.png              # Diagrama del star schema — próximamente
```

---

## 🚀 Cómo ejecutar el proyecto

### Requisitos previos

```bash
pip install pyodbc pandas faker
```

- SQL Server 2022 (local o Express)
- SQL Server Management Studio (SSMS)
- Python 3.8+
- ODBC Driver 17 for SQL Server

### Orden de ejecución

```bash
# 1. Crear la base de datos y el modelo dimensional
# Ejecutar en SSMS: sql/ddl/retailpro_ddl_v2.sql
# Ejecutar en SSMS: sql/inserts/insert_tiendas.sql

# 2. Configurar conexión
# Editar python/00_config.py → ajustar SERVER si es necesario

# 3. Cargar datos históricos (ejecutar en orden)
python dimtiempo.py
python dimcatalogo.py
python factsventas.py       # ~3-5 minutos
python factsinventario.py  # ~5-8 minutos

# 4. Carga diaria (ejecutar cada día)
python 05_daily_loader.py
```

### Automatización del daily loader

En Windows — Programador de tareas:
```
Acción: Iniciar programa
Programa: python
Argumentos: C:\ruta\al\proyecto\python\05_daily_loader.py
Hora: 11:00 PM todos los días
```

---

## 📈 KPIs y análisis disponibles

### Análisis descriptivo (¿qué pasó?)
- Ventas totales por tienda, categoría, mes y temporada
- Margen bruto por sección y subcategoría
- Rotación de inventario por artículo
- Comparativo 2025 vs 2026

### Análisis diagnóstico (¿por qué pasó?)
- Correlación entre feriados panameños y picos de venta
- Efecto quincena en el comportamiento de compra
- Artículos con stockout recurrente
- Performance por tienda vs benchmark de la cadena

### Análisis predictivo (¿qué va a pasar?) — en desarrollo
- Forecast de ventas Mayo–Diciembre 2026 con Prophet
- Clasificación de clientes por riesgo de abandono
- Predicción de demanda por artículo para optimizar reposición

---

## 🌍 Datos geoespaciales

El proyecto incluye archivos TopoJSON con la división político-administrativa
de Panamá a nivel de provincia y distrito. Esto permite construir mapas de calor
de ventas geolocalizados en Power BI y Qlik Sense.

Los nombres de `PROVINCIA` y `DISTRITO` en `dim.tienda` coinciden exactamente
con los campos del TopoJSON para habilitar JOINs geográficos sin transformación.

---

## 🛠️ Stack técnico

| Capa | Tecnología |
|---|---|
| Base de datos | SQL Server 2022 |
| Modelado | Star Schema con schemas `dim` y `fact` |
| Generación de datos | Python — pandas, faker, pyodbc |
| Análisis predictivo | Python — Prophet, scikit-learn (próximamente) |
| Visualización | Power BI Desktop |
| Análisis exploratorio | Qlik Sense |
| Versionado | Git + GitHub |

---

## 👤 Autor

**Ezequiel Díaz**
BI Analyst · Retail & Datos Públicos · Panamá 🇵🇦

[![GitHub](https://img.shields.io/badge/GitHub-ediaz850-181717?style=flat&logo=github)](https://github.com/ediaz850)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Ezequiel%20Díaz-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/ezequiel-díaz-pérez-76a775189/)

---

> *Este proyecto es parte de un portfolio profesional de Business Intelligence.
> Los datos son 100% sintéticos y no representan ninguna empresa real.*
