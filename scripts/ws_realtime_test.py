import asyncio
import websockets
import base64
import json
from pathlib import Path

WS_URL = 'ws://127.0.0.1:8000/api/v1/detection/ws/real-time-detection'
IMAGE_PATH = Path('backend/assets/images/detect_selection_df88259641d74ca198f9d2b50c6ad862.jpg')
import sys
MODEL = sys.argv[1] if len(sys.argv) > 1 else 'corpus'

async def send_frame():
    if not IMAGE_PATH.exists():
        print('Image not found:', IMAGE_PATH)
        return
    data = IMAGE_PATH.read_bytes()
    b64 = base64.b64encode(data).decode('ascii')
    image_data = f'data:image/jpeg;base64,{b64}'

    async with websockets.connect(WS_URL) as ws:
        print('Connected to', WS_URL)
        # send a few frames
        for i in range(3):
            msg = {'type': 'frame', 'model': MODEL, 'image': image_data}
            await ws.send(json.dumps(msg))
            print('Sent frame', i+1)
            resp = await ws.recv()
            print('Response', i+1, ':', resp)
            await asyncio.sleep(0.5)
        # send ping
        await ws.send(json.dumps({'type': 'ping'}))
        resp = await ws.recv()
        print('Ping response:', resp)

if __name__ == '__main__':
    asyncio.run(send_frame())
