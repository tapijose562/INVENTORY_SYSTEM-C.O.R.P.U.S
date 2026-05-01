import requests
import json

BASE = 'http://localhost:8000/api/v1/auth'

user = {
    'username': 'cliente1',
    'email': 'cliente1@example.com',
    'full_name': 'Cliente One',
    'password': 'Cliente123'
}

print('Registering user...', user['username'])
try:
    r = requests.post(f'{BASE}/register', json=user, timeout=10)
    print('Register status:', r.status_code)
    try:
        print('Register response:', r.json())
    except Exception:
        print('Register raw:', r.text)
except Exception as e:
    print('Register request failed:', e)

print('\nAttempting login...')
try:
    r = requests.post(f'{BASE}/login', json={'username': user['username'], 'password': user['password']}, timeout=10)
    print('Login status:', r.status_code)
    data = None
    try:
        data = r.json()
        print('Login response:', data)
    except Exception:
        print('Login raw:', r.text)

    token = None
    if data and 'access_token' in data:
        token = data['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print('\nCalling /me with token...')
        r2 = requests.get(f'{BASE}/me', headers=headers, timeout=10)
        print('/me status:', r2.status_code)
        try:
            print('/me response:', r2.json())
        except Exception:
            print('/me raw:', r2.text)
    else:
        print('No token received; cannot call /me')
except Exception as e:
    print('Login request failed:', e)
