import requests

url = 'http://localhost:8000/openapi.json'
try:
    r = requests.get(url, timeout=5)
    print('Status:', r.status_code)
    print(r.text[:2000])
except Exception as e:
    print('Error:', e)
