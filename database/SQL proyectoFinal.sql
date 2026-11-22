CREATE DATABASE proyectofinal;
USE proyectofinal;
CREATE TABLE usuario (
identificacion INT PRIMARY KEY,
nombre VARCHAR(50) NOT NULL,
apellidoPaterno VARCHAR(50) NOT NULL,
apellidoMaterno VARCHAR(50),
telefono BIGINT NOT NULL,
correo VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE comuna (
idComuna INT PRIMARY KEY,
nombreComuna VARCHAR (50) NOT NULL
);

CREATE TABLE barrio (
idBarrio INT PRIMARY KEY,
nombreBarrio VARCHAR(50) NOT NULL,
idComuna INT NOT NULL, 
FOREIGN KEY (idComuna)
REFERENCES comuna(idComuna)
);

CREATE TABLE estadoSolicitud (
idEstadoSolicitud INT PRIMARY KEY,
nombreEstado VARCHAR(50) NOT NULL
);

CREATE TABLE metodoPago (
idMetodoPago INT PRIMARY KEY,
nombreMetodoPago VARCHAR(50) NOT NULL
);

CREATE TABLE medioTransporte (
idMedioTransporte INT PRIMARY KEY,
nombreMedioTransporte VARCHAR(50) NOT NULL
);

CREATE TABLE estadoDomiciliario (
idEstadoDomiciliario INT PRIMARY KEY,
nombreEstadoDomiciliario VARCHAR(50) NOT NULL
);

CREATE TABLE tipoIncidente(
idTipoIncidente INT PRIMARY KEY,
nombreTipoIncidente VARCHAR(50) NOT NULL
);

CREATE TABLE tipoEstablecimiento(
idTipoEstablecimiento INT PRIMARY KEY,
nombreTipoEstablecimiento VARCHAR(50) NOT NULL
);

CREATE TABLE cliente (
identificacion INT PRIMARY KEY,
FOREIGN KEY (identificacion)
REFERENCES usuario(identificacion),
viaPrincipal VARCHAR(50) NOT NULL,
numero VARCHAR(50) NOT NULL,
idBarrio INT NOT NULL,
FOREIGN KEY (idBarrio)
REFERENCES barrio(idBarrio),
referencia VARCHAR(50)
);

CREATE TABLE domiciliario (
identificacion INT PRIMARY KEY,
FOREIGN KEY (identificacion)
REFERENCES usuario(identificacion),
codigoDomiciliario INT UNIQUE NOT NULL,
idMedioTransporte INT NOT NULL,
FOREIGN KEY (idMedioTransporte)
REFERENCES medioTransporte(idMedioTransporte),
idEstadoDomiciliario INT NOT NULL,
FOREIGN KEY (idEstadoDomiciliario)
REFERENCES estadoDomiciliario(idEstadoDomiciliario)
);

CREATE TABLE establecimiento(
codigoEstablecimiento INT PRIMARY KEY,
nombre VARCHAR(50) NOT NULL,
idTipoEstablecimiento INT NOT NULL,
FOREIGN KEY (idTipoEstablecimiento)
REFERENCES tipoEstablecimiento(idTipoEstablecimiento),
viaPrincipal VARCHAR(50) NOT NULL,
numero VARCHAR(50) NOT NULL,
idBarrio INT NOT NULL,
FOREIGN KEY (idBarrio)
REFERENCES barrio(idBarrio),
telefono BIGINT NOT NULL,
email VARCHAR(50) UNIQUE
);

CREATE TABLE tipoRecogida(
idTipoRecogida INT PRIMARY KEY,
nombreTipoRecogida VARCHAR (50)
);

CREATE TABLE solicitud (
numeroSolicitud INT PRIMARY KEY,
fechaCreacion DATE NOT NULL,
horaCreacion TIME NOT NULL,
identificacionCliente INT NOT NULL,
FOREIGN KEY (identificacionCliente)
REFERENCES cliente(identificacion),
idEstadoSolicitud INT NOT NULL,
FOREIGN KEY(idEstadoSolicitud)
REFERENCES estadoSolicitud(idEstadoSolicitud),
descripcion VARCHAR(50) NOT NULL,
montoTotal DECIMAL(10,2) NOT NULL,
idMetodoPago INT NOT NULL,
FOREIGN KEY (idMetodoPago)
REFERENCES metodoPago(idMetodoPago),
fechaAsignacion DATE,
horaAsignacion TIME,
identificacionDomiciliario INT,
FOREIGN KEY (identificacionDomiciliario)
REFERENCES domiciliario(identificacion),
viaPrincipalExterna VARCHAR(50),
numeroExterno VARCHAR(50),
idBarrioExterno INT,
FOREIGN KEY (idBarrioExterno)
REFERENCES barrio(idBarrio),
codigoEstablecimiento INT,
FOREIGN KEY (codigoEstablecimiento)
REFERENCES establecimiento(codigoEstablecimiento),
CHECK (
    (codigoEstablecimiento IS NOT NULL 
    AND viaPrincipalExterna IS NULL 
    AND numeroExterno IS NULL 
    AND idBarrioExterno IS NULL) 
	OR (codigoEstablecimiento IS NULL 
    AND viaPrincipalExterna IS NOT NULL 
    AND numeroExterno IS NOT NULL 
    AND idBarrioExterno IS NOT NULL)),
idTipoRecogida INT,
FOREIGN KEY (idTipoRecogida)
REFERENCES tipoRecogida(idTipoRecogida)
);

CREATE TABLE incidente (
codigoIncidente INT PRIMARY KEY,
idTipoIncidente INT NOT NULL,
FOREIGN KEY (idTipoIncidente)
REFERENCES tipoIncidente(idTipoIncidente),
descripcion VARCHAR(50) NOT NULL,
fecha DATE NOT NULL,
hora TIME NOT NULL,
numeroSolicitud INT NOT NULL,
FOREIGN KEY (numeroSolicitud)
REFERENCES solicitud(numeroSolicitud)
);

INSERT INTO comuna (idComuna, nombreComuna)
VALUES(2, 'Comuna 2'),
(3, 'Comuna 3'),
(8, 'Comuna 8'),
(12, 'Comuna 12'),
(17, 'Comuna 17'),
(19, 'Comuna 19'),
(22, 'Comuna 22'),
(5, 'Comuna 5'),
(7, 'Comuna 7'),
(4, 'Comuna 4');

INSERT INTO barrio (idBarrio, nombreBarrio, idComuna)
VALUES(1, 'Villa Colombia', 8),
(2, 'Ciudad Jardín', 22),
(3, 'Granada', 2),
(4, 'Bosques del limonar', 17),
(5, 'Prados del norte', 2),
(6, 'Chipichape', 2),
(7, 'Valle del Lili', 17),
(8, 'La floresta', 12),
(9, 'Eucaristico', 19),
(10, 'El Peñol', 3);

INSERT INTO estadoSolicitud(idEstadoSolicitud, nombreEstado)
VALUES (1, 'Creada'),
(2, 'Asignada'),
(3, 'En curso'),
(4, 'Finalizada'),
(5, 'Cancelada');

INSERT INTO metodoPago(idMetodoPago, nombreMetodoPago)
VALUES (1, 'Efectivo'),
(2, 'Electrónico'),
(3, 'Ninguno');

INSERT INTO medioTransporte (idMedioTransporte, nombreMedioTransporte)
VALUES(1, 'Bicicleta'),
(2, 'Motocicleta'),
(3, 'Automovil');

INSERT INTO estadoDomiciliario (idEstadoDomiciliario, nombreEstadoDomiciliario)
VALUES(1, 'Activo'),
(2, 'Inactivo');

INSERT INTO tipoIncidente (idTipoIncidente, nombreTipoIncidente)
VALUES(1, 'Retraso'),
(2, 'Direccion incorrecta'),
(3, 'Cliente no responde'),
(4, 'Establecimiento no entrega');

INSERT INTO tipoEstablecimiento (idTipoEstablecimiento, nombreTipoEstablecimiento)
VALUES(1, 'Restaurante'),
(2, 'Farmacia'),
(3, 'Supermercado'),
(4, 'Tienda especializada');

INSERT INTO tipoRecogida (idTipoRecogida, nombreTipoRecogida)
VALUES(1, 'Externa'),
(2, 'Establecimiento');

INSERT INTO usuario(identificacion,nombre, apellidoPaterno, apellidoMaterno, telefono, correo)
VALUES (34323237, 'Milena', 'Hurtado', 'Solano',3164926613,  'milena2153@hotmail.com'),
(25276291, 'Elizabeth', 'Cabezas', 'Burbano', 3188647400,'elizabeth.cabe@gmail.com'),
(10558214, 'Harold', 'Caicedo', 'Dinas', 3152732949, 'harolc@gmail.com'),
(102387546, 'Pablo Andrés', 'Ordoñez', 'López', 3168318786, 'pa_ordoñez@gmail.com'),
(1029546359, 'Lina Sofía', 'Vasquez', 'Muñoz', 3247284326, 'sofvasquez14@gmail.com'),
(12546302,  'Anastacio', 'Bermudez', 'Alvarado', 3210546925, 'abermudez@gmail.com'),
(254632126, 'Rosalba', 'Rodriguez', 'Meneses', 3121546325, 'rodriguezrosalba@hotmail.com'),
(111203654, 'Renatto', 'Castaño', 'Lombariza', 3102365489, 'clrenatto@gmail.com'),
(19856423,  'Alberto', 'Manquillo', 'Zapata', 3203654126, 'albertmanq9@hotmail.com'),
(125463203, 'Salomé', 'Chilito', 'Mina', 3652136524, 'minachilisa@hotmail.com');

INSERT INTO cliente (identificacion, viaPrincipal, numero, idBarrio, referencia)
VALUES (34323237, 'Calle 49', '13-22', 1, 'Local comercial'),
(102387546, 'Carrera 103', '12-55', 2, 'Condominio Parque del Sol'),
(1029546359, 'Calle 15 Norte', '9-30', 3, 'Apartamento 2 piso'),
(25276291, 'Carrera 66', '13-10', 4, 'Conjunto Torres del Limonar'),
(19856423, 'Avenida 3 Bis Norte', '32-25', 5, 'Edificio Prados del Norte');

INSERT INTO domiciliario (identificacion, codigoDomiciliario, idMedioTransporte, idEstadoDomiciliario)
VALUES (10558214, 102, 2, 1),
(12546302, 103, 2, 1),
(254632126, 104, 2, 2),
(111203654, 105, 1, 1),
(125463203, 106, 3, 2);

INSERT INTO establecimiento(codigoEstablecimiento, nombre, idTipoEstablecimiento, viaPrincipal, numero, idBarrio, telefono, email)
VALUES (860076919, 'Crepes & Waffles', 1, 'Avenida Roosevelt', '37-07', 9,  6767610, 'crepeswaffles@gmail.com'),
(71653570, 'Krika', 4, 'Carrera 100', '15-61', 2, 3130404, 'krika@gmail.com'),
(890900608, 'Carulla', 3, 'Calle 4', '34-04', 9, 3316262, 'servicioalclientecarulla@clientesexito.com'),
(860512330, 'Servientrega', 4, 'Carrera 85', '15-99', 7, 7700200, 'servicioalcliente@servientrega.com'),
(800251569, 'Inter Rapidísimo S.A.', 4, 'Avenida Roosevelt', '41-1', 6, 3232554455, 'defensaconsumidor@interrapidisimo.com'),
(800149695, 'Cruz Verde', 2, 'Avenida Colombia', '1-52', 10, 5240505, 'servicioalcliente@cruzverde.com.co'),
(805028991, 'Surtifamiliar', 3, 'Calle 9', '23-65', 1, 3217007997, 'contacto@surtifamiliar.com'),
(891408584, 'Frisby', 1, 'Avenida Roosevelt', '28-70', 9, 3015555555,'coordselnacional@frisby.com.co'),
(901314314, 'Droquímicos Cali', 4, 'Calle 32', '15-55', 8, 3145859622,'droquimicosdecali@gmail.com'),
(830129327, 'Farmatodo', 2, 'Carrera 1', '1-50', 10, 4841000, 'contactenos@farmatodo.com');

INSERT INTO Solicitud(numeroSolicitud, fechaCreacion, horaCreacion, identificacionCliente, idEstadoSolicitud, descripcion, montoTotal, idMetodoPago, fechaAsignacion, 
horaAsignacion, identificacionDomiciliario, viaPrincipalExterna, numeroExterno, idBarrioExterno, codigoEstablecimiento, idTipoRecogida) 
VALUES(1001, '2026-02-15', '09:28', 34323237, 4, 'Paquete', 30000, 1, '2026-02-15', '14:03', 12546302, 'Calle 23', '17-20', 8, NULL, 1),
(1002, '2026-04-17', '13:15', 102387546, 5, 'Encomienda', 26000, 3, NULL, NULL, NULL, NULL, NULL, NULL, 860512330,2),
(1003, '2026-05-03', '18:40', 1029546359, 2, 'Productos de cosmética (delicado)', 55000, 2, '2026-05-04', '11:12', 254632126, 'Calle 38N', '6N-47', 6, NULL,1),
(1004, '2026-05-20', '08:11', 25276291, 4, 'Artículos de limpieza', 40000, 1, '2026-05-24', '17:20', 111203654, 'Carrera 10', '10-22', 9, NULL,1),
(1005, '2026-06-23', '22:36', 102387546, 4, 'Comida', 32000, 1, '2026-06-23', '23:10', 254632126, NULL, NULL, NULL, 860076919,2),
(1006, '2026-06-30', '10:07', 25276291, 3, 'Verduras', 15000, 1, '2026-06-30', '11:00', 125463203, NULL, NULL, NULL, 805028991,2),
(1007, '2026-07-05', '13:00', 34323237, 2, 'Pollo', 21900, 2, '2026-07-05', '13:30', 12546302, NULL, NULL, NULL, 891408584,2),
(1008, '2026-07-07', '17:10', 1029546359, 5, 'Naproxeno x 2', 24000, 3, NULL, NULL, NULL, NULL, NULL, NULL, 800149695,2),
(1009, '2026-08-24', '11:30', 102387546, 1, 'Esmaltes X5', 40000, 2, NULL, NULL, NULL, NULL, NULL, NULL, 830129327,2),
(1010, '2026-08-29', '20:05', 25276291, 3, 'Cinta elástica', 9000, 1, '2026-08-30', '09:00', 254632126, 'Avenida Circunvalar', '66-21', 4, NULL,1);

INSERT INTO incidente(codigoIncidente, idTipoIncidente, descripcion, fecha, hora, numeroSolicitud)
VALUES (1010, 1, 'Se retrasó el domiciliario', '2026-06-23', '23:30', 1005),
(1011, 2, 'La dirección indicada era incorrecta', '2026-05-24', '18:00', 1004),
(1012, 4, 'No se entregó al domiciliario', '2026-04-19', '16:30', 1002),
(1013, 1, 'Se retrazó el domiciliario en la ruta', '2026-05-04', '13:00', 1003),
(1014, 3, 'No responde el cliente', '2026-06-23', '23:59', 1005),
(1015, 1, 'Accidente colisión a la bicicleta', '2026-05-24', '17:30', 1004),
(1016, 1, 'Derrame del producto', '2026-07-05', '14:00', 1007),
(1017, 2, 'Dirección no coincide', '2026-08-30', '09:30', 1010),
(1018, 3, 'El cliente no tiene señal', '2026-07-07', '17:20', 1008),
(1019, 4, 'No hay disponibilidad de producto', '2026-07-07', '17:20', 1008);

SELECT s.numeroSolicitud, u.identificacion AS 'ID cliente', u.nombre, u.apellidoPaterno, e.nombreEstado AS 'Estado', m.nombreMetodoPago AS 'Metodo de pago'
FROM solicitud s
JOIN usuario u
ON s.identificacionCliente = u.identificacion
JOIN metodopago m
ON s.idMetodoPago = m.idMetodoPago
JOIN estadosolicitud e
ON s.idEstadoSolicitud = e.idEstadoSolicitud;

SELECT s.numeroSolicitud, u.identificacion AS 'ID domiciliario', u.nombre, u.apellidoPaterno, m.nombreMedioTransporte AS 'Medio Transporte'
FROM solicitud s
JOIN usuario u
ON s.identificacionDomiciliario = u.identificacion
JOIN domiciliario d
ON s.identificacionDomiciliario = d.identificacion
JOIN mediotransporte m
ON d.idMedioTransporte = m.idMedioTransporte;

SELECT s.numeroSolicitud, u.identificacion AS 'ID domiciliario', u.nombre, u.apellidoPaterno
FROM solicitud s
LEFT JOIN usuario u
ON s.identificacionDomiciliario = u.identificacion;

SELECT i.codigoIncidente, t.nombreTipoIncidente AS 'Tipo incidente', i.numeroSolicitud, s.identificacionCliente, s.identificacionDomiciliario
FROM incidente i
JOIN tipoincidente t
ON i.idTipoIncidente = t.idTipoIncidente
JOIN solicitud s
ON i.numeroSolicitud = s.numeroSolicitud;

SELECT u.nombre AS 'Nombre cliente', COUNT(s.numeroSolicitud) AS 'Total solicitudes'
FROM cliente c
LEFT JOIN solicitud s
ON c.identificacion = s.identificacionCliente
JOIN usuario u
ON c.identificacion = u.identificacion
GROUP BY u.identificacion, u.nombre;

SELECT e.nombre AS 'Nombre establecimiento', SUM(s.montoTotal) AS 'Total vendido'
FROM establecimiento e 
JOIN solicitud s
ON e.codigoEstablecimiento = s.codigoEstablecimiento
GROUP BY e.codigoEstablecimiento, e.nombre;

SELECT c.identificacion, u.nombre AS 'Nombre cliente'
FROM cliente c
JOIN usuario u
ON c.identificacion = u.identificacion
WHERE NOT EXISTS (
SELECT 1
FROM solicitud s
WHERE c.identificacion = s.identificacionCliente
);

SELECT d.identificacion, u.nombre AS 'Nombre domiciliario'
FROM domiciliario d
JOIN usuario u
ON d.identificacion = u.identificacion
WHERE d.identificacion NOT IN (
SELECT s.identificacionDomiciliario
FROM solicitud s
WHERE d.identificacion = s.identificacionDomiciliario
);

SELECT numeroSolicitud AS 'Solicitudes sin incidentes'
FROM solicitud s
WHERE s.numeroSolicitud NOT IN ( 
SELECT i.numeroSolicitud
FROM incidente i 
WHERE s.numeroSolicitud = i.numeroSolicitud );

-- Clientes que han realizado pedidos en los establecimientos de tipo Restaurante o Farmacia, ordenados por el monto que han gastado Limite de 3--
SELECT s.identificacionCliente, u.nombre, u.apellidoPaterno, COUNT(s.numeroSolicitud) AS 'total pedidos', SUM(s.montoTotal) AS 'monto gastado'
FROM solicitud s
JOIN usuario u
ON s.identificacionCliente = u.identificacion 
WHERE s.codigoEstablecimiento IN (
SELECT e.codigoEstablecimiento
FROM establecimiento e
JOIN tipoestablecimiento t
ON e.idTipoEstablecimiento = t.idTipoEstablecimiento
WHERE t.nombreTipoEstablecimiento IN ('Restaurante', 'Farmacia')
) 
GROUP BY s.identificacionCliente, u.nombre, u.apellidoPaterno
ORDER BY SUM(s.montoTotal) DESC
LIMIT 3;

SELECT  u.identificacion, u.nombre, u.apellidoPaterno,
    CASE
        WHEN c.identificacion IS NOT NULL AND d.identificacion IS NOT NULL THEN 'Ambos (Cliente y Domiciliario)'
        WHEN c.identificacion IS NOT NULL THEN 'Cliente'
        WHEN d.identificacion IS NOT NULL THEN 'Domiciliario'
        ELSE 'Sin Rol Asignado'
    END AS tipoUsuario
FROM usuario u
LEFT JOIN cliente c 
    ON u.identificacion = c.identificacion
LEFT JOIN domiciliario d 
    ON u.identificacion = d.identificacion
WHERE u.identificacion = 34323237;

DELIMITER $$

CREATE FUNCTION fn_calcular_franja(horaCreacion TIME)
RETURNS VARCHAR (20)
DETERMINISTIC
BEGIN
	DECLARE franjaHoraria VARCHAR (20);
    
    IF horaCreacion >= '06:00:00' AND horaCreacion <= '11:59:59' THEN
		SET franjaHoraria = 'Jornada mañana';
	ELSEIF horaCreacion >= '12:00:00' AND horaCreacion <= '17:59:59' THEN
		SET franjaHoraria = 'Jornada tarde';
	ELSEIF horaCreacion >= '18:00:00' AND horaCreacion <= '23:59:59' THEN
		SET franjaHoraria = 'Jornada noche';
	ELSE
		SET franjaHoraria = 'Jornada madrugada';
	END IF;
    RETURN franjaHoraria;
END $$    

DELIMITER ;

SELECT numeroSolicitud, identificacionCliente, u.nombre, u.apellidoPaterno AS 'apellido',
		fn_calcular_franja(horaCreacion) AS 'Franja horaria'        
FROM solicitud s
JOIN usuario u
ON s.identificacionCliente = u.identificacion;

DELIMITER $$

CREATE PROCEDURE insertar_cliente (
	IN p_identificacion INT,
	IN p_nombre VARCHAR (50),
    IN p_apellidoPaterno VARCHAR (50),
    IN p_apellidoMaterno VARCHAR (50),
    IN p_telefono BIGINT,
    IN p_correo VARCHAR (50),
    IN p_viaPrincipal VARCHAR (50),
    IN p_numero VARCHAR (50),
    IN p_idBarrio INT,
    IN p_referencia VARCHAR (50)
)
BEGIN
	INSERT INTO usuario(identificacion, nombre, apellidoPaterno, apellidoMaterno, 
						telefono, correo)
	VALUES (p_identificacion, p_nombre, p_apellidoPaterno, p_apellidoMaterno, 
						p_telefono, p_correo);
                        
	INSERT INTO cliente(identificacion, viaPrincipal, numero, idBarrio, referencia)
    VALUES (p_identificacion, p_viaPrincipal, p_numero, p_idBarrio, p_referencia);
END $$

DELIMITER ;

CALL insertar_cliente (11664645, 'Julian', 'Diaz', 'Hurtado', 3115423612, 'juliandh@gmail.com', 'Carrera 36a Bis', '8-20', 10, 'Apartaestudios');

DELIMITER $$

CREATE PROCEDURE insertar_domiciliario (
	IN p_identificacion INT,
	IN p_nombre VARCHAR (50),
    IN p_apellidoPaterno VARCHAR (50),
    IN p_apellidoMaterno VARCHAR (50),
    IN p_telefono BIGINT,
    IN p_correo VARCHAR (50),
    IN p_codigoDomiciliario INT,
    IN p_idMedioTransporte INT,
    IN p_idEstadoDomiciliario INT
)
BEGIN
	INSERT INTO usuario(identificacion, nombre, apellidoPaterno, apellidoMaterno, 
						telefono, correo)
	VALUES (p_identificacion, p_nombre, p_apellidoPaterno, p_apellidoMaterno, 
						p_telefono, p_correo);
                        
	INSERT INTO domiciliario(identificacion, codigoDomiciliario, idMedioTransporte, idEstadoDomiciliario)
    VALUES (p_identificacion, p_codigoDomiciliario, p_idMedioTransporte, p_idEstadoDomiciliario);
END $$

DELIMITER ;

CALL insertar_domiciliario (1007854, 'Ignacio', 'Gil', 'Meza', 3166485694, 'gilmezaig@gmail.com', 107, 3, 2);

DELIMITER $$

CREATE TRIGGER cambiar_estado_incidente
AFTER INSERT ON incidente
FOR EACH ROW
BEGIN
	IF NEW.idTipoIncidente = 4 THEN
		UPDATE solicitud
		SET idEstadoSolicitud = 5
		WHERE numeroSolicitud = NEW.numeroSolicitud;
    END IF;
END $$

DELIMITER ;

INSERT INTO incidente (codigoIncidente, idTipoIncidente, descripcion, fecha, hora, numeroSolicitud)
VALUES (1020, 4, 'El restaurante cerró', '2026-06-30', '12:12:00', 1006);

DELIMITER $$

CREATE TRIGGER control_estado_solicitud
BEFORE UPDATE ON solicitud
FOR EACH ROW
BEGIN
	IF OLD.idEstadoSolicitud != NEW.idEstadoSolicitud THEN
		IF OLD.idEstadoSolicitud IN (4,5) THEN
			SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No se puede cambiar una solicitud "Cancelada" o "Finalizada"';
		END IF;
        IF OLD.idEstadoSolicitud = 1 AND NEW.idEstadoSolicitud NOT IN (2,5) THEN
			SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Una solicitud creada solo puede pasar a "Asignada" o "Cancelada"';
		END IF;
		IF OLD.idEstadoSolicitud = 2 AND NEW.idEstadoSolicitud NOT IN (3,5) THEN
			SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Una solicitud asignada solo puede pasar a "En curso" o "Cancelada"';
		END IF;	
		IF NEW.idEstadoSolicitud = 4 AND NEW.idMetodoPago = 3 THEN
			SIGNAL SQLSTATE '45000'
			SET MESSAGE_TEXT = 'No se puede finalizar una solicitud con método de pago "Ninguno"';
		END IF;
        IF NEW.idEstadoSolicitud = 5 THEN
			SET NEW.idMetodoPago = 3;
		END IF;
        IF NEW.idEstadoSolicitud = 2 THEN 
			IF NEW.identificacionDomiciliario IS NULL THEN
				SIGNAL SQLSTATE '45000'
				SET MESSAGE_TEXT = 'Debe asignar un domiciliario para cambiar al estado "Asignada"';
			END IF;
        END IF;	
	END IF;
    IF NEW.idMetodoPago != 3 AND NEW.idEstadoSolicitud = 5 THEN
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Si la solicitud esta "Cancelada" no se puede asignar otro método de pago';
	END IF;
    IF NEW.idMetodoPago = 3 AND NEW.idEstadoSolicitud = 4 THEN
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Si la solicitud esta "Finalizada" no se puede asignar método de pago "Ninguno"';
	END IF;
END $$

DELIMITER ;

-- UPDATE solicitud
-- SET idMetodoPago = 3
-- WHERE numeroSolicitud = 1001;

DELIMITER $$

CREATE PROCEDURE asignar_solicitud(
    IN p_numeroSolicitud INT,
    IN p_identificacionDomiciliario INT
)
BEGIN
    DECLARE variable_estadoSolicitud INT;
    DECLARE variable_estadoDomiciliario INT;

    SELECT idEstadoSolicitud INTO variable_estadoSolicitud
    FROM solicitud
    WHERE numeroSolicitud = p_numeroSolicitud;

    SELECT idEstadoDomiciliario INTO variable_estadoDomiciliario
    FROM domiciliario
    WHERE identificacion = p_identificacionDomiciliario;

    IF variable_estadoSolicitud IS NULL THEN
        SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: La solicitud no existe.';
    ELSEIF variable_estadoSolicitud != 1 THEN
        SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: Solo se pueden asignar solicitudes en estado Creada (1).';
    ELSEIF variable_estadoDomiciliario IS NULL THEN
        SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: El domiciliario no existe.';
    ELSEIF variable_estadoDomiciliario != 1 THEN
        SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: El domiciliario está Inactivo y no puede recibir pedidos.';
    ELSE
        UPDATE solicitud
        SET identificacionDomiciliario = p_identificacionDomiciliario,
            idEstadoSolicitud = 2, 
            fechaAsignacion = CURDATE(),
            horaAsignacion = CURTIME()
        WHERE numeroSolicitud = p_numeroSolicitud;
    END IF;
END $$

DELIMITER ;

-- CALL asignar_solicitud(1009, 25463212);

DELIMITER $$

CREATE PROCEDURE crear_solicitud(
    IN p_numeroSolicitud INT,
	IN p_identificacionCliente INT,
    IN p_descripcion VARCHAR (50),
    IN p_montoTotal DECIMAL(10, 2),
    IN p_idMetodoPago INT,
    IN p_viaPrincipalExterna VARCHAR (50),
    IN p_numeroExterno VARCHAR (50),
    IN p_idBarrioExterno INT,
    IN p_codigoEstablecimiento INT,
    IN p_idTipoRecogida INT
)
BEGIN
    DECLARE variable_clienteExiste INT;

    SELECT COUNT(*) INTO variable_clienteExiste
    FROM cliente
    WHERE identificacion = p_identificacionCliente;

    IF variable_clienteExiste = 0 THEN
        SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: El cliente no está registrado en el sistema';
	END IF;
    IF p_montoTotal <= 0 THEN
        SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: El monto total de la solicitud debe ser mayor a cero (0)';
	END IF;
    IF p_codigoEstablecimiento IS NOT NULL AND (p_viaPrincipalExterna IS NOT NULL OR p_numeroExterno IS NOT NULL OR p_idBarrioExterno IS NOT NULL)THEN
        SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: Si selecciona un establecimiento externo no debe ingresar direccion de recogida';
	END IF;
    IF p_codigoEstablecimiento IS NULL AND (p_viaPrincipalExterna IS NULL OR p_numeroExterno IS NULL OR p_idBarrioExterno IS NULL)THEN
        SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: Debe indicar un establecimiento o una direccion de recogida';
	END IF;
    IF p_idTipoRecogida = 1 AND p_codigoEstablecimiento IS NOT NULL THEN
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: Si la dirección de recogida es en establecimiento el tipo de recogida debe ser "Establecimiento"(2)';
	END IF;
	IF p_idTipoRecogida = 2 AND p_codigoEstablecimiento IS NULL THEN
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: Si la dirección de recogida es externa el tipo de recogida debe ser "Externa"(1)';
	END IF;
    
    INSERT INTO Solicitud(numeroSolicitud, fechaCreacion, horaCreacion, identificacionCliente, idEstadoSolicitud, descripcion, montoTotal, idMetodoPago, fechaAsignacion, 
						horaAsignacion, identificacionDomiciliario, viaPrincipalExterna, numeroExterno, idBarrioExterno, codigoEstablecimiento, idTipoRecogida)
	VALUES(p_numeroSolicitud, CURDATE(), CURTIME(), p_identificacionCliente, 1, p_descripcion, p_montoTotal, p_idMetodoPago, NULL, 
						NULL, NULL, p_viaPrincipalExterna, p_numeroExterno, p_idBarrioExterno, p_codigoEstablecimiento, p_idTipoRecogida);
END $$

DELIMITER ;

-- CALL crear_solicitud(1011, 34323237,'Combo hamburguesa', 1000, 2, NULL, NULL, NULL, NULL, 1);

DELIMITER $$

CREATE PROCEDURE facturacion_total()
BEGIN
	DECLARE fin INT DEFAULT 0;
    DECLARE v_monto DECIMAL(10, 2);
    DECLARE v_metodoPago INT;
    DECLARE v_totalEfectivo DECIMAL(10, 2) DEFAULT 0.00 ;
    DECLARE v_totalElectronico DECIMAL(10, 2) DEFAULT 0.00 ;
    DECLARE cur_pagos CURSOR FOR
		SELECT montoTotal, idMetodoPago
        FROM solicitud
        WHERE idEstadoSolicitud = 4;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET fin = 1;
	OPEN cur_pagos;
    
    ciclo: LOOP
		FETCH cur_pagos INTO v_monto, v_metodoPago;
        IF fin = 1 THEN LEAVE ciclo;
        END IF;
        IF v_metodoPago = 1 THEN 
			SET v_totalEfectivo = v_totalEfectivo + v_monto;
		ELSE 
			SET v_totalElectronico = v_totalElectronico + v_monto;
		END IF;
	END LOOP ciclo;
	CLOSE cur_pagos;
    SELECT v_totalEfectivo AS 'Dinero Total efectivo', v_totalElectronico AS 'Dinero Total electrónico',
    (v_totalEfectivo + v_totalElectronico) AS 'Total general';
END $$
    
DELIMITER ;

CALL facturacion_total();

