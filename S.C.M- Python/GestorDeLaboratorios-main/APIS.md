APIs del proyecto — GestorDeLaboratorios

Resumen de endpoints importantes (ruta -> método -> descripción)

Auth
- POST /api/login -> Login (JSON body: {correo, password})
- POST /api/logout -> Logout (borra sesión)
- GET  /api/session -> Obtiene la sesión activa (usuario y rol)

Personas (modulos/administracion/personas/personas_api.py)
- GET    /api/personas -> Listar todas las personas
- POST   /api/personas -> Crear persona (JSON body con campos)
- GET    /api/personas/<id> -> Obtener persona por id
- PUT    /api/personas/<id> -> Actualizar persona
- DELETE /api/personas/<id> -> Eliminar persona

Tarjetas (modulos/accesos/tarjetas_api.py)
- GET    /api/tarjetas -> Listar tarjetas
- POST   /api/tarjetas -> Crear tarjeta (JSON body: uid, nombre_completo, correo)
- GET    /api/tarjetas/<id> -> Obtener tarjeta
- PUT    /api/tarjetas/<id> -> Actualizar tarjeta
- DELETE /api/tarjetas/<id> -> Eliminar tarjeta

Reportes JSON (modulos/reportes/reportes_api.py)
- GET /api/reportes/accesos_historial -> Devuelve historial de accesos (filtros: fecha_desde, fecha_hasta, tipo_accion, usuario_responsable, tarjeta)
- GET /api/reportes/tarjetas_historial -> Devuelve historial de tarjetas (filtros: fecha_desde, fecha_hasta, accion, usuario, tarjeta)

Rutas server-rendered y exportes (varios en modulos/reportes)
- /reporte_tarjetas
- /exportar_excel_tarjetas
- /reporte_accesos_personal
- /reportes
- /tarjetas_historial (vista)
- /accesos_historial (vista)

Notas
- Las APIs JSON principales empiezan con /api/. Las rutas que generan páginas o archivos suelen ser rutas simples en la raíz y están en `modulos/reportes/`.
- Las rutas son registradas por `auth/login_api.py` cuando ejecutas `python auth\login_api.py`.
