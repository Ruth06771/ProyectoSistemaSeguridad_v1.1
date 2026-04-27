import sys
ROOT = r'C:\Users\Server Tecnología\Pictures\Proyecto-en-Python-main\S.C.M- Python\GestorDeLaboratorios-main'
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    import auth.login_api as login_api
    app = login_api.app
    rules = sorted([(r.rule, r.endpoint, ','.join(sorted(r.methods))) for r in app.url_map.iter_rules()])
    for rule in rules:
        print(rule)
except Exception as e:
    import traceback
    traceback.print_exc()
