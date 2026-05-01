## ML Pipeline Guide

### Overview

The ML Pipeline handles YOLO model training and continuous learning from detection logs.

### Components

#### 1. YOLO Trainer (`training/train.py`)

Trains YOLO v8 model with detection logs:

```python
from ml_pipeline.training.train import YOLOTrainer

trainer = YOLOTrainer()
dataset_path = trainer.prepare_dataset(detection_logs)
results = trainer.train(dataset_path, epochs=10, batch_size=16)
```

**Features:**
- Converts detection logs to YOLO format
- Automatic train/val split (80/20)
- Creates standardized dataset structure
- Saves trained models versioned by timestamp

#### 2. Color Analyzer (`training/color_analyzer.py`)

Extracts dominant colors from shoe images:

```python
from ml_pipeline.training.color_analyzer import ShoeColorAnalyzer

analyzer = ShoeColorAnalyzer()
colors = analyzer.extract_dominant_colors(image, k=3)
info = analyzer.analyze_shoe_image("path/to/image.jpg", bbox=(x1, y1, x2, y2))
```

**Features:**
- K-means clustering for color extraction
- RGB/BGR color values
- Color naming (black, white, red, etc.)
- Percentage distribution

#### 3. OCR Extractor (`training/ocr_extractor.py`)

Extracts text from shoe images:

```python
from ml_pipeline.training.ocr_extractor import ShoeOCRExtractor

extractor = ShoeOCRExtractor()
info = extractor.extract_shoe_info(image, bbox=(x1, y1, x2, y2))
# Returns: size, numbers, model, brand_indicators
```

**Features:**
- Tesseract OCR integration
- Image preprocessing for better results
- Shoe size extraction
- Brand keyword detection
- Model number recognition

### Dataset Structure

```
datasets/dataset_YYYYMMDD_HHMMSS/
├── images/
│   ├── train/
│   │   ├── train_000001.jpg
│   │   ├── train_000002.jpg
│   │   └── ...
│   └── val/
│       ├── val_000001.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── train_000001.txt  # YOLO format: class_id x_center y_center width height
│   │   └── ...
│   └── val/
│       └── ...
└── data.yaml  # Dataset configuration
```

### YOLO Format

Labels are in YOLO format (normalized coordinates):
```
class_id x_center y_center width height
```

**Class IDs:**
- 0: Nike
- 1: Adidas
- 2: Puma
- 3: Other_Shoe

### Training Process

1. **Collect Data**: Detection logs accumulate as users scan shoes
2. **Prepare Dataset**: Convert logs to YOLO format
3. **Train Model**: Run YOLOv8 training on prepared dataset
4. **Evaluate**: Check accuracy and loss metrics
5. **Deploy**: Save best model for production use

### Installation Requirements

```bash
cd ml-pipeline
pip install -r requirements.txt
```

**Key Dependencies:**
- ultralytics (YOLO)
- opencv-python (image processing)
- pytesseract (OCR)
- pyyaml (configuration)

### Example Usage

```python
from ml_pipeline.training.train import YOLOTrainer
from ml_pipeline.training.color_analyzer import ShoeColorAnalyzer
from ml_pipeline.training.ocr_extractor import ShoeOCRExtractor

# Load image
import cv2
image = cv2.imread("shoe.jpg")

# Extract information
color_analyzer = ShoeColorAnalyzer()
colors = color_analyzer.extract_dominant_colors(image)

ocr_extractor = ShoeOCRExtractor()
text_info = ocr_extractor.extract_shoe_info(image)

# Train model with collected data
trainer = YOLOTrainer()
dataset_path = trainer.prepare_dataset(detection_logs)
results = trainer.train(dataset_path, epochs=10, batch_size=16)
```

### Continuous Learning Workflow

1. User registers product with camera/image
2. Backend processes:
   - YOLO detection
   - Color extraction
   - OCR text recognition
3. Detection log saved to database
4. Periodically (when enough data collected):
   - Backend triggers training task
   - YOLOTrainer prepares dataset
   - Model training starts in background
   - New model saved and deployed
5. Next detections use updated model

### Performance Tips

- **Image Preprocessing**: Scale images to 640x640 for optimal YOLO performance
- **Color K-means**: k=3 gives good balance between granularity and speed
- **OCR Preprocessing**: Grayscale + threshold + upscale improves accuracy
- **Batch Size**: Use 16 for RTX 3080+, 8 for RTX 2080, 4 for CPU
- **Epochs**: Start with 10, increase if accuracy plateaus

### Model Evaluation

Check training results:
```python
results = trainer.train(dataset_path, epochs=10)
print(f"Accuracy: {results['results']['accuracy']}")
print(f"Loss: {results['results']['loss']}")
```
