-- =====================================================================
-- 04_rutinas.sql : triggers, función y procedimientos almacenados
-- Ejecutar después de 03_consultas_vistas.sql
-- =====================================================================
USE sonrisa_derrisa;

DROP TRIGGER   IF EXISTS trg_cita_bi;
DROP TRIGGER   IF EXISTS trg_cita_bu;
DROP TRIGGER   IF EXISTS trg_detalle_cita_bi;
DROP TRIGGER   IF EXISTS trg_pago_bi;
DROP FUNCTION  IF EXISTS fn_saldo_cita;
DROP PROCEDURE IF EXISTS sp_atender_cita;
DROP PROCEDURE IF EXISTS sp_estado_cuenta_paciente;

DELIMITER //

-- ---------------------------------------------------------------------
-- TRIGGERS
-- ---------------------------------------------------------------------

-- TR1 Evento: BEFORE INSERT en cita.
-- Condición 1 (RN2): el paciente no tiene historial clínico.
-- Condición 2 (RN5): el dentista ya tiene una cita no cancelada a esa fecha y hora.
-- Efecto: cancela la inserción con SQLSTATE 45000.
CREATE TRIGGER trg_cita_bi
BEFORE INSERT ON cita
FOR EACH ROW
BEGIN
    IF NOT EXISTS (SELECT 1 FROM historial_clinico WHERE id_paciente = NEW.id_paciente) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El paciente debe tener historial clínico antes de agendar una cita.';
    END IF;

    IF NEW.estado <> 'Cancelada' AND EXISTS (
        SELECT 1 FROM cita
        WHERE id_dentista = NEW.id_dentista AND fecha = NEW.fecha
          AND hora = NEW.hora AND estado <> 'Cancelada') THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El dentista ya tiene una cita en esa fecha y hora.';
    END IF;
END//

-- TR2 Evento: BEFORE UPDATE en cita. Condición (RN5): al reprogramar o
-- reactivar, el nuevo horario choca con otra cita activa del dentista.
CREATE TRIGGER trg_cita_bu
BEFORE UPDATE ON cita
FOR EACH ROW
BEGIN
    IF NEW.estado <> 'Cancelada' AND EXISTS (
        SELECT 1 FROM cita
        WHERE id_dentista = NEW.id_dentista AND fecha = NEW.fecha
          AND hora = NEW.hora AND estado <> 'Cancelada'
          AND id_cita <> NEW.id_cita) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El dentista ya tiene una cita en esa fecha y hora.';
    END IF;
END//

-- TR3 Evento: BEFORE INSERT en detalle_cita. Condición (RN7): la cita no
-- está Atendida. Efecto: rechaza registrar tratamientos en citas no atendidas.
CREATE TRIGGER trg_detalle_cita_bi
BEFORE INSERT ON detalle_cita
FOR EACH ROW
BEGIN
    IF (SELECT estado FROM cita WHERE id_cita = NEW.id_cita) <> 'Atendida' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Solo las citas atendidas pueden tener tratamientos.';
    END IF;
END//

-- TR4 Evento: BEFORE INSERT en pago. Condición (RN11): la suma de pagos
-- superaría el total de tratamientos de la cita. Efecto: rechaza el pago.
CREATE TRIGGER trg_pago_bi
BEFORE INSERT ON pago
FOR EACH ROW
BEGIN
    IF NEW.monto > fn_saldo_cita(NEW.id_cita) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El pago excede el saldo pendiente de la cita.';
    END IF;
END//
-- Nota: MySQL resuelve fn_saldo_cita al disparar el trigger, no al crearlo,
-- por eso la función puede definirse a continuación.

-- ---------------------------------------------------------------------
-- FUNCIÓN
-- ---------------------------------------------------------------------

-- F1 (RN12) Saldo pendiente de una cita = suma de precios aplicados - suma de pagos.
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

-- ---------------------------------------------------------------------
-- PROCEDIMIENTOS
-- ---------------------------------------------------------------------

-- P1 Operación de negocio multitabla: atender una cita.
-- Cambia la cita a 'Atendida' (cita), registra el tratamiento realizado
-- (detalle_cita) y, si se indica, el primer abono (pago). Todo o nada.
-- Si p_precio es NULL se usa el precio base del tratamiento.
CREATE PROCEDURE sp_atender_cita(
    IN p_id_cita        INT,
    IN p_id_tratamiento INT,
    IN p_diente         VARCHAR(5),
    IN p_precio         DECIMAL(10,2),
    IN p_monto_pago     DECIMAL(10,2),
    IN p_metodo_pago    VARCHAR(15)
)
BEGIN
    DECLARE v_estado VARCHAR(15);
    DECLARE v_precio DECIMAL(10,2);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT estado INTO v_estado FROM cita WHERE id_cita = p_id_cita;

    IF v_estado IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cita no existe.';
    END IF;
    IF v_estado = 'Cancelada' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede atender una cita cancelada.';
    END IF;

    SELECT precio_base INTO v_precio FROM tratamiento WHERE id_tratamiento = p_id_tratamiento;
    IF v_precio IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tratamiento no existe.';
    END IF;

    START TRANSACTION;

    UPDATE cita SET estado = 'Atendida' WHERE id_cita = p_id_cita;

    INSERT INTO detalle_cita (id_cita, id_tratamiento, diente, precio_aplicado)
    VALUES (p_id_cita, p_id_tratamiento, NULLIF(TRIM(p_diente), ''), IFNULL(p_precio, v_precio));

    IF p_monto_pago IS NOT NULL AND p_monto_pago > 0 THEN
        INSERT INTO pago (id_cita, monto, metodo_pago)
        VALUES (p_id_cita, p_monto_pago, p_metodo_pago);
    END IF;

    COMMIT;
END//

-- P2 Estado de cuenta de un paciente: citas atendidas con total, pagado y saldo.
CREATE PROCEDURE sp_estado_cuenta_paciente(IN p_id_paciente INT)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM paciente WHERE id_paciente = p_id_paciente) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El paciente no existe.';
    END IF;

    SELECT id_cita, fecha, dentista, total, pagado, saldo
    FROM vw_saldo_citas
    WHERE id_paciente = p_id_paciente
    ORDER BY fecha;

    SELECT paciente, SUM(total) AS total_general, SUM(pagado) AS pagado_general,
           SUM(saldo) AS saldo_general
    FROM vw_saldo_citas
    WHERE id_paciente = p_id_paciente
    GROUP BY paciente;
END//

DELIMITER ;
