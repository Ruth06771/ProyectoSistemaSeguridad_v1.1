from auth import login_api
app = login_api.app

for rule in app.url_map.iter_rules():
    print(rule)
