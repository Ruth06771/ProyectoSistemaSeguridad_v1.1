from auth.login_api import app

for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods))
    print(f"{rule.rule} -> {methods}")
