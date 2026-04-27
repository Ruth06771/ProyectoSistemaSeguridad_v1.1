import py_compile, sys, pathlib
root=pathlib.Path(r'c:\Users\Server Tecnología\Pictures\Proyecto-en-Python-main\S.C.M- Python\GestorDeLaboratorios-main')
errors=[]
for p in root.rglob('*.py'):
    try:
        py_compile.compile(str(p), doraise=True)
    except Exception as e:
        errors.append((str(p), str(e)))
print('checked', len(list(root.rglob('*.py'))), 'py files')
if errors:
    print('errors:')
    for f,e in errors:
        print(f, '->', e)
    sys.exit(1)
print('no python syntax errors found')
