import requests
import time
base='http://127.0.0.1:5000'

def wait_ready(timeout=20):
    for i in range(timeout):
        try:
            r = requests.get(base + '/api/tarjetas', timeout=2)
            if r.status_code == 200:
                print('server ready')
                return True
        except Exception:
            print('waiting for server...', i+1)
            time.sleep(1)
    return False

if not wait_ready(20):
    print('Server not ready after retries; aborting')
    exit(2)

try:
    # create persona
    persona = {'nombre':'Bit Retry','apellido':'Tester','correo':'retry@test.local','rol':'docente'}
    r_persona = requests.post(base + '/api/personas', json=persona, timeout=5)
    print('persona POST', r_persona.status_code, r_persona.text)

    # create tarjeta
    tarjeta = {'uid':'BIT_RETRY_UID','nombre_completo':'Bit Retry','correo':'retry@test.local'}
    r_tarjeta = requests.post(base + '/api/tarjetas', json=tarjeta, timeout=5)
    print('tarjeta POST', r_tarjeta.status_code, r_tarjeta.text)

    r_bit = requests.get(base + '/api/bitacora', timeout=5)
    print('bitacora status', r_bit.status_code)
    try:
        data = r_bit.json()
        for row in data[:10]:
            print(row)
    except Exception as e:
        print('Failed to parse bitacora JSON', e)

except Exception as e:
    print('FAILED', e)
