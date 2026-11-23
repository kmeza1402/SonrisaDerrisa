-- =====================================================================
-- 03_consultas_vistas.sql : 10 consultas documentadas, la función fn_saldo_cita,
-- 2 vistas y transacciones (COMMIT y ROLLBACK). Ejecutar después de 02_datos.sql
-- =====================================================================
USE sonrisa_derrisa;

-- ---------------------------------------------------------------------
-- CONSULTAS CON JOIN (3)
-- ---------------------------------------------------------------------

-- Q1 (JOIN 4 tablas, filtro y orden) Agenda de citas programadas.
SELECT c.id_cita, c.fecha, c.hora,
       CONCAT(p.nombre, ' ', p.apellidos) AS paciente,
       CONCAT(d.nombre, ' ', d.apellidos) AS dentista,
       e.nombre AS especialidad, c.motivo
FROM cita c
JOIN paciente p     ON p.id_paciente     = c.id_paciente
JOIN dentista d     ON d.id_dentista     = c.id_dentista
JOIN especialidad e ON e.id_especialidad = d.id_especialidad
WHERE c.estado = 'Programada'
ORDER BY c.fecha, c.hora;

-- Q2 (JOIN 4 tablas) Tratamientos realizados por paciente, con diente y precio aplicado.
SELECT CONCAT(p.nombre, ' ', p.apellidos) AS paciente, c.fecha,
       t.nombre AS tratamiento, dc.diente, t.precio_base, dc.precio_aplicado
FROM detalle_cita dc
JOIN cita c        ON c.id_cita        = dc.id_cita
JOIN paciente p    ON p.id_paciente    = c.id_paciente
JOIN tratamiento t ON t.id_tratamiento = dc.id_tratamiento
ORDER BY paciente, c.fecha;

-- Q3 (JOIN) Próximas citas de pacientes con alergias (riesgo clínico, RN2).
SELECT c.fecha, c.hora, CONCAT(p.nombre, ' ', p.apellidos) AS paciente,
       h.alergias, h.enfermedades, CONCAT(d.nombre, ' ', d.apellidos) AS dentista
FROM cita c
JOIN paciente p          ON p.id_paciente = c.id_paciente
JOIN historial_clinico h ON h.id_paciente = p.id_paciente
JOIN dentista d          ON d.id_dentista = c.id_dentista
WHERE c.estado = 'Programada'
  AND (h.alergias IS NOT NULL OR h.enfermedades IS NOT NULL);

-- ---------------------------------------------------------------------
-- SUBCONSULTAS (2)
-- ---------------------------------------------------------------------

-- Q4 (NOT EXISTS) Pacientes que aún no tienen historial clínico.
SELECT p.id_paciente, CONCAT(p.nombre, ' ', p.apellidos) AS paciente, p.fecha_registro
FROM paciente p
WHERE NOT EXISTS (SELECT 1 FROM historial_clinico h WHERE h.id_paciente = p.id_paciente);

-- Q5 (EXISTS) Dentistas que han realizado al menos una endodoncia.
SELECT d.id_dentista, CONCAT(d.nombre, ' ', d.apellidos) AS dentista, d.cedula
FROM dentista d
WHERE EXISTS (SELECT 1
              FROM cita c
              JOIN detalle_cita dc ON dc.id_cita = c.id_cita
              JOIN tratamiento t   ON t.id_tratamiento = dc.id_tratamiento
              WHERE c.id_dentista = d.id_dentista
                AND t.nombre = 'Endodoncia');

-- ---------------------------------------------------------------------
-- FUNCIONES AGREGADAS CON GROUP BY / HAVING (3)
-- ---------------------------------------------------------------------

-- Q6 (SUM/COUNT + GROUP BY) Ingresos por método de pago.
SELECT metodo_pago, COUNT(*) AS pagos, SUM(monto) AS total
FROM pago
GROUP BY metodo_pago
ORDER BY total DESC;

-- Q7 (COUNT + HAVING) Pacientes con más de una cita atendida.
SELECT CONCAT(p.nombre, ' ', p.apellidos) AS paciente, COUNT(*) AS citas_atendidas
FROM paciente p
JOIN cita c ON c.id_paciente = p.id_paciente
WHERE c.estado = 'Atendida'
GROUP BY p.id_paciente, p.nombre, p.apellidos
HAVING COUNT(*) > 1;

-- Q8 (SUM/AVG + GROUP BY) Producción por dentista: total cobrado y promedio por cita.
SELECT CONCAT(d.nombre, ' ', d.apellidos) AS dentista,
       COUNT(DISTINCT c.id_cita)                                  AS citas_atendidas,
       SUM(dc.precio_aplicado)                                    AS total_tratamientos,
       ROUND(SUM(dc.precio_aplicado) / COUNT(DISTINCT c.id_cita), 2) AS promedio_por_cita
FROM dentista d
JOIN cita c          ON c.id_dentista = d.id_dentista AND c.estado = 'Atendida'
JOIN detalle_cita dc ON dc.id_cita    = c.id_cita
GROUP BY d.id_dentista, d.nombre, d.apellidos
ORDER BY total_tratamientos DESC;

-- ---------------------------------------------------------------------
-- LIBRE ELECCIÓN (2)
-- ---------------------------------------------------------------------

