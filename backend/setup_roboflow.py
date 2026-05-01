#!/usr/bin/env python3
"""
Setup script for Roboflow Shoe Detector
Helps users configure and test the Roboflow model for real-time detection
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)


def create_models_directory():
    """Ensure models directory exists"""
    models_dir = os.path.join(backend_path, 'models')
    os.makedirs(models_dir, exist_ok=True)
    print(f"✅ Models directory: {models_dir}")
    return models_dir


def download_roboflow_model(api_key: str, project_id: str, version: int):
    """
    Download model from Roboflow
    Usage: python setup_roboflow.py --download <API_KEY> <PROJECT_ID> <VERSION>
    """
    print(f"📥 Downloading Roboflow model...")
    print(f"   Project: {project_id}")
    print(f"   Version: {version}")
    
    models_dir = create_models_directory()
    
    # Construct Roboflow download URL
    url = f"https://api.roboflow.com/model/download?api_key={api_key}&project={project_id}&version={version}&format=yolov8"
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        model_path = os.path.join(models_dir, 'roboflow_shoes.pt')
        
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Model downloaded: {model_path}")
        return model_path
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return None


def test_roboflow_detector():
    """Test the Roboflow detector with a sample image"""
    print("\n🧪 Testing Roboflow Shoe Detector...")
    
    try:
        from app.services.roboflow_detector import get_roboflow_detector
        import numpy as np
        import cv2
        
        detector = get_roboflow_detector()
        print("✅ Detector initialized")
        
        # Create a dummy image
        dummy_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test detection
        results = detector.detect_shoes_only(dummy_image)
        print(f"✅ Detection test completed: {len(results)} shoes found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing detector: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_models():
    """List available models"""
    models_dir = os.path.join(backend_path, 'models')
    
    print("\n📂 Available Models:")
    print("-" * 50)
    
    if os.path.exists(models_dir):
        models = [f for f in os.listdir(models_dir) if f.endswith('.pt')]
        if models:
            for model in models:
                path = os.path.join(models_dir, model)
                size = os.path.getsize(path) / (1024*1024)  # MB
                print(f"  • {model:<30} ({size:.1f} MB)")
        else:
            print("  ❌ No models found")
            print("  ℹ️  Place your roboflow_shoes.pt in models/")
    else:
        print(f"  ❌ Models directory not found: {models_dir}")


def show_config():
    """Show current configuration"""
    print("\n⚙️  Configuration:")
    print("-" * 50)
    
    try:
        from app.core.config import settings
        print(f"  YOLO Model Path: {settings.YOLO_MODEL_PATH}")
        print(f"  Confidence Threshold: {settings.YOLO_CONFIDENCE_THRESHOLD}")
        print(f"  Upload Directory: {settings.UPLOAD_DIR}")
    except Exception as e:
        print(f"  ❌ Error reading config: {e}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("🎥 ROBOFLOW SHOE DETECTOR - SETUP & TEST")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python setup_roboflow.py --test          # Test detector")
        print("  python setup_roboflow.py --list          # List models")
        print("  python setup_roboflow.py --config        # Show config")
        print("  python setup_roboflow.py --download <API_KEY> <PROJECT> <VERSION>")
        print("\nExample:")
        print("  python setup_roboflow.py --test")
        print("  python setup_roboflow.py --download abc123 shoe-detector 1")
        return
    
    command = sys.argv[1]
    
    if command == "--test":
        test_roboflow_detector()
    
    elif command == "--list":
        list_models()
    
    elif command == "--config":
        show_config()
    
    elif command == "--download":
        if len(sys.argv) < 5:
            print("❌ Missing arguments")
            print("Usage: python setup_roboflow.py --download <API_KEY> <PROJECT> <VERSION>")
            return
        
        api_key = sys.argv[2]
        project = sys.argv[3]
        version = int(sys.argv[4])
        
        download_roboflow_model(api_key, project, version)
    
    else:
        print(f"❌ Unknown command: {command}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
