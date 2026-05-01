from app.core.security import jwt
from app.core.config import settings
from app.db.database import SessionLocal
from app.models.user import User

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwianRpIjoiYmQ1MTAyMjUtMjNkOC00OTA5LThkNDItMTVjZmU0NjZmNDc0IiwiZXhwIjoxNzc3NDEyNzI3fQ.uOwnVwR24r32wJLSFhD9B-AJbny0zRZLzMVbwqpo07Q'

print('Decoding token...')
try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print('Payload:', payload)
except Exception as e:
    print('Decode error:', repr(e))

print('Querying DB for user id:', payload.get('sub'))
db = SessionLocal()
try:
    user = db.query(User).filter(User.id == int(payload.get('sub'))).first()
    print('User:', user)
    if user:
        print('User fields:', {k: v for k, v in user.__dict__.items() if not k.startswith('_')})
finally:
    db.close()
