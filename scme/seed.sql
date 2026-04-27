-- seed.sql: datos de prueba
SET NOCOUNT ON;

-- Insert TipoSangre if missing
IF NOT EXISTS (SELECT 1 FROM dbo.TipoSangre WHERE Nombre = 'A+')
	INSERT INTO dbo.TipoSangre (Nombre) VALUES ('A+');
IF NOT EXISTS (SELECT 1 FROM dbo.TipoSangre WHERE Nombre = 'O+')
	INSERT INTO dbo.TipoSangre (Nombre) VALUES ('O+');

-- Insert PersonaEmergencia if missing
IF NOT EXISTS (SELECT 1 FROM dbo.PersonaEmergencia WHERE Nombres='Maria' AND Apellidos='Gomez' AND TelefonoPersonal='60011122')
	INSERT INTO dbo.PersonaEmergencia (Nombres,Apellidos,TelefonoPersonal) VALUES ('Maria','Gomez','60011122');

-- Insert Persona if missing (based on CI)
IF NOT EXISTS (SELECT 1 FROM dbo.Persona WHERE CI='1234567')
BEGIN
	DECLARE @IdTipoSangre INT = (SELECT TOP 1 IdSangre FROM dbo.TipoSangre WHERE Nombre='A+');
	DECLARE @IdPersonaEmergencia INT = (SELECT TOP 1 IdPersonaEmergencia FROM dbo.PersonaEmergencia WHERE Nombres='Maria' AND Apellidos='Gomez');
	INSERT INTO dbo.Persona (Nombres,Apellidos,FechaNacimiento,Correo,TelefonoPersonal,CI,Genero,IdTipoSangre,IdPersonaEmergencia)
	VALUES ('Carlos','Lopez','1990-01-01','carlos@example.com','71234567','1234567','M', @IdTipoSangre, @IdPersonaEmergencia);
END

-- Insert PerfilAccesoLab if missing
IF NOT EXISTS (SELECT 1 FROM dbo.PerfilAccesoLab WHERE Nombre='Laboratorio A')
	INSERT INTO dbo.PerfilAccesoLab (Nombre) VALUES ('Laboratorio A');

-- Insert Tarjeta if missing
IF NOT EXISTS (SELECT 1 FROM dbo.Tarjeta WHERE TarjetaUID='UID123456')
	INSERT INTO dbo.Tarjeta (TarjetaUID, FechaFabricacion) VALUES ('UID123456','2023-01-01');

-- Insert Enrolar if missing
IF NOT EXISTS (
	SELECT 1 FROM dbo.Enrolar e
	WHERE e.TarjetaUID='UID123456' AND e.IdPersona = (SELECT TOP 1 IdPersona FROM dbo.Persona WHERE CI='1234567')
)
BEGIN
	INSERT INTO dbo.Enrolar (IdPersona, TarjetaUID, IdPerfilAccesoLab)
	VALUES ((SELECT TOP 1 IdPersona FROM dbo.Persona WHERE CI='1234567'), 'UID123456', (SELECT TOP 1 IdPerfilAccesoLab FROM dbo.PerfilAccesoLab WHERE Nombre='Laboratorio A'));
END

-- Insert TipoMovimiento and TipoDispositivo if missing
IF NOT EXISTS (SELECT 1 FROM dbo.TipoMovimiento WHERE Nombre='Entrada')
	INSERT INTO dbo.TipoMovimiento (Nombre) VALUES ('Entrada');
IF NOT EXISTS (SELECT 1 FROM dbo.TipoDispositivo WHERE Nombre='Controladora-1')
	INSERT INTO dbo.TipoDispositivo (Nombre) VALUES ('Controladora-1');

-- Insert RegistroAcceso if not exists exact
IF NOT EXISTS (
	SELECT 1 FROM dbo.RegistroAcceso r
	WHERE r.TarjetaUID='UID123456' AND r.IdTipoMovimiento = (SELECT TOP 1 IdTipoMovimiento FROM dbo.TipoMovimiento WHERE Nombre='Entrada')
	  AND r.IdTipoDispositivo = (SELECT TOP 1 IdTipoDispositivo FROM dbo.TipoDispositivo WHERE Nombre='Controladora-1')
	  AND r.Descripcion = 'Acceso de prueba'
)
BEGIN
	INSERT INTO dbo.RegistroAcceso (TarjetaUID, IdTipoMovimiento, IdTipoDispositivo, Descripcion)
	VALUES ('UID123456', (SELECT TOP 1 IdTipoMovimiento FROM dbo.TipoMovimiento WHERE Nombre='Entrada'), (SELECT TOP 1 IdTipoDispositivo FROM dbo.TipoDispositivo WHERE Nombre='Controladora-1'), 'Acceso de prueba');
END

GO

-- Create table Dispositivos (device registry) and insert a test device with api_key
IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.Dispositivos') AND type in (N'U'))
BEGIN
	CREATE TABLE dbo.Dispositivos (
		IdDispositivo INT IDENTITY(1,1) PRIMARY KEY,
		Nombre NVARCHAR(200) NOT NULL,
		ApiKey NVARCHAR(200) NOT NULL UNIQUE,
		Activo BIT NOT NULL DEFAULT(1),
		FechaRegistro DATETIME NOT NULL DEFAULT(GETDATE())
	);
END

IF NOT EXISTS (SELECT 1 FROM dbo.Dispositivos WHERE ApiKey = 'MI_PRUEBA_CLAVE')
BEGIN
	INSERT INTO dbo.Dispositivos (Nombre, ApiKey, Activo) VALUES ('ESP32-Test','MI_PRUEBA_CLAVE', 1);
END


-- verification selects
SELECT 'TipoSangre' AS tabla, IdSangre, Nombre FROM dbo.TipoSangre ORDER BY IdSangre;
SELECT 'PersonaEmergencia' AS tabla, IdPersonaEmergencia, Nombres, Apellidos, TelefonoPersonal FROM dbo.PersonaEmergencia ORDER BY IdPersonaEmergencia;
SELECT 'Persona' AS tabla, IdPersona, Nombres, Apellidos, Correo, CI FROM dbo.Persona ORDER BY IdPersona;
SELECT 'Tarjeta' AS tabla, IdTarjeta, TarjetaUID, FechaFabricacion FROM dbo.Tarjeta ORDER BY IdTarjeta;
SELECT 'Enrolar' AS tabla, IdEnrolar, IdPersona, TarjetaUID, IdPerfilAccesoLab FROM dbo.Enrolar ORDER BY IdEnrolar;
SELECT 'RegistroAcceso' AS tabla, IdRegistroAcceso, TarjetaUID, FechaHora, IdTipoMovimiento, IdTipoDispositivo, Descripcion FROM dbo.RegistroAcceso ORDER BY IdRegistroAcceso DESC;
