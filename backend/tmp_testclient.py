from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwianRpIjoiYmQ1MTAyMjUtMjNkOC00OTA5LThkNDItMTVjZmU0NjZmNDc0IiwiZXhwIjoxNzc3NDEyNzI3fQ.uOwnVwR24r32wJLSFhD9B-AJbny0zRZLzMVbwqpo07Q'}

resp = client.get('/api/v1/auth/me', headers=headers)
print('status', resp.status_code)
print(resp.text)

