# Cambios Realizados en el Módulo de Reportes

## Resumen
Se modificó el módulo de reportes para actualizar las columnas de la base de datos, backend y frontend según los nuevos requisitos.

## Cambios en la Base de Datos (config/db.py)

### Tabla: `registro_acceso`
Se añadieron nuevas columnas:
- **resultado**: Indica si el acceso fue "Permitido" o "Denegado"
- **credencial**: Especifica si el acceso fue con "Tarjeta" o "PIN"
- **enrolar_id**: Referencia a la tabla `enrolar` para vincular con la persona que ingresó

Estructura actualizada:
```sql
CREATE TABLE IF NOT EXISTS registro_acceso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrolar_id INTEGER,
    tarjeta_uid TEXT,
    codigo_ingreso TEXT,
    fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
    tipo_movimiento_id INTEGER,
    tipo_dispositivo_id INTEGER,
    resultado TEXT,
    credencial TEXT,
    descripcion TEXT,
    estado INTEGER DEFAULT 1,
    FOREIGN KEY(enrolar_id) REFERENCES enrolar(id),
    FOREIGN KEY(tipo_movimiento_id) REFERENCES tipo_movimiento(id),
    FOREIGN KEY(tipo_dispositivo_id) REFERENCES tipo_dispositivo(id)
)
```

## Cambios en el Backend

### Archivo: auth/esp_api.py
Se actualizó el endpoint `/api/esp/access` para registrar los accesos en la tabla `registro_acceso`:
- Ahora obtiene el `enrolar_id` cuando encuentra un usuario enrolado
- Inserta registros con `resultado` (Permitido/Denegado)
- Registra el tipo de `credencial` utilizado (Tarjeta/PIN)
- Almacena información de auditoría completa

### Archivo: modulos/reportes/reportes_api.py
Se actualizó el endpoint `/api/reportes/accesos_historial`:
- Realiza un JOIN entre `registro_acceso`, `enrolar` y `personas`
- Retorna el nombre completo de la persona enrolada que ingresó
- Incluye filtros para: fecha, tipo de movimiento, resultado y credencial
- Columnas retornadas:
  - id
  - fecha_hora
  - persona (nombre completo)
  - movimiento (Entrada/Salida)
  - resultado (Permitido/Denegado)
  - credencial (Tarjeta/PIN)

## Cambios en el Frontend

### Archivo: modulos/reportes/AccesosHistorial.jsx
Se actualizó el componente React:
- Nueva tabla con 6 columnas:
  - **ID**: Identificador del registro
  - **Fecha y Hora**: Timestamp del acceso
  - **Persona**: Nombre de la persona enrolada que ingresó
  - **Movimiento**: Badge verde para Entrada, badge azul para Salida
  - **Resultado**: Badge verde para Permitido, badge rojo para Denegado
  - **Credencial**: Badge azul para Tarjeta, badge amarillo para PIN

- Filtros disponibles:
  - Fecha Desde / Fecha Hasta
  - Tipo de Movimiento (Entrada/Salida)
  - Resultado (Permitido/Denegado)
  - Credencial (Tarjeta/PIN)

- Visual mejorado con badges de colores para mejor legibilidad

## Estructura de Datos

### Flujo de Datos:
1. ESP32 envía evento de acceso con `uid` de tarjeta
2. Backend verifica si la tarjeta está enrolada (tabla `enrolar`)
3. Si está enrolada, obtiene la información de la persona (tabla `personas`)
4. Registra el evento en `registro_acceso` con:
   - Referencia al `enrolar_id` (persona enrolada)
   - Timestamp del acceso
   - Tipo de movimiento (Entrada/Salida)
   - Resultado (Permitido si persona existe, Denegado si no)
   - Tipo de credencial utilizado

## Compatibilidad
- SQLite: ✅ Totalmente compatible
- MySQL: ✅ Compatible (con placeholders `%s`)
- La migración es automática para bases de datos existentes (ALTER TABLE)

## Testing
Para probar el módulo:
1. Acceder a `/reportes` en el frontend
2. Ir a "Historial de Accesos"
3. Los registros se mostrarán con las nuevas columnas
4. Probar filtros por fecha, movimiento, resultado y credencial
