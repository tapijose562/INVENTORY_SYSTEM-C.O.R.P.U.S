#!/usr/bin/env python
"""
YOLO Training Script
Retrains YOLO model with detection logs collected from the application
"""

import os
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image

class YOLOTrainer:
    """YOLO Model Trainer for continuous learning"""

    def __init__(self, base_model: str = "yolov8n.pt", dataset_root: str = "datasets"):
        base_path = Path(base_model)
        if not base_path.exists() and Path("..", "..", "models", base_model).exists():
            base_path = Path("..", "..", "models", base_model)
        elif not base_path.exists() and Path("..", "models", base_model).exists():
            base_path = Path("..", "models", base_model)

        self.base_model = str(base_path)
        self.dataset_root = Path(dataset_root)
        self.dataset_root.mkdir(exist_ok=True)
        self.model = None
    
    def prepare_dataset(self, detection_logs: list) -> str:
        """Prepare YOLO dataset from detection logs
        
        Args:
            detection_logs: List of detection log records
            
        Returns:
            Path to dataset directory
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dataset_path = self.dataset_root / f"dataset_{timestamp}"
        
        # Create directory structure
        images_train = dataset_path / "images" / "train"
        images_val = dataset_path / "images" / "val"
        labels_train = dataset_path / "labels" / "train"
        labels_val = dataset_path / "labels" / "val"
        
        images_train.mkdir(parents=True, exist_ok=True)
        images_val.mkdir(parents=True, exist_ok=True)
        labels_train.mkdir(parents=True, exist_ok=True)
        labels_val.mkdir(parents=True, exist_ok=True)
        
        # Class mapping
        classes = {
            "Nike": 0,
            "Adidas": 1,
            "Puma": 2,
            "Other_Shoe": 3
        }
        
        # Split dataset (80% train, 20% val)
        split_idx = int(len(detection_logs) * 0.8)
        train_logs = detection_logs[:split_idx]
        val_logs = detection_logs[split_idx:]
        
        # Process training images
        for idx, log in enumerate(train_logs):
            self._process_detection_log(
                log, idx, labels_train, images_train, classes, "train"
            )
        
        # Process validation images
        for idx, log in enumerate(val_logs):
            self._process_detection_log(
                log, idx, labels_val, images_val, classes, "val"
            )
        
        # Create data.yaml
        data_yaml = {
            "path": str(dataset_path.absolute()),
            "train": "images/train",
            "val": "images/val",
            "nc": len(classes),
            "names": list(classes.keys())
        }
        
        with open(dataset_path / "data.yaml", "w") as f:
            yaml.dump(data_yaml, f)
        
        print(f"Dataset created at: {dataset_path}")
        return str(dataset_path)
    
    def _process_detection_log(self, log, idx, labels_path, images_path, classes, split):
        """Process a single detection log"""
        
        try:
            # Load image
            image_path = log.get("image_path")
            if not os.path.exists(image_path):
                return
            
            image = cv2.imread(image_path)
            if image is None:
                return
            
            # Get detection data
            brand = log.get("detected_brand", "Other_Shoe")
            bbox = log.get("detection_metadata", {}).get("bbox", [])
            
            if not bbox or brand not in classes:
                return
            
            # Normalize coordinates to YOLO format (center x, center y, width, height)
            height, width = image.shape[:2]
            x1, y1, x2, y2 = bbox
            
            center_x = ((x1 + x2) / 2) / width
            center_y = ((y1 + y2) / 2) / height
            box_width = (x2 - x1) / width
            box_height = (y2 - y1) / height
            
            # Save image
            img_name = f"{split}_{idx:06d}.jpg"
            img_save_path = images_path / img_name
            cv2.imwrite(str(img_save_path), image)
            
            # Save label
            label_name = f"{split}_{idx:06d}.txt"
            label_path = labels_path / label_name
            class_id = classes[brand]
            
            with open(label_path, "w") as f:
                f.write(f"{class_id} {center_x} {center_y} {box_width} {box_height}\n")
            
        except Exception as e:
            print(f"Error processing log {idx}: {e}")
    
    def train(self, dataset_path: str, epochs: int = 10, batch_size: int = 16, device: str = "cpu") -> dict:
        """Train YOLO model
        
        Args:
            dataset_path: Path to dataset directory
            epochs: Number of training epochs
            batch_size: Batch size for training
            device: Device for training ('cpu' or '0' for GPU)
            
        Returns:
            Training results
        """
        
        try:
            # Load model
            self.model = YOLO(self.base_model)
            
            # Train
            results = self.model.train(
                data=os.path.join(dataset_path, "data.yaml"),
                epochs=epochs,
                imgsz=640,
                batch=batch_size,
                device=device,
                patience=10,
                save=True,
                verbose=True
            )
            
            # Save trained model
            model_save_path = Path("models") / f"yolov8_trained_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
            model_save_path.parent.mkdir(exist_ok=True)
            
            best_model = Path(self.model.trainer.best.parent) / "best.pt"
            shutil.copy(best_model, model_save_path)
            
            print(f"Model saved to: {model_save_path}")
            
            return {
                "success": True,
                "model_path": str(model_save_path),
                "results": {
                    "accuracy": float(results.box.map) if hasattr(results, 'box') else 0.0,
                    "loss": float(results.loss.cls) if hasattr(results, 'loss') else 0.0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

if __name__ == "__main__":
    # Example usage
    trainer = YOLOTrainer()
    
    # In real scenario, these would come from database
    sample_logs = [
        {
            "image_path": "sample_image.jpg",
            "detected_brand": "Nike",
            "detection_metadata": {
                "bbox": [100, 100, 300, 400]
            }
        }
    ]
    
    dataset_path = trainer.prepare_dataset(sample_logs)
    results = trainer.train(dataset_path, epochs=10, batch_size=16)
    print(results)
