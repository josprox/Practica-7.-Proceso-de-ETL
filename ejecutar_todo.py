import sys
import time

# Importación de los módulos organizados por capas de responsabilidad
from acciones.paso_01_crear_base_y_tablas import crear_base_y_tablas
from acciones.paso_02_cargar_staging import cargar_staging
from acciones.paso_03_ejecutar_transformacion_y_etl import ejecutar_transformacion_y_etl
from acciones.paso_04_generar_reportes import generar_reportes

def ejecutar_pipeline_completo():
    tiempo_inicio = time.time()
    print("\n" + "#" * 70)
    print("INICIANDO PIPELINE ETL COMPLETO - CAMPUSFIT ONLINE")
    print("#" * 70 + "\n")

    try:
        # Acción 1: Creación de la base de datos y esquema DDL
        crear_base_y_tablas()

        # Acción 2: Extracción y carga en Staging
        cargar_staging()

        # Acción 3: Transformación, limpieza y rechazos ETL
        ejecutar_transformacion_y_etl()

        # Acción 4: Generación de reportes
        generar_reportes()

        duracion = time.time() - tiempo_inicio
        print("#" * 70)
        print(f"PIPELINE ETL FINALIZADO CON ÉXITO EN {duracion:.2f} SEGUNDOS")
        print("#" * 70 + "\n")

    except Exception as error:
        print(f"\n[ERROR CRÍTICO] El proceso ETL falló con la siguiente excepción:\n{error}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_pipeline_completo()
