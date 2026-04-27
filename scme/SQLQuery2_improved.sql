-- SQLQuery2_improved.sql
-- Idempotent, safe create script for ReportesSistemaSeguridad
-- Run this script using sqlcmd or SSMS

SET NOCOUNT ON;

-- Ensure database exists
IF DB_ID('ReportesSistemaSeguridad') IS NULL
BEGIN
    PRINT 'Creating database ReportesSistemaSeguridad...';
    CREATE DATABASE ReportesSistemaSeguridad;
END
GO

USE ReportesSistemaSeguridad;
GO

-- Drop children first to ensure clean re-create (use with caution on production)
IF OBJECT_ID('dbo.RegistroAcceso','U') IS NOT NULL DROP TABLE dbo.RegistroAcceso;
IF OBJECT_ID('dbo.Enrolar','U') IS NOT NULL DROP TABLE dbo.Enrolar;
IF OBJECT_ID('dbo.Bitacora','U') IS NOT NULL DROP TABLE dbo.Bitacora;
IF OBJECT_ID('dbo.DetalleRolPermiso','U') IS NOT NULL DROP TABLE dbo.DetalleRolPermiso;
IF OBJECT_ID('dbo.UsuarioSistema','U') IS NOT NULL DROP TABLE dbo.UsuarioSistema;
IF OBJECT_ID('dbo.Permisos','U') IS NOT NULL DROP TABLE dbo.Permisos;
IF OBJECT_ID('dbo.RolSistema','U') IS NOT NULL DROP TABLE dbo.RolSistema;
IF OBJECT_ID('dbo.Persona','U') IS NOT NULL DROP TABLE dbo.Persona;
IF OBJECT_ID('dbo.PersonaEmergencia','U') IS NOT NULL DROP TABLE dbo.PersonaEmergencia;
IF OBJECT_ID('dbo.TipoSangre','U') IS NOT NULL DROP TABLE dbo.TipoSangre;
IF OBJECT_ID('dbo.Tarjeta','U') IS NOT NULL DROP TABLE dbo.Tarjeta;
IF OBJECT_ID('dbo.PerfilAccesoLab','U') IS NOT NULL DROP TABLE dbo.PerfilAccesoLab;
IF OBJECT_ID('dbo.TipoMovimiento','U') IS NOT NULL DROP TABLE dbo.TipoMovimiento;
IF OBJECT_ID('dbo.TipoDispositivo','U') IS NOT NULL DROP TABLE dbo.TipoDispositivo;
GO

-- Create tables
CREATE TABLE dbo.TipoSangre (
    IdSangre INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Estado TINYINT DEFAULT 1
);
GO

CREATE TABLE dbo.PersonaEmergencia (
    IdPersonaEmergencia INT IDENTITY(1,1) PRIMARY KEY,
    Nombres VARCHAR(100) NOT NULL,
    Apellidos VARCHAR(100) NOT NULL,
    TelefonoPersonal VARCHAR(20) NOT NULL,
    Estado TINYINT DEFAULT 1
);
GO

CREATE TABLE dbo.Persona (
    IdPersona INT IDENTITY(1,1) PRIMARY KEY,
    Nombres VARCHAR(100) NOT NULL,
    Apellidos VARCHAR(100) NOT NULL,
    FechaNacimiento DATE NULL,
    Correo VARCHAR(100) NOT NULL,
    TelefonoPersonal VARCHAR(20) NOT NULL,
    CI VARCHAR(20) NOT NULL,
    Genero CHAR(1) NOT NULL CHECK (Genero IN('M','F')),
    IdTipoSangre INT NULL,
    IdPersonaEmergencia INT NULL,
    Estado TINYINT DEFAULT 1,
    CONSTRAINT FK_Persona_TipoSangre FOREIGN KEY(IdTipoSangre) REFERENCES dbo.TipoSangre(IdSangre),
    CONSTRAINT FK_Persona_PersonaEmergencia FOREIGN KEY(IdPersonaEmergencia) REFERENCES dbo.PersonaEmergencia(IdPersonaEmergencia)
);
GO

CREATE TABLE dbo.RolSistema (
    IdRol INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Estado TINYINT DEFAULT 1
);
GO

CREATE TABLE dbo.UsuarioSistema (
    IdUsuario INT IDENTITY(1,1) PRIMARY KEY,
    IdPersona INT NOT NULL,
    NombreUsuario VARCHAR(50) UNIQUE NOT NULL,
    Contrasena VARCHAR(255) NOT NULL,
    IdRol INT NOT NULL,
    Estado TINYINT DEFAULT 1,
    CONSTRAINT FK_UsuarioSistema_Persona FOREIGN KEY(IdPersona) REFERENCES dbo.Persona(IdPersona),
    CONSTRAINT FK_UsuarioSistema_Rol FOREIGN KEY(IdRol) REFERENCES dbo.RolSistema(IdRol)
);
GO