-- Q9 (JOIN 3 tablas + COUNT + HAVING) Dentistas con tres o más citas activas (no canceladas).
SELECT CONCAT(d.nombre, ' ', d.apellidos) AS dentista, e.nombre AS especialidad,
       COUNT(*) AS citas_activas
FROM dentista d
JOIN especialidad e ON e.id_especialidad = d.id_especialidad
JOIN cita c         ON c.id_dentista     = d.id_dentista
WHERE c.estado <> 'Cancelada'
GROUP BY d.id_dentista, d.nombre, d.apellidos, e.nombre
HAVING COUNT(*) >= 3
ORDER BY citas_activas DESC;

-- Q10 (UNION, operación de conjunto) Directorio telefónico de pacientes y dentistas.
SELECT 'Paciente' AS tipo, CONCAT(nombre, ' ', apellidos) AS nombre, telefono
FROM paciente
UNION
SELECT 'Dentista', CONCAT(nombre, ' ', apellidos), telefono
FROM dentista
WHERE telefono IS NOT NULL
ORDER BY tipo, nombre;

-- ---------------------------------------------------------------------
-- FUNCIÓN fn_saldo_cita (RN12)
-- Se crea aquí, antes de las vistas, porque vw_saldo_citas la usa.
-- Saldo de una cita = suma de precios aplicados - suma de pagos.
-- ---------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_saldo_cita;
DELIMITER //
CREATE FUNCTION fn_saldo_cita(p_id_cita INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE v_total  DECIMAL(10,2);
    DECLARE v_pagado DECIMAL(10,2);
    SELECT IFNULL(SUM(precio_aplicado), 0) INTO v_total  FROM detalle_cita WHERE id_cita = p_id_cita;
    SELECT IFNULL(SUM(monto), 0)           INTO v_pagado FROM pago         WHERE id_cita = p_id_cita;
    RETURN v_total - v_pagado;
END//
DELIMITER ;

-- ---------------------------------------------------------------------
-- VISTAS (2)
-- ---------------------------------------------------------------------

-- V1 Agenda completa con datos clínicos de alerta (la usa el módulo de citas).
CREATE OR REPLACE VIEW vw_agenda AS
SELECT c.id_cita, c.fecha, c.hora, c.estado, c.motivo,
       p.id_paciente, CONCAT(p.nombre, ' ', p.apellidos) AS paciente, p.telefono,
       d.id_dentista, CONCAT(d.nombre, ' ', d.apellidos) AS dentista,
       e.nombre AS especialidad,
       h.alergias
FROM cita c
JOIN paciente p     ON p.id_paciente     = c.id_paciente
JOIN dentista d     ON d.id_dentista     = c.id_dentista
JOIN especialidad e ON e.id_especialidad = d.id_especialidad
LEFT JOIN historial_clinico h ON h.id_paciente = p.id_paciente;

-- V2 Estado de cuenta por cita: total, pagado y saldo (la usa el reporte de saldos).
CREATE OR REPLACE VIEW vw_saldo_citas AS
SELECT c.id_cita, c.fecha, c.estado,
       p.id_paciente, CONCAT(p.nombre, ' ', p.apellidos) AS paciente,
       CONCAT(d.nombre, ' ', d.apellidos) AS dentista,
       (SELECT IFNULL(SUM(precio_aplicado), 0) FROM detalle_cita WHERE id_cita = c.id_cita) AS total,
       (SELECT IFNULL(SUM(monto), 0) FROM pago WHERE id_cita = c.id_cita)                    AS pagado,
       fn_saldo_cita(c.id_cita)                                                              AS saldo
FROM cita c
JOIN paciente p ON p.id_paciente = c.id_paciente
JOIN dentista d ON d.id_dentista = c.id_dentista
WHERE c.estado = 'Atendida';

-- Demostración de las vistas
SELECT id_cita, fecha, hora, paciente, dentista, especialidad, estado, alergias
FROM vw_agenda WHERE fecha >= '2026-11-01' ORDER BY fecha, hora;
SELECT * FROM vw_saldo_citas WHERE saldo > 0 ORDER BY saldo DESC;

-- ---------------------------------------------------------------------
-- TRANSACCIONES
-- ---------------------------------------------------------------------

-- T1 COMMIT: alta de un servicio nuevo y actualización de precio de lista.
START TRANSACTION;
INSERT INTO tratamiento (nombre, descripcion, precio_base)
VALUES ('Corona de porcelana', 'Corona fija de porcelana', 6500.00);
UPDATE tratamiento SET precio_base = precio_base * 1.05 WHERE nombre = 'Limpieza dental';
COMMIT;
SELECT nombre, precio_base FROM tratamiento
WHERE nombre IN ('Corona de porcelana', 'Limpieza dental');

-- T2 ROLLBACK controlado: se borran por error los pagos de la cita 2 y se revierte.
SELECT 'Antes' AS paso, COUNT(*) AS pagos_cita_2, SUM(monto) AS total FROM pago WHERE id_cita = 2;
START TRANSACTION;
DELETE FROM pago WHERE id_cita = 2;
SELECT 'Dentro de la transacción' AS paso, COUNT(*) AS pagos_cita_2, SUM(monto) AS total FROM pago WHERE id_cita = 2;
ROLLBACK;
SELECT 'Después del ROLLBACK' AS paso, COUNT(*) AS pagos_cita_2, SUM(monto) AS total FROM pago WHERE id_cita = 2;
