import traceback
mods = [
 'modulos.administracion.personas.personas_api',
 'modulos.accesos.tarjetas_api',
 'modulos.reportes.reportes_api'
]
for m in mods:
    try:
        __import__(m)
        print(m, 'imported OK')
    except Exception as e:
        print(m, 'FAILED')
        traceback.print_exc()
