import urllib.request

url='http://127.0.0.1:5000/api/personas'
try:
    resp=urllib.request.urlopen(url)
    print('STATUS', resp.status)
    print(resp.read()[:500])
except Exception as e:
    print('ERROR', e)
