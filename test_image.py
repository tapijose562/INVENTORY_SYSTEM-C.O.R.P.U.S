from pathlib import Path
import argparse
import requests
import cv2
import torch

# Allowlist ultralytics DetectionModel for torch safe unpickling when loading checkpoints
try:
    import ultralytics.nn.tasks as _u_tasks
    try:
        _safe = []
        try:
            _safe.append(_u_tasks.DetectionModel)
        except Exception:
            pass
        try:
            import torch.nn as _nn
            _safe.append(_nn.modules.container.Sequential)
            _safe.append(_nn.modules.module.Module)
        except Exception:
            pass
        if _safe:
            try:
                torch.serialization.add_safe_globals(_safe)
            except Exception:
                pass
    except Exception:
        pass
except Exception:
    pass


# If torch's safe unpickling blocks loading custom classes, temporarily allow full load by
# forcing `weights_only=False` for torch.load calls (only if you trust the checkpoint).
try:
    _orig_torch_load = torch.load
    def _torch_load_wrapper(*args, **kwargs):
        kwargs.setdefault("weights_only", False)
        return _orig_torch_load(*args, **kwargs)
    torch.load = _torch_load_wrapper
except Exception:
    pass

from ultralytics import YOLO
def parse_args():
    parser = argparse.ArgumentParser(description="Run YOLOv8 inference on one image using CPU.")
    parser.add_argument("--model", default="best.pt", help="Path to the trained YOLO model.")
    parser.add_argument("--image", default="test.jpg", help="Path to the input image.")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size.")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    parser.add_argument("--api", action="store_true", help="Use backend API instead of local model.")
    parser.add_argument("--server", default="http://localhost:8000", help="Backend server URL")
    parser.add_argument("--use-corpus", action="store_true", help="Ask backend to use corpus trained model")
    return parser.parse_args()


def main():
    args = parse_args()

    model_path = Path(args.model)
    image_path = Path(args.image)

    if args.api:
        # Send to backend API
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}.")
        url = f"{args.server}/api/v1/detection/detect-from-image"
        files = {"file": open(str(image_path), "rb")}
        data = {}
        if args.use_corpus:
            data["use_corpus"] = "true"
        resp = requests.post(url, files=files, data=data, timeout=30)
        try:
            resp.raise_for_status()
            print("API response:")
            print(resp.json())
        except Exception as e:
            print(f"API request failed: {e}\nResponse: {resp.text}")
        return

    # Local model inference (original behavior)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}. Train first or copy runs\\detect\\train\\weights\\best.pt here."
        )
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}. Place your test image here or pass --image.")

    model = YOLO(str(model_path))
    results = model.predict(
        source=str(image_path),
        device="cpu",
        imgsz=args.imgsz,
        conf=args.conf,
        verbose=False,
    )

    annotated = results[0].plot()
    window_name = "YOLOv8 Image Inference (CPU)"
    try:
        cv2.imshow(window_name, annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception:
        out_path = Path("annotated_output.jpg")
        cv2.imwrite(str(out_path), annotated)
        print(f"GUI no disponible: imagen anotada guardada en {out_path}")


if __name__ == "__main__":
    main()
