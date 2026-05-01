from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import cv2
import numpy as np
import json
import traceback
import time
from pathlib import Path

from app.core.config import settings
from app.core.security import hash_password
from app.db.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.product import Product
from app.api.routes import auth, products, detection, training, product_images
from app.services.ai import (
    YOLODetectionService,
    ColorDetectionService,
    OCRService,
    ImageProcessingService
)
from app.services.roboflow_detector import get_roboflow_detector
from migrate_add_product_columns import migrate_add_product_columns

# Debug: Print database URL and working directory
import os
print(f"[DEBUG] Current working directory: {os.getcwd()}")
print(f"[DEBUG] Database URL: {settings.database_url}")

# Create uploads directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Apply schema migrations only for SQLite databases
if settings.database_url.startswith("sqlite"):
    migrate_add_product_columns()

# Initialize services
yolo_service = YOLODetectionService()
color_service = ColorDetectionService()
ocr_service = OCRService()
image_service = ImageProcessingService()

# Initialize Roboflow detector for Real-Time Detection (shoes only)
roboflow_detector = get_roboflow_detector()
print("[INIT] Roboflow shoe detector initialized for real-time mode")

# Try to initialize corpus detector (trained YOLO model) for optional realtime mode
try:
    from app.services.corpus_detector_service import corpus_detector
    print("[INIT] Corpus detector service imported for optional realtime mode")
except Exception as e:
    corpus_detector = None
    print(f"[INIT] Corpus detector NOT available for realtime: {e}")

from app.models.role import Role

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    print("🚀 Starting Inventory Corpus v2 Server...")
    # Ensure roles exist (do NOT create hardcoded users)
    db = SessionLocal()
    try:
        for rname, desc in [("admin", "Administrator"), ("client", "Cliente/Comprador")]:
            exists = db.query(Role).filter(Role.name == rname).first()
            if not exists:
                db.add(Role(name=rname, description=desc))
        db.commit()
        print("✅ Roles ensured: admin, client")
    except Exception as e:
        print(f"⚠️ Error ensuring roles: {e}")
    finally:
        db.close()
    yield
    print("🛑 Shutting down server...")

