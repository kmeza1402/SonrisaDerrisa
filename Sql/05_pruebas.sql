-- =====================================================================
-- 05_pruebas.sql : casos válidos e inválidos de triggers, función,
-- procedimientos y restricciones. Los casos inválidos DEBEN fallar,
-- por eso se ejecuta con --force para que el script continúe:
--   mysql --force -vvv --default-character-set=utf8mb4 -u root -p < 05_pruebas.sql
-- =====================================================================
USE sonrisa_derrisa;

-- ---------- Función fn_saldo_cita (RN12) ----------
-- PF-01 válido: saldo de algunas citas
SELECT id_cita, fn_saldo_cita(id_cita) AS saldo FROM cita WHERE id_cita IN (1, 2, 4, 8, 11);
-- PF-02 caso límite: cita sin tratamientos -> 0
SELECT fn_saldo_cita(12) AS saldo_cita_programada;

-- ---------- Trigger TR1 (RN2 y RN5) ----------
-- PT-01 inválido: paciente sin historial (Diego, 8) -> ERROR 1644
INSERT INTO cita (id_paciente, id_dentista, fecha, hora, motivo) VALUES (8, 1, '2026-12-01', '09:00', 'Valoración');
-- PT-02 inválido: empalme, la Dra. Morales (1) ya tiene cita el 2026-11-25 11:00 -> ERROR 1644
INSERT INTO cita (id_paciente, id_dentista, fecha, hora, motivo) VALUES (5, 1, '2026-11-25', '11:00', 'Limpieza');
-- PT-03 válido: el mismo horario de una cita CANCELADA sí se puede usar (cita 6: 2026-10-20 09:00)
INSERT INTO cita (id_paciente, id_dentista, fecha, hora, motivo) VALUES (2, 1, '2026-10-20', '09:00', 'Hueco por cancelación');
SELECT id_cita, id_paciente, fecha, hora, estado FROM cita WHERE id_dentista = 1 AND fecha = '2026-10-20';

-- ---------- Trigger TR2 (RN5 al reprogramar) ----------
-- PT-04 inválido: reprogramar la cita 12 (dentista 1) al 2026-11-10 09:00,
--        horario ocupado por la cita 9 del mismo dentista -> ERROR 1644
UPDATE cita SET fecha = '2026-11-10', hora = '09:00' WHERE id_cita = 12;

-- ---------- Trigger TR3 (RN7) ----------
-- PT-05 inválido: tratamiento en cita Programada (13) -> ERROR 1644
INSERT INTO detalle_cita (id_cita, id_tratamiento, precio_aplicado) VALUES (13, 1, 600);

-- ---------- Trigger TR4 (RN11) ----------
-- PT-06 inválido: la cita 4 debe 700; se intenta pagar 900 -> ERROR 1644
INSERT INTO pago (id_cita, monto, metodo_pago) VALUES (4, 900, 'Efectivo');
-- PT-07 válido: pagar exactamente el saldo (700) deja la cita en 0
INSERT INTO pago (id_cita, monto, metodo_pago) VALUES (4, 700, 'Efectivo');
SELECT fn_saldo_cita(4) AS saldo_cita_4;

-- ---------- Procedimiento P1 sp_atender_cita ----------
-- PP-01 válido: atender la cita 13 (Fernanda) con limpieza a precio infantil y abono de 300
CALL sp_atender_cita(13, 1, NULL, 500.00, 300.00, 'Efectivo');
SELECT id_cita, estado FROM cita WHERE id_cita = 13;
SELECT * FROM detalle_cita WHERE id_cita = 13;
SELECT * FROM pago WHERE id_cita = 13;
SELECT fn_saldo_cita(13) AS saldo_cita_13;

-- PP-02 inválido: cita inexistente -> ERROR 'La cita no existe.'
CALL sp_atender_cita(999, 1, NULL, NULL, NULL, NULL);
-- PP-03 inválido: cita cancelada (6) -> ERROR
CALL sp_atender_cita(6, 3, '48', NULL, NULL, NULL);
-- PP-04 inválido con ROLLBACK: pago mayor al total (cita 14, blanqueamiento 2800, paga 5000)
--         el trigger TR4 falla y el procedimiento revierte también el cambio de estado
CALL sp_atender_cita(14, 7, NULL, NULL, 5000.00, 'Tarjeta');
SELECT id_cita, estado FROM cita WHERE id_cita = 14;               -- sigue Programada
SELECT COUNT(*) AS detalles_cita_14 FROM detalle_cita WHERE id_cita = 14;  -- 0
-- PP-05 inválido: diente con formato incorrecto (CHECK) -> ROLLBACK
CALL sp_atender_cita(14, 2, '99', NULL, NULL, NULL);
SELECT id_cita, estado FROM cita WHERE id_cita = 14;

-- ---------- Procedimiento P2 sp_estado_cuenta_paciente ----------
-- PP-06 válido: estado de cuenta de Luis (2)
CALL sp_estado_cuenta_paciente(2);
-- PP-07 inválido: paciente inexistente -> ERROR
CALL sp_estado_cuenta_paciente(999);

-- ---------- Restricciones de integridad ----------
-- PR-01 FK: eliminar dentista con citas -> ERROR 1451
DELETE FROM dentista WHERE id_dentista = 1;
-- PR-02 UNIQUE: cédula repetida -> ERROR 1062
INSERT INTO dentista (nombre, apellidos, cedula, id_especialidad) VALUES ('Otro', 'Dentista', 'CED-10001', 1);
-- PR-03 UNIQUE (RN2): segundo historial para el mismo paciente -> ERROR 1062
INSERT INTO historial_clinico (id_paciente, alergias) VALUES (1, 'Ninguna');
-- PR-04 CHECK (RN6): estado no permitido -> ERROR 3819
UPDATE cita SET estado = 'Pendiente' WHERE id_cita = 12;
-- PR-05 CHECK (RN11): pago con monto 0 -> ERROR 3819
INSERT INTO pago (id_cita, monto, metodo_pago) VALUES (11, 0, 'Efectivo');
-- PR-06 CHECK (RN1): teléfono inválido -> ERROR 3819
INSERT INTO paciente (nombre, apellidos, telefono) VALUES ('Prueba', 'Teléfono', '64612AB');
-- PR-07 ON DELETE CASCADE: al borrar un paciente sin citas se borra su historial
INSERT INTO paciente (nombre, apellidos, telefono) VALUES ('Temporal', 'Cascada', '6460000000');
SET @tmp = LAST_INSERT_ID();
INSERT INTO historial_clinico (id_paciente) VALUES (@tmp);
DELETE FROM paciente WHERE id_paciente = @tmp;
SELECT COUNT(*) AS historiales_huerfanos FROM historial_clinico WHERE id_paciente = @tmp;

-- Estado final
SELECT 'paciente' AS tabla, COUNT(*) AS registros FROM paciente
UNION ALL SELECT 'historial_clinico', COUNT(*) FROM historial_clinico
UNION ALL SELECT 'dentista', COUNT(*) FROM dentista
UNION ALL SELECT 'cita', COUNT(*) FROM cita
UNION ALL SELECT 'detalle_cita', COUNT(*) FROM detalle_cita
UNION ALL SELECT 'pago', COUNT(*) FROM pago;
