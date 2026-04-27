import requests, re
base='http://127.0.0.1:5000'
try:
    r = requests.get(base+'/', timeout=5)
    html = r.text
    print('root status', r.status_code)
    m = re.search(r'src="(/assets/[^"]+)"', html)
    if m:
        jsurl = base + m.group(1)
        print('Found js:', jsurl)
        r2 = requests.get(jsurl, timeout=5)
        print('js status', r2.status_code, 'len', len(r2.content))
    else:
        print('No assets js found in index html')
except Exception as e:
    print('FAILED', e)
