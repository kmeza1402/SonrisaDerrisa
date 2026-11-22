-- =====================================================================
-- Proyecto Final Base de Datos - Sonrisa Derrisa (Equipo Bombones)
-- Sistema de citas, tratamientos y pagos para clínica dental
-- 01_esquema.sql : base de datos, tablas, PK, FK y restricciones
-- Ejecutar: mysql -u root -p --default-character-set=utf8mb4 < 01_esquema.sql
-- =====================================================================

DROP DATABASE IF EXISTS sonrisa_derrisa;

CREATE DATABASE sonrisa_derrisa
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;
-- utf8mb4_0900_ai_ci es la intercalación por defecto de MySQL 8 y la de la
-- conexión de la aplicación; usar otra provocaba el error 1267 (incidencia INC-01).

USE sonrisa_derrisa;

-- Áreas de la odontología
CREATE TABLE especialidad
(
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(50) NOT NULL,
    CONSTRAINT uq_especialidad_nombre UNIQUE (nombre)
);

-- Personas que reciben atención (RN1: nombre, apellidos y teléfono obligatorios)
CREATE TABLE paciente
(
    id_paciente      INT AUTO_INCREMENT PRIMARY KEY,
    nombre           VARCHAR(50)  NOT NULL,
    apellidos        VARCHAR(80)  NOT NULL,
    fecha_nacimiento DATE,
    telefono         VARCHAR(15)  NOT NULL,
    correo           VARCHAR(100),
    fecha_registro   DATE         NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT uq_paciente_correo   UNIQUE (correo),
    CONSTRAINT ck_paciente_telefono CHECK (telefono REGEXP '^[0-9]{10}$'),
    CONSTRAINT ck_paciente_correo   CHECK (correo IS NULL OR correo LIKE '%_@_%._%')
);

-- Antecedentes médicos (RN2: uno por paciente)
CREATE TABLE historial_clinico
(
    id_historial        INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente         INT  NOT NULL,
    alergias            VARCHAR(200),
    enfermedades        VARCHAR(200),
    medicamentos        VARCHAR(200),
    fecha_actualizacion DATE NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT uq_historial_paciente UNIQUE (id_paciente),
    CONSTRAINT fk_historial_paciente
        FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Profesionales (RN3: una especialidad, cédula única)
CREATE TABLE dentista
(
    id_dentista     INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(50) NOT NULL,
    apellidos       VARCHAR(80) NOT NULL,
    cedula          VARCHAR(20) NOT NULL,
    telefono        VARCHAR(15),
    id_especialidad INT         NOT NULL,
    CONSTRAINT uq_dentista_cedula   UNIQUE (cedula),
    CONSTRAINT ck_dentista_telefono CHECK (telefono IS NULL OR telefono REGEXP '^[0-9]{10}$'),
    CONSTRAINT fk_dentista_especialidad
        FOREIGN KEY (id_especialidad) REFERENCES especialidad(id_especialidad)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Catálogo de servicios
CREATE TABLE tratamiento
(
    id_tratamiento INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(60)   NOT NULL,
    descripcion    VARCHAR(200),
    precio_base    DECIMAL(10,2) NOT NULL,
    CONSTRAINT uq_tratamiento_nombre UNIQUE (nombre),
    CONSTRAINT ck_tratamiento_precio CHECK (precio_base >= 0)
);

-- Visitas programadas (RN4, RN6). RN5 (sin empalmes) se valida con trigger.
CREATE TABLE cita
(
    id_cita     INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT          NOT NULL,
    id_dentista INT          NOT NULL,
    fecha       DATE         NOT NULL,
    hora        TIME         NOT NULL,
    motivo      VARCHAR(150),
    estado      VARCHAR(15)  NOT NULL DEFAULT 'Programada',
    CONSTRAINT ck_cita_estado CHECK (estado IN ('Programada', 'Atendida', 'Cancelada')),
    CONSTRAINT fk_cita_paciente
        FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_cita_dentista
        FOREIGN KEY (id_dentista) REFERENCES dentista(id_dentista)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX ix_cita_agenda (id_dentista, fecha, hora)
);

-- Tratamientos realizados en una cita (resuelve N:M Cita-Tratamiento; RN8, RN9)
CREATE TABLE detalle_cita
(
    id_detalle      INT AUTO_INCREMENT PRIMARY KEY,
    id_cita         INT           NOT NULL,
    id_tratamiento  INT           NOT NULL,
    diente          VARCHAR(5),
    precio_aplicado DECIMAL(10,2) NOT NULL,
    CONSTRAINT uq_detalle_cita_trat_diente UNIQUE (id_cita, id_tratamiento, diente),
    CONSTRAINT ck_detalle_precio CHECK (precio_aplicado >= 0),
    CONSTRAINT ck_detalle_diente CHECK (diente IS NULL OR diente REGEXP '^[1-8][1-8]$'),
    CONSTRAINT fk_detalle_cita
        FOREIGN KEY (id_cita) REFERENCES cita(id_cita)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_detalle_tratamiento
        FOREIGN KEY (id_tratamiento) REFERENCES tratamiento(id_tratamiento)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Abonos (RN10, RN11: monto > 0; el tope por cita se valida con trigger)
CREATE TABLE pago
(
    id_pago     INT AUTO_INCREMENT PRIMARY KEY,
    id_cita     INT           NOT NULL,
    fecha_pago  DATE          NOT NULL DEFAULT (CURRENT_DATE),
    monto       DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(15)   NOT NULL,
    CONSTRAINT ck_pago_monto  CHECK (monto > 0),
    CONSTRAINT ck_pago_metodo CHECK (metodo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia')),
    CONSTRAINT fk_pago_cita
        FOREIGN KEY (id_cita) REFERENCES cita(id_cita)
        ON UPDATE CASCADE ON DELETE RESTRICT
);
