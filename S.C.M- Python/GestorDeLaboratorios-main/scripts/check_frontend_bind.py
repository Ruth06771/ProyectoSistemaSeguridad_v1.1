import requests
for host in ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://192.168.0.112:3000']:
    try:
        r = requests.get(host, timeout=3)
        print(host, '->', r.status_code)
    except Exception as e:
        print(host, 'FAILED', e)