CREATE TABLE dbo.Permisos (
    IdPermisos INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL,
    Estado TINYINT DEFAULT 1
);
GO

CREATE TABLE dbo.DetalleRolPermiso (
    IdDetalleRolPermiso INT IDENTITY(1,1) PRIMARY KEY,
    IdPermiso INT NOT NULL,
    IdRol INT NOT NULL,
    Estado TINYINT DEFAULT 1,
    CONSTRAINT FK_DetalleRolPermiso_Rol FOREIGN KEY(IdRol) REFERENCES dbo.RolSistema(IdRol),
    CONSTRAINT FK_DetalleRolPermiso_Permiso FOREIGN KEY(IdPermiso) REFERENCES dbo.Permisos(IdPermisos)
);
GO

CREATE TABLE dbo.Bitacora (
    IdBitacora INT IDENTITY(1,1) PRIMARY KEY,
    IdUsuario INT NOT NULL,
    Estado TINYINT DEFAULT 1,
    CONSTRAINT FK_Bitacora_Usuario FOREIGN KEY(IdUsuario) REFERENCES dbo.UsuarioSistema(IdUsuario)
);
GO

CREATE TABLE dbo.PerfilAccesoLab (
    IdPerfilAccesoLab INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(60) NOT NULL,
    Estado TINYINT DEFAULT 1
);
GO

CREATE TABLE dbo.Tarjeta (
    IdTarjeta INT IDENTITY(1,1) PRIMARY KEY,
    TarjetaUID VARCHAR(100) UNIQUE NOT NULL,
    Estado TINYINT DEFAULT 1,
    FechaFabricacion DATE NULL
);
GO

CREATE TABLE dbo.Enrolar (
    IdEnrolar INT IDENTITY(1,1) PRIMARY KEY,
    IdPersona INT NOT NULL,
    TarjetaUID VARCHAR(100) NOT NULL,
    IdCodigoIngreso VARCHAR(50) NULL,
    IdPerfilAccesoLab INT NOT NULL,
    Estado TINYINT DEFAULT 1,
    FechaDeRegistro DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_Enrolar_Persona FOREIGN KEY(IdPersona) REFERENCES dbo.Persona(IdPersona),
    CONSTRAINT FK_Enrolar_Perfil FOREIGN KEY(IdPerfilAccesoLab) REFERENCES dbo.PerfilAccesoLab(IdPerfilAccesoLab),
    CONSTRAINT FK_Enrolar_Tarjeta FOREIGN KEY(TarjetaUID) REFERENCES dbo.Tarjeta(TarjetaUID)
);
GO

CREATE TABLE dbo.TipoMovimiento (
    IdTipoMovimiento INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Estado TINYINT DEFAULT 1
);
GO

CREATE TABLE dbo.TipoDispositivo (
    IdTipoDispositivo INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Estado TINYINT DEFAULT 1
);
GO

CREATE TABLE dbo.RegistroAcceso (
    IdRegistroAcceso INT IDENTITY(1,1) PRIMARY KEY,
    TarjetaUID VARCHAR(100) NOT NULL,
    IdCodigoIngreso VARCHAR(50) NULL,
    FechaHora DATETIME DEFAULT CURRENT_TIMESTAMP,
    IdTipoMovimiento INT NOT NULL,
    IdTipoDispositivo INT NOT NULL,
    Descripcion VARCHAR(MAX) NULL,
    Estado TINYINT DEFAULT 1,
    CONSTRAINT FK_RegistroAcceso_Tarjeta FOREIGN KEY(TarjetaUID) REFERENCES dbo.Tarjeta(TarjetaUID),
    CONSTRAINT FK_RegistroAcceso_TipoMovimiento FOREIGN KEY(IdTipoMovimiento) REFERENCES dbo.TipoMovimiento(IdTipoMovimiento),
    CONSTRAINT FK_RegistroAcceso_TipoDispositivo FOREIGN KEY(IdTipoDispositivo) REFERENCES dbo.TipoDispositivo(IdTipoDispositivo)
);
GO

-- Indexes
CREATE NONCLUSTERED INDEX IX_RegistroAcceso_FechaHora ON dbo.RegistroAcceso(FechaHora);
CREATE NONCLUSTERED INDEX IX_RegistroAcceso_TarjetaUID_FechaHora ON dbo.RegistroAcceso(TarjetaUID, FechaHora);
CREATE NONCLUSTERED INDEX IX_Enrolar_Persona ON dbo.Enrolar(IdPersona);
CREATE NONCLUSTERED INDEX IX_Enrolar_TarjetaUID ON dbo.Enrolar(TarjetaUID);
GO

-- Optional seed (commented)
/*
INSERT INTO dbo.TipoSangre (Nombre) VALUES ('A+'),('A-'),('B+'),('B-'),('AB+'),('AB-'),('O+'),('O-');
*/

PRINT 'Script finished.'
GO
