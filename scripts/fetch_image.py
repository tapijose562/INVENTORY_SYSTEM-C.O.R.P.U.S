import requests
url = 'http://127.0.0.1:8000/api/v1/detection/images/detect_selection_df88259641d74ca198f9d2b50c6ad862.jpg'
resp = requests.get(url)
print('status', resp.status_code)
if resp.status_code == 200:
    open('tmp_annotated.jpg','wb').write(resp.content)
    print('Saved tmp_annotated.jpg')
else:
    print(resp.text)
