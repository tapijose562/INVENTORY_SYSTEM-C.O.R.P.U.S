import requests
import json

try:
    r = requests.post(
        'http://localhost:8000/api/v1/products',
        json={
            'name': 'Nike Gato',
            'brand': 'Nike',
            'colors': 'Cloud White / Green / Black',
            'color_rgb': {'r': 89, 'g': 121, 'b': 46},
            'size': '40',
            'stock': 5,
            'price': 10000,
            'yolo_confidence': 0.75,
            'detected_text': 'Nike shoe',
            'description': 'Test nike shoe',
            'detection_metadata': {}
        },
        timeout=5
    )
    print(f'✅ Status: {r.status_code}')
    print('Response:')
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f'ERROR: {str(e)}')
