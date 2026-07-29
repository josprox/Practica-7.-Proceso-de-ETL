def insertar_en_lotes(cursor, tabla, columnas, lista_valores_sql, tamano_lote=50):
    """
    Inserta una lista de tuplas formateadas como SQL en lotes especificados.
    """
    if not lista_valores_sql:
        return
    
    cols_str = f"({', '.join(columnas)})" if columnas else ""
    
    for i in range(0, len(lista_valores_sql), tamano_lote):
        bloque = lista_valores_sql[i:i + tamano_lote]
        consulta = f"INSERT INTO {tabla} {cols_str} VALUES {','.join(bloque)}"
        cursor.execute(consulta)
