import json
import urllib.request

url = 'http://127.0.0.1:5000/api/personas'

data = {
    'nombre_completo': 'Test Persona',
    'fecha_nacimiento': '1990-01-01',
    'correo': 'test@example.com',
    'telefono_personal': '12345678',
    'documento_identidad': 'ABC123',
    'sexo': 'M',
    'tipo_sangre': 'O+',
    'persona_emergencia': 'Contacto',
    'telefono_emergencia': '87654321'
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as resp:
        print('Status:', resp.status)
        print(resp.read().decode())
except Exception as e:
    import traceback
    traceback.print_exc()