# Initialize FastAPI app
app = FastAPI(
    title="Inventory Corpus v2 API",
    description="Sistema de gestión de inventario con IA y detección de objetos",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PRIORITY: Add WebSocket route FIRST before any routers
# This ensures the WebSocket endpoint is registered before the detection router
# ============================================================================
@app.websocket("/api/v1/detection/ws/real-time-detection")
async def real_time_detection_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for REAL-TIME DETECTION (Shoes Only)
    Uses Roboflow-trained model to detect ONLY shoes in live camera feed
    Other detection modes remain unchanged
    """

    print("[websocket] 🎥 Real-time detection connection requested")

    # Create database session for this WebSocket connection
    db = SessionLocal()

    await websocket.accept()
    print("[websocket] ✅ Real-time detection connection established (Roboflow - Shoes Only)")

    try:
        while True:
            # Receive frame data from client
            data = await websocket.receive_json()

            if data.get("type") == "frame":
                # Decode base64 image data
                import base64
                image_data = data.get("image", "")
                if not image_data:
                    await websocket.send_json({"error": "No image data provided"})
                    continue

                try:
                    start_time = time.time()
                    
                    # Remove data URL prefix if present
                    if image_data.startswith("data:image/"):
                        image_data = image_data.split(",")[1]

                    # Decode base64 to bytes
                    image_bytes = base64.b64decode(image_data)
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if image is None:
                        await websocket.send_json({"error": "Invalid image data"})
                        continue

                    # Resize for faster processing (real-time optimization)
                    image = image_service.resize_image(image, 416)  # Smaller for speed

                    # Select model for detection: 'roboflow' (default) or 'corpus'
                    model_choice = data.get("model", "roboflow")
                    if model_choice == "corpus" and corpus_detector is not None and corpus_detector.is_available():
                        # Use corpus trained YOLO model for detection
                        shoe_detections = corpus_detector.detect_objects(image, conf=0.4)
                    else:
                        # Fallback to Roboflow shoe-only detector for real-time
                        shoe_detections = roboflow_detector.detect_shoes_only(image, confidence_threshold=0.5)

                    if not shoe_detections:
                        # No shoes detected
                        await websocket.send_json({
                            "detections": [],
                            "shoe_count": 0,
                            "processing_time": time.time() - start_time,
                            "timestamp": time.time(),
                            "mode": "realtime-shoes-only"
                        })
                        continue

                    # Process each shoe detection
                    detection_results = []

                    for detection in shoe_detections:
                        bbox = detection["bbox"]

                        # Extract color from shoe region
                        try:
                            colors_string, dominant_rgb, all_colors_rgb = color_service.extract_multiple_colors(
                                image, bbox, max_colors=2
                            )
                        except:
                            colors_string = "Unknown"
                            dominant_rgb = {"r": 128, "g": 128, "b": 128}
                            all_colors_rgb = []

                        # Extract any text/numbers from shoe region (brand, size, etc)
                        try:
                            x1, y1, x2, y2 = bbox
                            roi = image[int(y1):int(y2), int(x1):int(x2)]
                            if roi.size > 0:
                                detected_text = ocr_service.extract_text(
                                    roi, [0, 0, roi.shape[1], roi.shape[0]]
                                )
                                numbers = ocr_service.extract_numbers(detected_text)
                            else:
                                detected_text = ""
                                numbers = []
                        except:
                            detected_text = ""
                            numbers = []

                        # Try to match with product database
                        product_price = None
                        product_brand = None
                        suggested_size = numbers[0] if numbers else None

                        try:
                            # Search in database by color or detected text
                            if colors_string and colors_string != "Unknown":
                                matching_product = db.query(Product).filter(
                                    Product.color.ilike(f"%{colors_string}%")
                                ).first()
                            else:
                                # Fallback to first shoe product
                                matching_product = db.query(Product).filter(
                                    Product.brand.ilike("%shoe%") | Product.brand.ilike("%adidas%")
                                ).first()
                            
                            if matching_product:
                                product_price = matching_product.price
                                product_brand = matching_product.brand
                                if not suggested_size:
                                    suggested_size = matching_product.size
                        except Exception as db_error:
                            print(f"[websocket] Database lookup warning: {db_error}")

                        detection_results.append({
                            "id": len(detection_results) + 1,
                            "bbox": bbox,
                            "class": "shoe",  # Always shoe in real-time mode
                            "confidence": round(detection["confidence"], 3),
                            "color": colors_string,
                            "rgb": dominant_rgb,
                            "detected_text": detected_text,
                            "detected_size": suggested_size or "Unknown",
                            "product_brand": product_brand or "Unknown",
                            "product_price": product_price,
                            "center": {
                                "x": detection["center_x"],
                                "y": detection["center_y"]
                            }
                        })

                    # Send results back to client
                    processing_time = time.time() - start_time
                    await websocket.send_json({
                        "detections": detection_results,
                        "shoe_count": len(detection_results),
                        "processing_time": round(processing_time, 3),
                        "fps": round(1.0 / max(processing_time, 0.001), 1),
                        "timestamp": time.time(),
                        "mode": "realtime-shoes-only",
                        "status": "✅ Shoes detected" if detection_results else "⚠️ No shoes detected"
                    })

                except Exception as e:
                    print(f"[websocket] ❌ Error processing frame: {e}")
                    import traceback
                    traceback.print_exc()
                    await websocket.send_json({
                        "error": f"Processing error: {str(e)}",
                        "mode": "realtime-shoes-only"
                    })

            elif data.get("type") == "ping":
                # Respond to ping to keep connection alive
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": time.time(),
                    "mode": "realtime-shoes-only"
                })

    except WebSocketDisconnect:
        print("[websocket] 🔴 Real-time detection connection closed")
    except Exception as e:
        print(f"[websocket] ❌ Unexpected error: {e}")
        try:
            await websocket.send_json({"error": f"Server error: {str(e)}"})
        except:
            pass
    finally:
        # Clean up database session
        db.close()
        print("[websocket] Database session cleaned up")

# Include Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(product_images.router, prefix="/api/v1/product-images", tags=["Product Images"])
app.include_router(detection.router, prefix="/api/v1/detection", tags=["Detection"])
app.include_router(training.router, prefix="/api/v1/training", tags=["Training"])

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "Inventory Corpus v2"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Inventory Corpus v2 API",
        "docs": "/docs",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
