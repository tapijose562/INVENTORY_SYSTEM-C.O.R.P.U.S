from pathlib import Path
import argparse
import sys

try:
    import torch
except Exception:
    torch = None

from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="Train YOLOv8 on CPU.")
    parser.add_argument("--data", default=r".\Corpus-1\data.yaml", help="Path to data.yaml")
    parser.add_argument("--model", default="yolov8n.pt", help="Base model for training")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Training image size")
    parser.add_argument("--device", default="auto", help="Device to use: 'auto', 'cpu' or 'cuda'")
    parser.add_argument("--batch", type=int, default=16, help="Batch size for training")
    parser.add_argument("--workers", type=int, default=2, help="Number of data loader workers")
    return parser.parse_args()


def main():
    args = parse_args()
    data_path = Path(args.data)

    # If the provided data path doesn't exist, try to auto-discover a data.yaml in subfolders
    if not data_path.exists():
        candidates = list(Path('.').rglob('data.yaml'))
        if candidates:
            data_path = candidates[0]
            print(f"Usando data.yaml encontrado en: {data_path}")
        else:
            raise FileNotFoundError(
                f"Dataset config not found: {data_path}. Run download_roboflow.py first or pass --data."
            )

    # Determine device
    device = args.device
    if device == "auto":
        if torch is not None and torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

    print(f"Entrenamiento: modelo={args.model}, device={device}, epochs={args.epochs}, imgsz={args.imgsz}, batch={args.batch}, workers={args.workers}")

    model = YOLO(args.model)
    model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        device=device,
        batch=args.batch,
        workers=args.workers,
    )


if __name__ == "__main__":
    main()
