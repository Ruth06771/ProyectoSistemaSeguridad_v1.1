import requests
urls = [
    ('Backend root','http://127.0.0.1:5000/'),
    ('/api/metrics','http://127.0.0.1:5000/api/metrics'),
    ('/api/tarjetas','http://127.0.0.1:5000/api/tarjetas'),
    ('/api/personas','http://127.0.0.1:5000/api/personas'),
    ('Frontend root','http://localhost:3000/')
]
for name,url in urls:
    try:
        r = requests.get(url, timeout=5)
        print('---',name,'status',r.status_code)
        content = r.text
        print(content[:1600])
    except Exception as e:
        print('---',name,'FAILED',e)
