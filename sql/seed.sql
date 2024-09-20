
INSERT INTO services (id_market, cdi, voltage_level) -- crear el servicio
VALUES
(100, 400, 1)

INSERT INTO tariffs (id_market, cdi, voltage_level, "G", "T", "D", "R", "C", "P", "CU")  -- Crear información de tariffa asociada al servicio anterior
VALUES
(100, 400, 1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)


INSERT INTO records (id_service, record_timestamp) -- insertar records asociados al servicio anterior
VALUES
(1, '2024-01-19 00:00:00'),
(1, '2024-01-19 01:00:00'),
(1, '2024-01-19 02:00:00'),
(1, '2024-01-19 03:00:00'),
(1, '2024-01-19 04:00:00'),
(1, '2024-01-19 05:00:00'),
(1, '2024-01-19 06:00:00'),
(1, '2024-01-19 07:00:00'),
(1, '2024-01-19 08:00:00'),
(1, '2024-01-19 09:00:00'),
(1, '2024-01-19 10:00:00')


INSERT INTO injection (id_record, value) -- crear injections relacionado a uno de los records anteriores
VALUES
(2, 15),
(2, 15),
(2, 15),
(2, 15),
(2, 15),
(2, 15),
(2, 15),
(2, 15),
(2, 15),
(2, 15);


INSERT INTO consumption (id_record, value) -- crear consumptions relacionado a uno de los records anteriores
VALUES
(2, 10),
(2, 10),
(2, 10),
(2, 10),
(2, 10),
(2, 10),
(2, 10),
(2, 10),
(2, 10),
(2, 10);

INSERT INTO xm_data_hourly_per_agent (value, record_timestamp)
VALUES 
(0.13, '2024-01-19 02:00:00'),
(0.12, '2024-01-19 00:00:00'),
(0.13, '2024-01-19 01:00:00'),
(0.13, '2024-01-19 03:00:00'), 
(0.13, '2024-01-19 04:00:00'), 
(0.13, '2024-01-19 05:00:00'), 
(0.13, '2024-01-19 06:00:00'), 
(0.13, '2024-01-19 07:00:00'),
(0.13, '2024-01-19 08:00:00'), 
(0.13, '2024-01-19 09:00:00'), 
(0.14, '2024-01-19 10:00:00');



select * from injection i 
select * from services s 
select * from records r 

