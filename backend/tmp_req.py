import requests
url='http://127.0.0.1:8001/api/v1/auth/me'
headers={'Authorization':'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwianRpIjoiYmQ1MTAyMjUtMjNkOC00OTA5LThkNDItMTVjZmU0NjZmNDc0IiwiZXhwIjoxNzc3NDEyNzI3fQ.uOwnVwR24r32wJLSFhD9B-AJbny0zRZLzMVbwqpo07Q'}
try:
    r=requests.get(url, headers=headers, timeout=5)
    print('status', r.status_code)
    print(r.text)
except Exception as e:
    print('err', e)
