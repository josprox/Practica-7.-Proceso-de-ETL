# Pipeline ETL y Data Warehouse Dimensional (SQL Server & Python)

Este repositorio contiene un pipeline modular de **ETL (Extract, Transform, Load)** desarrollado en Python y conectado a Microsoft SQL Server. El sistema extrae datos de fuentes heterogéneas en bruto (Excel, CSV, Word), los procesa mediante reglas de limpieza y calidad, captura registros anómalos en una tabla de auditoría de rechazos y construye un Data Warehouse bajo un **Modelo Estrella (Star Schema)**.

---

## 📁 Estructura del Código

El proyecto está organizado por capas de responsabilidad para facilitar el mantenimiento y ejecución independiente:

```text
.
├── .env.example                                # Plantilla de variables de entorno
├── .gitignore                                  # Exclusión de credenciales y cache de Python
├── requirements.txt                            # Dependencias del proyecto
├── ejecutar_todo.py                            # Orquestador principal del pipeline
├── Código de consultas.sql                     # Script SQL nativo ejecutable en SSMS / Azure Data Studio
│
├── config/
│   └── conexion.py                             # Carga de credenciales con python-dotenv y conexión a SQL Server
│
├── limpiadores/
│   └── normalizadores.py                       # Funciones de parseo de fechas, montos y estandarización de texto
│
├── inserciones/
│   └── cargador_lotes.py                       # Ejecución de inserciones SQL masivas por lotes
│
└── acciones/
    ├── paso_01_crear_base_y_tablas.py          # DDL: Creación de BD, tablas Staging, Rechazos, Dimensiones y Hechos
    ├── paso_02_cargar_staging.py               # Extracción de fuentes crudas (XLSX, CSV, DOCX) a la capa Staging
    ├── paso_03_ejecutar_transformacion_y_etl.py # ETL: Transformación, reglas de calidad, auditoría y carga dimensional
    └── paso_04_generar_reportes.py             # Consultas SQL e impresión de reportes gerenciales
```

---

## ⚙️ Descripción de los Módulos

### 1. `config/conexion.py`
Maneja la autenticación y conectividad con el servidor SQL Server. Utiliza `python-dotenv` para extraer `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` y `DB_DRIVER` sin exponer claves en el código fuente.

### 2. `limpiadores/normalizadores.py`
Proporciona funciones puras para la limpieza de datos:
- **`comillas_sql(valor)`**: Escapa cadenas para prevenir inyecciones SQL.
- **`parsear_monto(valor_raw)`**: Extrae valores numéricos a `float` eliminando texto/símbolos (`$`, `MXN`).
- **`parsear_fecha(valor_raw)`**: Estandariza fechas heterogéneas al formato `YYYY-MM-DD`.
- **`normalizar_ciudad(ciudad_raw)`**: Homologa nombres de entidades federativas (*CDMX, EdoMex, Pue., Qro.*).
- **`normalizar_canal(canal_raw)`**: Estandariza canales de marketing (*Instagram, Facebook, Sitio Web, Google Ads, Referido*).
- **`normalizar_modalidad(modalidad_raw)`**: Estandariza modalidades de cursos (*En vivo, Grabado, Híbrido*).

### 3. `inserciones/cargador_lotes.py`
Optimiza el rendimiento de la carga ejecutando instrucciones `INSERT INTO ... VALUES (...)` agrupadas en lotes (batch processing de 50 filas) hacia SQL Server.

### 4. `acciones/paso_01_crear_base_y_tablas.py`
Ejecuta las sentencias DDL para crear la estructura relacional:
- **Capa Staging**: `stg_usuarios`, `stg_cursos`, `stg_campanias`, `stg_inscripciones`, `stg_pagos_pasarela`, `stg_reporte_campanias_doc`.
- **Capa Auditoría**: `etl_rechazos` (`id_rechazo`, `tabla_origen`, `id_origen`, `motivo_rechazo`, `fecha_rechazo`).
- **Data Warehouse**: `dim_usuario`, `dim_curso`, `dim_campania` y la tabla de hechos `fact_inscripciones`.

### 5. `acciones/paso_02_cargar_staging.py`
Lectura masiva de archivos crudos y vuelco sin restricciones a las tablas `stg_`:
- Extracción de pestañas desde `campusfit_fuentes.xlsx` usando `openpyxl`.
- Extracción del archivo plano `pagos_pasarela.csv` usando `csv`.
- Extracción de datos cualitativos desde `reporte_campanias.docx` usando `python-docx`.

### 6. `acciones/paso_03_ejecutar_transformacion_y_etl.py`
Aplica el motor de reglas de negocio y calidad:
- **Transformación de Usuarios**: Convierte correos a minúsculas, elimina espacios, rechaza correos nulos o sin `@` y elimina duplicados.
- **Transformación de Cursos y Campañas**: Parsea montos numéricos, normaliza modalidades y canales, e integra responsable/objetivo del archivo Word.
- **Carga de Hechos con Lookups**: Asigna surrogate keys (`sk_usuario`, `sk_curso`, `sk_campania`) mediante búsquedas por clave natural y rechaza registros huérfanos, fechas corruptas, montos `&le; 0` o inscripciones duplicadas.
- **Auditoría**: Inserta automáticamente todos los rechazos detectados en `etl_rechazos`.

### 7. `acciones/paso_04_generar_reportes.py`
Ejecuta y formatea en consola las 4 consultas analíticas solicitadas:
- Tabla de control del proceso ETL (recuento de filas en cada etapa).
- Reporte de inscripciones válidas e ingresos por campaña.
- Reporte de ingresos, avance promedio y modalidad por curso.
- Reporte detallado del log de rechazados por el ETL.

### 8. `ejecutar_todo.py`
Script orquestador principal que ejecuta la secuencia de los pasos 01 a 04 capturando métricas de tiempo de ejecución y excepciones globales.

---

## 🛠️ Instalación y Configuración

### 1. Clonar el repositorio e instalar dependencias
```bash
git clone https://github.com/josprox/Practica-7.-Proceso-de-ETL.git
cd Practica-7.-Proceso-de-ETL
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example`:

```env
DB_HOST=sqlserv.joss.red
DB_USER=joss
DB_PASSWORD=TuPasswordAqui
DB_NAME=db_campusfit_etl
DB_DRIVER=ODBC Driver 18 for SQL Server
```

---

## 🚀 Ejecución del Pipeline

Para correr el pipeline completo de inicio a fin:

```bash
python ejecutar_todo.py
```

También puedes ejecutar cualquier paso de forma individual:

```bash
python acciones/paso_01_crear_base_y_tablas.py
python acciones/paso_02_cargar_staging.py
python acciones/paso_03_ejecutar_transformacion_y_etl.py
python acciones/paso_04_generar_reportes.py
```
