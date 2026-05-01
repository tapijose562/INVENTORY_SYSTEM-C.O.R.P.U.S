import requests
from pathlib import Path
img = Path('runs/detect/train/val_batch2_pred.jpg')
if not img.exists():
    print('Image not found:', img)
    raise SystemExit(1)
url = 'http://127.0.0.1:8000/api/v1/detection/detect-corpus'
with img.open('rb') as f:
    resp = requests.post(url, files={'file': f}, data={'use_corpus': 'true'})
    print('status', resp.status_code)
    try:
        j = resp.json()
        print(j)
        ann = j.get('annotated_image_url') or j.get('annotated_image') or j.get('metadata', {}).get('annotated_image_url')
        if ann:
            full = ann if ann.startswith('http') else ('http://127.0.0.1:8000' + ann)
            r = requests.get(full)
            if r.status_code == 200:
                open('tmp_frontend_annotated.jpg','wb').write(r.content)
                print('Saved tmp_frontend_annotated.jpg')
            else:
                print('Failed to fetch annotated image:', r.status_code)
    except Exception:
        print(resp.text)
