import requests
BASE='http://localhost:8000/api/v1/auth'
print('Attempt admin login...')
try:
    r = requests.post(f'{BASE}/login', json={'username':'admin','password':'admin123'}, timeout=10)
    print('status', r.status_code)
    try:
        print('resp', r.json())
    except:
        print('raw', r.text)
except Exception as e:
    print('error', e)
