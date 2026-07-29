from config.conexion import obtener_conexion

def generar_reportes():
    print("=" * 60)
    print("ACCIÓN 4: CONSULTAS Y GENERACIÓN DE REPORTES")
    print("=" * 60)

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # 5. TABLA DE CONTROL DEL PROCESO ETL
    print("\n" + "=" * 60)
    print("5. TABLA DE CONTROL DEL PROCESO ETL")
    print("=" * 60)
    cursor.execute("""
        SELECT 'src_usuarios' AS Tabla, COUNT(*) AS Total FROM stg_usuarios
        UNION ALL
        SELECT 'stg_usuarios', COUNT(*) FROM stg_usuarios
        UNION ALL
        SELECT 'dim_usuario', COUNT(*) FROM dim_usuario
        UNION ALL
        SELECT 'fact_inscripciones', COUNT(*) FROM fact_inscripciones
        UNION ALL
        SELECT 'etl_rechazos', COUNT(*) FROM etl_rechazos
    """)
    filas_ctrl = cursor.fetchall()
    print(f"{'Tabla':<22} | {'Total Registros':<15}")
    print("-" * 40)
    for r in filas_ctrl:
        print(f"{r[0]:<22} | {r[1]:<15}")

    # 6. REPORTE DE INSCRIPCIONES VÁLIDAS POR CAMPAÑA
    print("\n" + "=" * 60)
    print("6. REPORTE DE INSCRIPCIONES VÁLIDAS POR CAMPAÑA")
    print("=" * 60)
    cursor.execute("""
        SELECT 
            c.nombre_campania AS Campania,
            c.canal AS Canal,
            COUNT(f.sk_inscripcion) AS Total_Inscripciones,
            SUM(f.monto_pagado) AS Ingresos_Totales
        FROM fact_inscripciones f
        JOIN dim_campania c ON f.sk_campania = c.sk_campania
        GROUP BY c.nombre_campania, c.canal
        ORDER BY Ingresos_Totales DESC
    """)
    filas_camp = cursor.fetchall()
    print(f"{'Campaña':<25} | {'Canal':<12} | {'Total Inscripciones':<20} | {'Ingresos Totales':<18}")
    print("-" * 80)
    for r in filas_camp:
        print(f"{r[0]:<25} | {r[1]:<12} | {r[2]:<20} | ${r[3]:,.2f}")

    # 7. REPORTE DE INGRESOS POR CURSO
    print("\n" + "=" * 60)
    print("7. REPORTE DE INGRESOS POR CURSO")
    print("=" * 60)
    cursor.execute("""
        SELECT 
            cu.nombre_curso AS Curso,
            cu.categoria AS Categoria,
            cu.modalidad AS Modalidad,
            COUNT(f.sk_inscripcion) AS Total_Inscripciones,
            SUM(f.monto_pagado) AS Ingresos_Totales,
            AVG(CAST(f.porcentaje_avance AS FLOAT)) AS Avance_Promedio
        FROM fact_inscripciones f
        JOIN dim_curso cu ON f.sk_curso = cu.sk_curso
        GROUP BY cu.nombre_curso, cu.categoria, cu.modalidad
        ORDER BY Ingresos_Totales DESC
    """)
    filas_curso = cursor.fetchall()
    print(f"{'Curso':<25} | {'Categoría':<12} | {'Modalidad':<10} | {'Insc.':<6} | {'Ingresos Totales':<18} | {'Avance Prom.':<12}")
    print("-" * 95)
    for r in filas_curso:
        print(f"{r[0]:<25} | {r[1]:<12} | {r[2]:<10} | {r[3]:<6} | ${r[4]:,.2f}          | {r[5]:.1f}%")

    # 8. REPORTE DE RECHAZADOS POR ETL
    print("\n" + "=" * 60)
    print("8. REPORTE DE RECHAZADOS POR ETL")
    print("=" * 60)
    cursor.execute("""
        SELECT 
            tabla_origen AS Fuente,
            id_origen AS Clave_Origen,
            motivo_rechazo AS Motivo,
            fecha_rechazo AS Cuando_Se_Rechazaron
        FROM etl_rechazos
        ORDER BY id_rechazo ASC
    """)
    filas_rechazos = cursor.fetchall()
    print(f"Total de registros rechazados: {len(filas_rechazos)}\n")
    print(f"{'Fuente':<20} | {'ID Origen':<10} | {'Motivo del Rechazo':<45} | {'Fecha/Hora Rechazo':<25}")
    print("-" * 105)
    for r in filas_rechazos:
        print(f"{r[0]:<20} | {r[1]:<10} | {r[2]:<45} | {r[3]}")

    conexion.close()
    print("\nAcción 4 finalizada exitosamente.\n")

if __name__ == "__main__":
    generar_reportes()
