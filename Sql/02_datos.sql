-- =====================================================================
-- 02_datos.sql : datos de prueba ficticios (reproducible)
-- Ejecutar después de 01_esquema.sql
-- =====================================================================
USE sonrisa_derrisa;

INSERT INTO especialidad (nombre) VALUES
('Odontología general'),
('Ortodoncia'),
('Endodoncia'),
('Odontopediatría'),
('Periodoncia');

INSERT INTO paciente (nombre, apellidos, fecha_nacimiento, telefono, correo, fecha_registro) VALUES
('Mariana',   'Gómez Ruiz',       '1995-03-14', '6461230001', 'mariana@correo.com',  '2026-09-01'),
('Luis',      'Pérez Soto',       '1988-07-22', '6461230002', 'luis@correo.com',     '2026-09-03'),
('Fernanda',  'Castillo Vega',    '2014-11-05', '6461230003', NULL,                  '2026-09-10'),
('Ricardo',   'Navarro León',     '1979-01-30', '6461230004', 'ricardo@correo.com',  '2026-09-15'),
('Paola',     'Ibarra Montes',    '2001-05-09', '6461230005', 'paola@correo.com',    '2026-10-02'),
('Héctor',    'Salas Bravo',      '1965-12-12', '6461230006', NULL,                  '2026-10-08'),
('Valeria',   'Ochoa Duarte',     '2010-08-27', '6461230007', 'valeria@correo.com',  '2026-10-20'),
('Diego',     'Rentería Luna',    '1999-02-18', '6461230008', 'diego@correo.com',    '2026-11-15');
-- Diego (8) aún no tiene historial clínico: no se le puede agendar cita (RN2).

INSERT INTO historial_clinico (id_paciente, alergias, enfermedades, medicamentos, fecha_actualizacion) VALUES
(1, 'Penicilina',  NULL,                     NULL,              '2026-09-01'),
(2, NULL,          'Hipertensión',           'Losartán 50 mg',  '2026-09-03'),
(3, NULL,          NULL,                     NULL,              '2026-09-10'),
(4, 'Látex',       'Diabetes tipo 2',        'Metformina',      '2026-09-15'),
(5, NULL,          NULL,                     NULL,              '2026-10-02'),
(6, 'Ibuprofeno',  'Hipertensión',           'Enalapril',       '2026-10-08'),
(7, NULL,          'Asma',                   'Salbutamol',      '2026-10-20');

INSERT INTO dentista (nombre, apellidos, cedula, telefono, id_especialidad) VALUES
('Andrea',   'Morales Rivas',   'CED-10001', '6469870001', 1),
('Jorge',    'Valdez Cruz',     'CED-10002', '6469870002', 2),
('Claudia',  'Fuentes Ortega',  'CED-10003', '6469870003', 3),
('Samuel',   'Treviño Gil',     'CED-10004', '6469870004', 4),
('Isabel',   'Quintero Lara',   'CED-10005', NULL,         1);
-- Periodoncia (5) todavía no tiene dentistas (participación opcional).

INSERT INTO tratamiento (nombre, descripcion, precio_base) VALUES
('Limpieza dental',       'Profilaxis y pulido',                    600.00),
('Resina',                'Restauración con resina fotocurable',    850.00),
('Extracción simple',     'Extracción de pieza sin cirugía',        700.00),
('Endodoncia',            'Tratamiento de conductos',              3500.00),
('Ajuste de brackets',    'Control mensual de ortodoncia',          900.00),
('Sellador de fosetas',   'Prevención de caries en niños',          400.00),
('Blanqueamiento',        'Blanqueamiento en consultorio',         2800.00),
('Valoración',            'Revisión y diagnóstico inicial',         300.00);

INSERT INTO cita (id_paciente, id_dentista, fecha, hora, motivo, estado) VALUES
(1, 1, '2026-10-05', '09:00', 'Limpieza semestral',       'Atendida'),   -- 1
(2, 3, '2026-10-06', '10:00', 'Dolor en muela',           'Atendida'),   -- 2
(3, 4, '2026-10-07', '16:00', 'Revisión infantil',        'Atendida'),   -- 3
(4, 1, '2026-10-12', '11:00', 'Caries',                   'Atendida'),   -- 4
(5, 2, '2026-10-14', '12:00', 'Control de brackets',      'Atendida'),   -- 5
(6, 1, '2026-10-20', '09:00', 'Extracción',               'Cancelada'),  -- 6
(6, 5, '2026-10-27', '13:00', 'Extracción',               'Atendida'),   -- 7
(7, 4, '2026-11-03', '17:00', 'Selladores',               'Atendida'),   -- 8
(1, 1, '2026-11-10', '09:00', 'Resina en premolar',       'Atendida'),   -- 9
(2, 3, '2026-11-13', '10:00', 'Seguimiento endodoncia',   'Atendida'),   -- 10
(5, 2, '2026-11-18', '12:00', 'Control de brackets',      'Atendida'),   -- 11
(4, 1, '2026-11-25', '11:00', 'Revisión de resina',       'Programada'), -- 12
(3, 4, '2026-11-26', '16:00', 'Limpieza infantil',        'Programada'), -- 13
(7, 5, '2026-11-27', '10:00', 'Blanqueamiento',           'Programada'); -- 14

INSERT INTO detalle_cita (id_cita, id_tratamiento, diente, precio_aplicado) VALUES
(1,  1, NULL, 600.00),
(2,  8, NULL, 300.00),
(2,  4, '36', 3500.00),
(3,  1, NULL, 500.00),   -- descuento infantil
(4,  2, '16', 850.00),
(4,  2, '17', 850.00),
(5,  5, NULL, 900.00),
(7,  3, '48', 700.00),
(8,  6, '36', 400.00),
(8,  6, '46', 400.00),
(9,  2, '24', 850.00),
(10, 8, NULL, 0.00),     -- seguimiento sin costo
(11, 5, NULL, 900.00);

INSERT INTO pago (id_cita, fecha_pago, monto, metodo_pago) VALUES
(1,  '2026-10-05',  600.00, 'Efectivo'),
(2,  '2026-10-06', 1800.00, 'Tarjeta'),
(2,  '2026-10-20', 1000.00, 'Transferencia'),   -- endodoncia en abonos, queda saldo
(3,  '2026-10-07',  500.00, 'Efectivo'),
(4,  '2026-10-12', 1000.00, 'Tarjeta'),          -- queda saldo
(5,  '2026-10-14',  900.00, 'Efectivo'),
(7,  '2026-10-27',  700.00, 'Efectivo'),
(8,  '2026-11-03',  400.00, 'Transferencia'),    -- queda saldo
(9,  '2026-11-10',  850.00, 'Tarjeta'),
(11, '2026-11-18',  500.00, 'Efectivo');          -- queda saldo
