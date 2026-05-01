import argparse
import logging
import threading
import time
import queue
from pathlib import Path
from typing import Optional

import cv2
import requests
from ultralytics import YOLO


LOG = logging.getLogger("test_camera")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def parse_args():
    p = argparse.ArgumentParser(description="Threaded YOLOv8 camera inference (local or API)")
    p.add_argument("--model", default="best.pt", help="Path to the trained YOLO model")
    p.add_argument("--camera", type=int, default=0, help="Camera index")
    p.add_argument("--imgsz", type=int, default=640, help="Inference image size")
    p.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    p.add_argument("--device", default="cpu", help="Device for inference: cpu or 0,1 for cuda device")
    p.add_argument("--api", action="store_true", help="Send frames to backend API instead of local model")
    p.add_argument("--server", default="http://localhost:8000", help="Backend server URL")
    p.add_argument("--use-corpus", action="store_true", help="Use corpus realtime endpoint on backend")
    p.add_argument("--yes", action="store_true", help="Auto-confirm camera usage")
    p.add_argument("--no-ui", action="store_true", help="Run without opening GUI windows (save annotated files)")
    p.add_argument("--max-queue", type=int, default=4, help="Max queue size between reader and worker")
    return p.parse_args()


class FrameReader(threading.Thread):
    def __init__(self, camera_index=0, queue_out: queue.Queue = None):
        super().__init__(daemon=True)
        self.camera_index = camera_index
        self.queue_out = queue_out or queue.Queue(maxsize=4)
        self._stop_event = threading.Event()

    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            LOG.error("Could not open camera %s", self.camera_index)
            return
        LOG.info("Camera opened: %s", self.camera_index)
        try:
            while not self._stop_event.is_set():
                ok, frame = cap.read()
                if not ok:
                    LOG.warning("Empty frame from camera")
                    time.sleep(0.01)
                    continue
                # push frame, drop oldest if queue full
                try:
                    self.queue_out.put(frame, block=False)
                except queue.Full:
                    try:
                        _ = self.queue_out.get_nowait()
                        self.queue_out.put(frame, block=False)
                    except Exception:
                        pass
        finally:
            cap.release()
            LOG.info("Camera released")

    def stop(self):
        self._stop_event.set()


class InferenceWorker(threading.Thread):
    def __init__(self, q_in: queue.Queue, args):
        super().__init__(daemon=True)
        self.q = q_in
        self.args = args
        self._stop_event = threading.Event()
        self.model: Optional[YOLO] = None

    def setup_model(self):
        model_path = Path(self.args.model)
        if not model_path.exists() and not self.args.api:
            LOG.error("Model not found: %s; worker will stop", model_path)
            # stop worker gracefully if no model available
            self._stop_event.set()
            return

        if not self.args.api:
            LOG.info("Loading model %s on device=%s", model_path, self.args.device)
            # model initialization
            self.model = YOLO(str(model_path))

    def perform_ocr(self, image):
        # Optional OCR hook: prefer EasyOCR if installed, else return empty list
        try:
            import easyocr  # type: ignore[reportMissingImports]

            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(image)
            return results
        except Exception:
            return []

    def post_to_api(self, frame):
        ret, buf = cv2.imencode('.jpg', frame)
        if not ret:
            return None
        files = {'file': ('frame.jpg', buf.tobytes(), 'image/jpeg')}
        if self.args.use_corpus:
            url = f"{self.args.server}/api/v1/detection/detect-corpus-realtime"
        else:
            url = f"{self.args.server}/api/v1/detection/detect-corpus-realtime"
        r = requests.post(url, files=files, timeout=10)
        r.raise_for_status()
        return r.json()

    def draw_results(self, frame, data):
        # draw boxes from local ultralytics results or API JSON
        if data is None:
            return frame
        if isinstance(data, dict) and 'detections' in data:
            for det in data['detections']:
                x1, y1, x2, y2 = map(int, det['bbox'])
                cls = det.get('class', 'obj')
                conf = det.get('confidence', 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{cls} {conf:.2f}", (x1, max(10, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            return frame

        # ultralytics results: results object from model.predict
        try:
            boxes = data[0].boxes
            annotated = data[0].plot()
            return annotated
        except Exception:
            return frame

    def run(self):
        self.setup_model()
        last_time = time.time()
        frame_count = 0
        fps = 0.0
        saved_failures = 0

        while not self._stop_event.is_set():
            try:
                frame = self.q.get(timeout=1)
            except queue.Empty:
                continue

            t0 = time.time()
            data = None
            try:
                if self.args.api:
                    data = self.post_to_api(frame)
                    det_count = len(data.get('detections', [])) if data else 0
                else:
                    # convert to RGB for model if needed
                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.model.predict(source=img_rgb, device=self.args.device, imgsz=self.args.imgsz, conf=self.args.conf, verbose=False)
                    data = results
                    det_count = len(results[0].boxes) if results and results[0].boxes is not None else 0

                # draw/annotate
                out = self.draw_results(frame.copy(), data)

                # optional OCR on detections
                ocr_results = []
                # if det_count > 0: (could crop and OCR specific boxes)
                # ocr_results = self.perform_ocr(out)

                # display or save
                frame_count += 1
                now = time.time()
                fps = 0.9 * fps + 0.1 * (1.0 / (now - last_time)) if now != last_time else fps
                last_time = now

                LOG.info("Frame %d: detections=%d, fps=%.2f", frame_count, det_count, fps)

                if not self.args.no_ui:
                    try:
                        cv2.imshow('Realtime', out)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    except Exception:
                        LOG.exception('Error showing window; saving frame')
                        out_path = Path(f"annotated_camera_{saved_failures}.jpg")
                        cv2.imwrite(str(out_path), out)
                        saved_failures += 1
                        if saved_failures >= 5:
                            LOG.error('Saved %s failure frames, stopping', saved_failures)
                            break
            except Exception as e:
                LOG.exception('Inference error: %s', e)
                saved_failures += 1
                out_path = Path(f"inference_error_{saved_failures}.jpg")
                try:
                    cv2.imwrite(str(out_path), frame)
                except Exception:
                    pass
                if saved_failures >= 5:
                    LOG.error('Too many failures; exiting')
                    break

        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

    def stop(self):
        self._stop_event.set()


def main():
    args = parse_args()

    if not args.yes:
        try:
            resp = input('Este script abrirá la cámara. ¿Continuar? (y/N): ')
        except Exception:
            resp = 'y'
        if resp.strip().lower() != 'y':
            LOG.info('Cancelado por el usuario')
            return

    q = queue.Queue(maxsize=args.max_queue)
    reader = FrameReader(camera_index=args.camera, queue_out=q)
    worker = InferenceWorker(q, args)

    try:
        reader.start()
        worker.start()
        LOG.info('Reader and worker started. Press q in window to quit.')
        while reader.is_alive() and worker.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        LOG.info('Keyboard interrupt, stopping')
    finally:
        reader.stop()
        worker.stop()
        reader.join(timeout=2)
        worker.join(timeout=2)


if __name__ == '__main__':
    main()
