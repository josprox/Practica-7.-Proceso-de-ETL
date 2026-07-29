USE db_campusfit_etl;
GO

-- 5. Tabla de Control del Proceso ETL
SELECT 'src_usuarios' AS Tabla, COUNT(*) AS Total FROM stg_usuarios
UNION ALL SELECT 'stg_usuarios', COUNT(*) FROM stg_usuarios
UNION ALL SELECT 'dim_usuario', COUNT(*) FROM dim_usuario
UNION ALL SELECT 'fact_inscripciones', COUNT(*) FROM fact_inscripciones
UNION ALL SELECT 'etl_rechazos', COUNT(*) FROM etl_rechazos;
GO

-- 6. Reporte de Inscripciones Válidas por Campaña
SELECT 
    c.nombre_campania AS Campania,
    c.canal AS Canal,
    COUNT(f.sk_inscripcion) AS Total_Inscripciones,
    SUM(f.monto_pagado) AS Ingresos_Totales
FROM fact_inscripciones f
JOIN dim_campania c ON f.sk_campania = c.sk_campania
GROUP BY c.nombre_campania, c.canal
ORDER BY Ingresos_Totales DESC;
GO

-- 7. Reporte de Ingresos por Curso
SELECT 
    cu.nombre_curso AS Curso,
    cu.categoria AS Categoria,
    cu.modalidad AS Modalidad,
    COUNT(f.sk_inscripcion) AS Total_Inscripciones,
    SUM(f.monto_pagado) AS Ingresos_Totales,
    ROUND(AVG(CAST(f.porcentaje_avance AS FLOAT)), 1) AS Avance_Promedio
FROM fact_inscripciones f
JOIN dim_curso cu ON f.sk_curso = cu.sk_curso
GROUP BY cu.nombre_curso, cu.categoria, cu.modalidad
ORDER BY Ingresos_Totales DESC;
GO

-- 8. Reporte de Rechazados por ETL (44 Registros en total)
SELECT tabla_origen AS Fuente, id_origen AS Clave_Origen, motivo_rechazo AS Motivo, fecha_rechazo AS Cuando_Se_Rechazaron
FROM etl_rechazos ORDER BY id_rechazo ASC;
GO

use master