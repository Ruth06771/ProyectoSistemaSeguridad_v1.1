from flask import Flask
import sys
sys.path.insert(0, '.')
from modulos.reportes.reportes_api import reportes_api

app = Flask(__name__)
app.register_blueprint(reportes_api)

with app.test_client() as client:
    resp = client.get('/api/reportes/enrolamiento_historial')
    print('status', resp.status_code)
    print(resp.get_data(as_text=True))
