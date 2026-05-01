import requests

# Login to get token
login_data = {"username": "admin", "password": "admin123"}
print("Haciendo login...")
login_response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
print(f"Login status: {login_response.status_code}")
token = login_response.json()["access_token"]

print(f"Token obtenido: {token[:20]}...")

# Test detection
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("test_street.jpg", "rb")}

print("Enviando imagen para detección...")
response = requests.post(
    "http://localhost:8000/api/v1/detection/detect-from-image",
    headers=headers,
    files=files
)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print("Detección exitosa!")
    print(f"Marca: {result['brand']}")
    print(f"Color: {result['color']}")
    print(f"Confianza: {result['confidence']}")
    print(f"Bounding box: {result['metadata']['bbox']}")
else:
    print(f"Error: {response.text}")