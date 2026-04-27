-- cleanup_duplicates.sql
SET NOCOUNT ON;
USE ReportesSistemaSeguridad;
GO

PRINT '--- TipoSangre duplicates ---';
-- Update references from duplicate TipoSangre to the kept Id
;WITH d AS (
  SELECT IdSangre, Nombre, ROW_NUMBER() OVER (PARTITION BY Nombre ORDER BY IdSangre) rn
  FROM dbo.TipoSangre
), keepers AS (
  SELECT IdSangre AS keepId, Nombre FROM d WHERE rn = 1
), removals AS (
  SELECT IdSangre AS remId, Nombre FROM d WHERE rn > 1
)
-- update Persona references
UPDATE p
SET IdTipoSangre = k.keepId
FROM dbo.Persona p
JOIN removals r ON p.IdTipoSangre = r.remId
JOIN keepers k ON k.Nombre = r.Nombre;

-- delete duplicates
DELETE s
FROM dbo.TipoSangre s
JOIN removals r ON s.IdSangre = r.remId;

SELECT 'TipoSangre remaining' AS what, COUNT(*) AS cnt FROM dbo.TipoSangre;
GO

PRINT '--- PersonaEmergencia duplicates ---';
;WITH d AS (
  SELECT IdPersonaEmergencia, Nombres, Apellidos, TelefonoPersonal,
         ROW_NUMBER() OVER (PARTITION BY Nombres, Apellidos, TelefonoPersonal ORDER BY IdPersonaEmergencia) rn
  FROM dbo.PersonaEmergencia
), keepers AS (
  SELECT IdPersonaEmergencia AS keepId, Nombres, Apellidos, TelefonoPersonal FROM d WHERE rn = 1
), removals AS (
  SELECT IdPersonaEmergencia AS remId, Nombres, Apellidos, TelefonoPersonal FROM d WHERE rn > 1
)
-- update Persona references
UPDATE p
SET IdPersonaEmergencia = k.keepId
FROM dbo.Persona p
JOIN removals r ON p.IdPersonaEmergencia = r.remId
JOIN keepers k ON k.Nombres = r.Nombres AND k.Apellidos = r.Apellidos AND ISNULL(k.TelefonoPersonal,'') = ISNULL(r.TelefonoPersonal,'');
-- delete duplicates
DELETE e
FROM dbo.PersonaEmergencia e
JOIN removals r ON e.IdPersonaEmergencia = r.remId;
SELECT 'PersonaEmergencia remaining' AS what, COUNT(*) AS cnt FROM dbo.PersonaEmergencia;
GO

PRINT '--- Persona duplicates (by CI) ---';
;WITH d AS (
  SELECT IdPersona, CI, ROW_NUMBER() OVER (PARTITION BY CI ORDER BY IdPersona) rn
  FROM dbo.Persona
), keepers AS (
  SELECT IdPersona AS keepId, CI FROM d WHERE rn = 1
), removals AS (
  SELECT IdPersona AS remId, CI FROM d WHERE rn > 1
)
-- Update Enrolar references
UPDATE e
SET IdPersona = k.keepId
FROM dbo.Enrolar e
JOIN removals r ON e.IdPersona = r.remId
JOIN keepers k ON k.CI = r.CI;
-- Update UsuarioSistema references
UPDATE u
SET IdPersona = k.keepId
FROM dbo.UsuarioSistema u
JOIN removals r ON u.IdPersona = r.remId
JOIN keepers k ON k.CI = r.CI;
-- delete duplicates
DELETE p
FROM dbo.Persona p
JOIN removals r ON p.IdPersona = r.remId;
SELECT 'Persona remaining' AS what, COUNT(*) AS cnt FROM dbo.Persona;
GO

PRINT '--- Enrolar duplicates (IdPersona, TarjetaUID, IdPerfilAccesoLab) ---';
;WITH d AS (
  SELECT IdEnrolar, IdPersona, TarjetaUID, IdPerfilAccesoLab,
         ROW_NUMBER() OVER (PARTITION BY IdPersona, TarjetaUID, IdPerfilAccesoLab ORDER BY IdEnrolar) rn
  FROM dbo.Enrolar
), keepers AS (
  SELECT IdEnrolar AS keepId, IdPersona, TarjetaUID, IdPerfilAccesoLab FROM d WHERE rn = 1
), removals AS (
  SELECT IdEnrolar AS remId, IdPersona, TarjetaUID, IdPerfilAccesoLab FROM d WHERE rn > 1
)
-- No FK to update for Enrolar in this schema; delete duplicates
DELETE e
FROM dbo.Enrolar e
JOIN removals r ON e.IdEnrolar = r.remId;
SELECT 'Enrolar remaining' AS what, COUNT(*) AS cnt FROM dbo.Enrolar;
GO

PRINT '--- RegistroAcceso exact duplicate removals ---';
;WITH d AS (
  SELECT IdRegistroAcceso, TarjetaUID, IdTipoMovimiento, IdTipoDispositivo, FechaHora, Descripcion,
         ROW_NUMBER() OVER (PARTITION BY TarjetaUID, IdTipoMovimiento, IdTipoDispositivo, FechaHora, ISNULL(Descripcion,'') ORDER BY IdRegistroAcceso) rn
  FROM dbo.RegistroAcceso
), removals AS (
  SELECT IdRegistroAcceso AS remId FROM d WHERE rn > 1
)
DELETE r
FROM dbo.RegistroAcceso r
JOIN removals rem ON r.IdRegistroAcceso = rem.remId;
SELECT 'RegistroAcceso remaining' AS what, COUNT(*) AS cnt FROM dbo.RegistroAcceso;
GO

PRINT '--- Done cleanup ---';
GO
