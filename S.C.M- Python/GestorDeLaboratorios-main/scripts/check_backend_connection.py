import json
import urllib.request
import urllib.error

BASES = ["http://127.0.0.1:5000", "http://localhost:5000", "http://172.168.7.196:5000"]

def get(path, base):
    url = base + path
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            print(f"GET {url} -> {r.status}")
            print(r.read(500).decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f"GET {url} failed: {e}")


def post_login(base):
    url = base + '/api/login'
    data = json.dumps({"correo":"admin@uni.edu","password":"1234"}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"POST {url} -> {r.status}")
            print(r.read(500).decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f"POST {url} failed: {e}")

if __name__ == '__main__':
    for b in BASES:
        print('--- Testing base', b)
        get('/', b)
        get('/ping', b)
        post_login(b)
