import requests
try:
    r = requests.get('http://127.0.0.1:5000/', timeout=5)
    print('status', r.status_code)
    print(r.text[:1200])
except Exception as e:
    print('FAILED', e)
