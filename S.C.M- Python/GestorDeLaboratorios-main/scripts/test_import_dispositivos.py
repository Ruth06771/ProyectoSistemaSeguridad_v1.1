import sys, traceback
ROOT = r'C:\Users\Server Tecnología\Pictures\Proyecto-en-Python-main\S.C.M- Python\GestorDeLaboratorios-main'
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
try:
    import modulos.administracion.dispositivos_api as m
    print('Import OK:', m)
except Exception:
    traceback.print_exc()
