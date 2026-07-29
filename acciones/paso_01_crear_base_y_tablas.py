from config.conexion import obtener_conexion, BASE_DATOS_DEFAULT

def crear_base_y_tablas():
    print("=" * 60)
    print("ACCIONAL 1: CREACIÓN DE BASE DE DATOS Y ESTRUCTURA DDL")
    print("=" * 60)

    # 1. Verificar y crear la Base de Datos
    conexion_master = obtener_conexion(base_datos='master')
    cursor_master = conexion_master.cursor()
    
    cursor_master.execute("SELECT name FROM sys.databases WHERE name = ?", [BASE_DATOS_DEFAULT])
    existe_bd = cursor_master.fetchone()
    
    if not existe_bd:
        print(f"Creando base de datos '{BASE_DATOS_DEFAULT}'...")
        cursor_master.execute(f"CREATE DATABASE {BASE_DATOS_DEFAULT}")
        print(f"Base de datos '{BASE_DATOS_DEFAULT}' creada exitosamente.")
    else:
        print(f"La base de datos '{BASE_DATOS_DEFAULT}' ya existe.")
    
    conexion_master.close()

    # 2. Conectar a la base de datos ETL y crear tablas
    conexion = obtener_conexion(base_datos=BASE_DATOS_DEFAULT)
    cursor = conexion.cursor()

    tablas = [
        "fact_inscripciones", "dim_usuario", "dim_curso", "dim_campania",
        "etl_rechazos", "stg_usuarios", "stg_cursos", "stg_campanias",
        "stg_inscripciones", "stg_pagos_pasarela", "stg_reporte_campanias_doc"
    ]
    for tabla in tablas:
        cursor.execute(f"IF OBJECT_ID('{tabla}', 'U') IS NOT NULL DROP TABLE {tabla}")
    print("Limpieza de tablas anteriores completada.")

    # Tablas Staging
    cursor.execute("""
    CREATE TABLE stg_usuarios (
        id_usuario_origen VARCHAR(50),
        nombre VARCHAR(150),
        correo VARCHAR(150),
        ciudad VARCHAR(100),
        fecha_registro VARCHAR(50),
        canal_origen VARCHAR(50)
    )""")

    cursor.execute("""
    CREATE TABLE stg_cursos (
        id_curso_origen VARCHAR(50),
        nombre_curso VARCHAR(150),
        categoria VARCHAR(100),
        instructor VARCHAR(100),
        modalidad VARCHAR(50),
        costo_base VARCHAR(50)
    )""")

    cursor.execute("""
    CREATE TABLE stg_campanias (
        id_campania_origen VARCHAR(50),
        nombre_campania VARCHAR(150),
        canal VARCHAR(100),
        presupuesto VARCHAR(50),
        fecha_inicio VARCHAR(50),
        fecha_fin VARCHAR(50)
    )""")

    cursor.execute("""
    CREATE TABLE stg_inscripciones (
        id_inscripcion_origen VARCHAR(50),
        correo_usuario VARCHAR(150),
        nombre_curso VARCHAR(150),
        nombre_campania VARCHAR(150),
        fecha_inscripcion VARCHAR(50),
        monto_pagado VARCHAR(50),
        porcentaje_avance VARCHAR(50)
    )""")

    cursor.execute("""
    CREATE TABLE stg_pagos_pasarela (
        id_pago VARCHAR(50),
        correo VARCHAR(150),
        fecha_pago VARCHAR(50),
        monto VARCHAR(50),
        metodo_pago VARCHAR(50),
        referencia_pago VARCHAR(100),
        estatus_pago VARCHAR(50)
    )""")

    cursor.execute("""
    CREATE TABLE stg_reporte_campanias_doc (
        nombre_campania VARCHAR(150),
        canal_reportado VARCHAR(100),
        responsable VARCHAR(100),
        objetivo_manual VARCHAR(255),
        observacion VARCHAR(255)
    )""")

    # Tabla de Rechazos
    cursor.execute("""
    CREATE TABLE etl_rechazos (
        id_rechazo INT IDENTITY(1,1) PRIMARY KEY,
        tabla_origen VARCHAR(100),
        id_origen VARCHAR(100),
        motivo_rechazo VARCHAR(255),
        fecha_rechazo DATETIME DEFAULT GETDATE()
    )""")

    # Dimensiones
    cursor.execute("""
    CREATE TABLE dim_usuario (
        sk_usuario INT IDENTITY(1,1) PRIMARY KEY,
        id_usuario_origen INT,
        nombre VARCHAR(150),
        correo VARCHAR(150) UNIQUE,
        ciudad VARCHAR(100),
        fecha_registro DATE
    )""")

    cursor.execute("""
    CREATE TABLE dim_curso (
        sk_curso INT IDENTITY(1,1) PRIMARY KEY,
        id_curso_origen INT,
        nombre_curso VARCHAR(150),
        categoria VARCHAR(100),
        instructor VARCHAR(100),
        modalidad VARCHAR(50),
        costo_base DECIMAL(10,2)
    )""")

    cursor.execute("""
    CREATE TABLE dim_campania (
        sk_campania INT IDENTITY(1,1) PRIMARY KEY,
        id_campania_origen INT,
        nombre_campania VARCHAR(150),
        canal VARCHAR(100),
        presupuesto DECIMAL(10,2),
        responsable VARCHAR(100),
        objetivo_manual VARCHAR(255),
        fecha_inicio DATE,
        fecha_fin DATE
    )""")

    # Tabla de Hechos
    cursor.execute("""
    CREATE TABLE fact_inscripciones (
        sk_inscripcion INT IDENTITY(1,1) PRIMARY KEY,
        sk_usuario INT FOREIGN KEY REFERENCES dim_usuario(sk_usuario),
        sk_curso INT FOREIGN KEY REFERENCES dim_curso(sk_curso),
        sk_campania INT FOREIGN KEY REFERENCES dim_campania(sk_campania),
        id_inscripcion_origen INT,
        fecha_inscripcion DATE,
        monto_pagado DECIMAL(10,2),
        porcentaje_avance INT
    )""")

    conexion.close()
    print("Acción 1 finalizada exitosamente.\n")

if __name__ == "__main__":
    crear_base_y_tablas()
