import requests

url = 'http://localhost:8000/api/v1/auth/me'
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwianRpIjoiYmQ1MTAyMjUtMjNkOC00OTA5LThkNDItMTVjZmU0NjZmNDc0IiwiZXhwIjoxNzc3NDEyNzI3fQ.uOwnVwR24r32wJLSFhD9B-AJbny0zRZLzMVbwqpo07Q'}

try:
    r = requests.get(url, headers=headers, timeout=5)
    print('Status:', r.status_code)
    print('JSON:', r.text)
except Exception as e:
    print('Request error:', e)
