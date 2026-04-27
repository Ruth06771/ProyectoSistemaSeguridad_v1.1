import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location('login_api', str(ROOT / 'auth' / 'login_api.py'))
mod = importlib.util.module_from_spec(spec)
import types

spec.loader.exec_module(mod)
app = getattr(mod, 'app', None)
if not app:
  print('No se pudo obtener `app` desde auth/login_api.py')
  sys.exit(1)

rules = sorted(app.url_map.iter_rules(), key=lambda r: (str(r.rule), ','.join(sorted(r.methods))))
for r in rules:
  print(f"{r.rule}    methods={','.join(sorted(r.methods))}    endpoint={r.endpoint}")
