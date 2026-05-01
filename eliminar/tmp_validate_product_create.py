import requests
import json

url = 'http://localhost:8000/api/v1/products'
payload = {
    'name': 'Test Complete Product',
    'brand': 'Nike',
    'colors': 'Core Black / Cloud White / Grey',
    'color_rgb': {'r': 0, 'g': 0, 'b': 0},
    'size': '42',
    'stock': 1,
    'price': 10000,
    'yolo_confidence': 0.85,
    'detected_text': 'Test',
    'description': 'Test complete product',
    'detection_metadata': {'batch_images': 1}
}

try:
    r = requests.post(url, json=payload, timeout=5)
    print(r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('Error', e)
