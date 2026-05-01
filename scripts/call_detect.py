import requests
from pathlib import Path
img = Path('runs/detect/train/val_batch2_pred.jpg')
if not img.exists():
    print('Image not found:', img)
    raise SystemExit(1)
with img.open('rb') as f:
    resp = requests.post('http://127.0.0.1:8000/api/v1/detection/detect-from-selection', files={'file': f}, data={'detection_id': '0'})
    print(resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
