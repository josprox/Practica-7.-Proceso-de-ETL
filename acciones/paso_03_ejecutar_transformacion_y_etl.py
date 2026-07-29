from config.conexion import obtener_conexion
from limpiadores.normalizadores import (
    comillas_sql, parsear_monto, parsear_fecha,
    normalizar_ciudad, normalizar_canal, normalizar_modalidad
)
from inserciones.cargador_lotes import insertar_en_lotes

def ejecutar_transformacion_y_etl():
    print("=" * 60)
    print("ACCIÓN 3: TRANSFORMACIONES DE CALIDAD, ETL Y RECHAZOS")
    print("=" * 60)

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    lista_rechazos = []

    # A. DIM_USUARIO
    print("Procesando dim_usuario...")
    cursor.execute("SELECT id_usuario_origen, nombre, correo, ciudad, fecha_registro FROM stg_usuarios")
    filas_u = cursor.fetchall()
    correos_insertados = set()
    valores_dim_u = []

    for fila in filas_u:
        id_orig, nombre, correo_raw, ciudad_raw, fecha_raw = fila
        correo = (correo_raw or '').strip().lower()
        id_str = str(id_orig)

        if not correo:
            lista_rechazos.append(('stg_usuarios', id_str, 'Correo de usuario vacío'))
            continue
        if '@' not in correo:
            lista_rechazos.append(('stg_usuarios', id_str, 'Correo de usuario no contiene @'))
            continue
        if correo in correos_insertados:
            lista_rechazos.append(('stg_usuarios', id_str, 'Correo de usuario duplicado'))
            continue

        fecha_reg = parsear_fecha(fecha_raw) or '2026-01-01'
        ciudad_norm = normalizar_ciudad(ciudad_raw)
        correos_insertados.add(correo)
        u_id = int(id_orig) if str(id_orig).isdigit() else "NULL"
        valores_dim_u.append(f"({u_id}, {comillas_sql(nombre.strip())}, {comillas_sql(correo)}, {comillas_sql(ciudad_norm)}, {comillas_sql(fecha_reg)})")

    insertar_en_lotes(cursor, 'dim_usuario', ['id_usuario_origen', 'nombre', 'correo', 'ciudad', 'fecha_registro'], valores_dim_u)
    print(f"  - dim_usuario: {len(valores_dim_u)} registros válidos.")

    # B. DIM_CURSO
    print("Procesando dim_curso...")
    cursor.execute("SELECT id_curso_origen, nombre_curso, categoria, instructor, modalidad, costo_base FROM stg_cursos")
    filas_c = cursor.fetchall()
    cursos_insertados = set()
    valores_dim_c = []

    for fila in filas_c:
        id_orig, n_curso, cat, inst, mod, costo_raw = fila
        id_str = str(id_orig)

        if not n_curso or not n_curso.strip():
            lista_rechazos.append(('stg_cursos', id_str, 'Nombre de curso vacío'))
            continue

        costo = parsear_monto(costo_raw)
        if costo is None:
            lista_rechazos.append(('stg_cursos', id_str, 'Costo base de curso no numérico'))
            continue

        n_curso_clean = n_curso.strip()
        if n_curso_clean in cursos_insertados:
            lista_rechazos.append(('stg_cursos', id_str, 'Curso duplicado'))
            continue

        cursos_insertados.add(n_curso_clean)
        mod_norm = normalizar_modalidad(mod)
        cat_norm = cat.strip().title()
        c_id = int(id_orig) if str(id_orig).isdigit() else "NULL"
        valores_dim_c.append(f"({c_id}, {comillas_sql(n_curso_clean)}, {comillas_sql(cat_norm)}, {comillas_sql(inst.strip())}, {comillas_sql(mod_norm)}, {costo})")

    insertar_en_lotes(cursor, 'dim_curso', ['id_curso_origen', 'nombre_curso', 'categoria', 'instructor', 'modalidad', 'costo_base'], valores_dim_c)
    print(f"  - dim_curso: {len(valores_dim_c)} registros válidos.")

    # C. DIM_CAMPANIA
    print("Procesando dim_campania...")
    cursor.execute("SELECT nombre_campania, responsable, objetivo_manual FROM stg_reporte_campanias_doc")
    info_doc = {row[0].strip(): (row[1].strip(), row[2].strip()) for row in cursor.fetchall()}

    cursor.execute("SELECT id_campania_origen, nombre_campania, canal, presupuesto, fecha_inicio, fecha_fin FROM stg_campanias")
    filas_cmp = cursor.fetchall()
    campanias_insertadas = set()
    valores_dim_cmp = []

    for fila in filas_cmp:
        id_orig, n_camp, canal_raw, pres_raw, f_ini_raw, f_fin_raw = fila
        id_str = str(id_orig)

        if not n_camp or not n_camp.strip():
            lista_rechazos.append(('stg_campanias', id_str, 'Nombre de campaña vacío'))
            continue

        presupuesto = parsear_monto(pres_raw)
        if presupuesto is None:
            lista_rechazos.append(('stg_campanias', id_str, 'Presupuesto de campaña no numérico'))
            continue

        n_camp_clean = n_camp.strip()
        if n_camp_clean in campanias_insertadas:
            lista_rechazos.append(('stg_campanias', id_str, 'Campaña duplicada'))
            continue

        campanias_insertadas.add(n_camp_clean)
        canal_norm = normalizar_canal(canal_raw)
        f_ini = parsear_fecha(f_ini_raw)
        f_fin = parsear_fecha(f_fin_raw)

        responsable, objetivo = info_doc.get(n_camp_clean, ('Marketing General', 'Promoción General'))
        cmp_id = int(id_orig) if str(id_orig).isdigit() else "NULL"
        valores_dim_cmp.append(f"({cmp_id}, {comillas_sql(n_camp_clean)}, {comillas_sql(canal_norm)}, {presupuesto}, {comillas_sql(responsable)}, {comillas_sql(objetivo)}, {comillas_sql(f_ini)}, {comillas_sql(f_fin)})")

    insertar_en_lotes(cursor, 'dim_campania', ['id_campania_origen', 'nombre_campania', 'canal', 'presupuesto', 'responsable', 'objetivo_manual', 'fecha_inicio', 'fecha_fin'], valores_dim_cmp)
    print(f"  - dim_campania: {len(valores_dim_cmp)} registros válidos.")

    # D. FACT_INSCRIPCIONES
    print("Procesando fact_inscripciones...")
    cursor.execute("SELECT sk_usuario, correo FROM dim_usuario")
    lookup_usuarios = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT sk_curso, nombre_curso FROM dim_curso")
    lookup_cursos = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT sk_campania, nombre_campania FROM dim_campania")
    lookup_campanias = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT id_inscripcion_origen, correo_usuario, nombre_curso, nombre_campania, fecha_inscripcion, monto_pagado, porcentaje_avance FROM stg_inscripciones")
    filas_ins = cursor.fetchall()
    inscripciones_insertadas = set()
    valores_fact = []

    for fila in filas_ins:
        id_orig, correo_raw, curso_raw, camp_raw, fecha_raw, monto_raw, avance_raw = fila
        id_str = str(id_orig)

        correo = (correo_raw or '').strip().lower()
        curso = (curso_raw or '').strip()
        camp = (camp_raw or '').strip()

        fecha_ins = parsear_fecha(fecha_raw)
        if not fecha_ins:
            lista_rechazos.append(('stg_inscripciones', id_str, 'Fecha de inscripción inválida'))
            continue

        monto = parsear_monto(monto_raw)
        if monto is None or monto <= 0:
            lista_rechazos.append(('stg_inscripciones', id_str, 'Monto pagado inválido o <= 0'))
            continue

        sk_u = lookup_usuarios.get(correo)
        if not sk_u:
            lista_rechazos.append(('stg_inscripciones', id_str, 'Usuario inexistente en dim_usuario'))
            continue

        sk_c = lookup_cursos.get(curso)
        if not sk_c:
            lista_rechazos.append(('stg_inscripciones', id_str, 'Curso inexistente en dim_curso'))
            continue

        sk_cmp = lookup_campanias.get(camp)
        if not sk_cmp:
            lista_rechazos.append(('stg_inscripciones', id_str, 'Campaña inexistente en dim_campania'))
            continue

        llave_dedup = (sk_u, sk_c, sk_cmp, fecha_ins)
        if llave_dedup in inscripciones_insertadas:
            lista_rechazos.append(('stg_inscripciones', id_str, 'Inscripción duplicada'))
            continue

        inscripciones_insertadas.add(llave_dedup)
        avance = int(avance_raw) if str(avance_raw).isdigit() else 0
        ins_id = int(id_orig) if str(id_orig).isdigit() else "NULL"
        valores_fact.append(f"({sk_u}, {sk_c}, {sk_cmp}, {ins_id}, {comillas_sql(fecha_ins)}, {monto}, {avance})")

    insertar_en_lotes(cursor, 'fact_inscripciones', ['sk_usuario', 'sk_curso', 'sk_campania', 'id_inscripcion_origen', 'fecha_inscripcion', 'monto_pagado', 'porcentaje_avance'], valores_fact)
    print(f"  - fact_inscripciones: {len(valores_fact)} inscripciones válidas.")

    # E. CARGA DE REGISTROS RECHAZADOS
    if lista_rechazos:
        valores_rej = [f"({comillas_sql(r[0])}, {comillas_sql(r[1])}, {comillas_sql(r[2])})" for r in lista_rechazos]
        insertar_en_lotes(cursor, 'etl_rechazos', ['tabla_origen', 'id_origen', 'motivo_rechazo'], valores_rej)
    print(f"  - etl_rechazos: {len(lista_rechazos)} registros rechazados.")

    conexion.close()
    print("Acción 3 finalizada exitosamente.\n")

if __name__ == "__main__":
    ejecutar_transformacion_y_etl()
