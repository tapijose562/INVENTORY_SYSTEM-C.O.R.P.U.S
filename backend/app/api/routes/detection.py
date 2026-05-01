from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import cv2
import numpy as np
import json
import traceback
import time
from uuid import uuid4
from app.db.database import get_db
from app.models.product import Product, DetectionLog
from app.models.user import User
from app.schemas import DetectionResponse
from app.core.security import get_current_user, require_roles
from app.core.config import settings
from app.services.ai import (
    YOLODetectionService,
    ColorDetectionService,
    OCRService,
    AISuggestionService,
    ImageProcessingService
)

# Import Corpus detector service
try:
    from app.services.corpus_detector_service import corpus_detector
    print("[detection] ✅ Corpus detector service imported successfully")
except ImportError as e:
    print(f"[detection] ❌ Failed to import corpus detector service: {e}")
    corpus_detector = None

router = APIRouter()

# Initialize services
yolo_service = YOLODetectionService()
color_service = ColorDetectionService()
ocr_service = OCRService()
image_service = ImageProcessingService()

@router.post("/detect-from-image", response_model=DetectionResponse)
async def detect_from_image(
    file: UploadFile = File(...),
    use_corpus: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect shoes, colors, and text from uploaded image with enhanced shoe detection"""

    start_time = time.time()

    try:
        # Read image from upload
        read_start = time.time()
        contents = await file.read()
        print(f"[detection] uploaded file name={file.filename}, content_type={file.content_type}, size={len(contents)}")
        image = ImageProcessingService.decode_image_bytes(contents)

        if image is None:
            print(f"[detection] Invalid image content received for file {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )

        print(f"[timing] Image decode: {time.time() - read_start:.2f}s")

        # Save uploaded image file to disk so that training pipeline can use it
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        image_filename = f"detect_{uuid4().hex}.jpg"
        image_path = os.path.join(settings.UPLOAD_DIR, image_filename)
        success = cv2.imwrite(image_path, image)
        if not success:
            print(f"[detection] Failed to save image file to {image_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded image"
            )

        # Resize to 800px for faster YOLO detection (was 1920px)
        resize_start = time.time()
        image = image_service.resize_image(image, 800)
        print(f"[timing] Image resize: {time.time() - resize_start:.2f}s")

        # YOLO Detection with enhanced shoe detection (allow corpus model)
        yolo_start = time.time()
        if use_corpus and corpus_detector is not None and corpus_detector.is_available():
            yolo_detections = corpus_detector.detect_objects(image)
        else:
            yolo_detections = yolo_service.detect_shoes(image)
        print(f"[timing] YOLO detection: {time.time() - yolo_start:.2f}s")
        print(f"[detection] Found {len(yolo_detections)} potential shoe detections")

        if not yolo_detections:
            # For demo purposes, create a smart mock detection if no objects detected
            height, width = image.shape[:2]
            mock_detection = {
                "class": "demo_object",
                "confidence": 0.8,
                "bbox": [width//4, height//4, 3*width//4, 3*height//4],
                "area": float((width//2) * (height//2)),
                "segmentation": None,
                "is_shoe": True
            }
            yolo_detections = [mock_detection]

        # Get best detection (highest confidence, most shoe-like)
        best_detection = max(yolo_detections, key=lambda x: x["confidence"])
        bbox = best_detection["bbox"]

        print(f"[detection] Best detection: {best_detection['class']} (conf: {best_detection['confidence']:.2f})")
        print(f"[detection] Bounding box: {bbox}")

        # Enhanced brand detection based on detection class
        detected_class = best_detection["class"]

        # More sophisticated brand mapping
        shoe_brand_mappings = {
            # Direct shoe detections
            "shoe": "Generic Shoe",
            "sneakers": "Nike",
            "running shoe": "Nike",
            "tennis shoe": "Adidas",
            "boot": "Timberland",
            "boots": "Timberland",
            "sandal": "Birkenstock",
            "sandals": "Birkenstock",
            "heel": "Jimmy Choo",
            "high heel": "Jimmy Choo",
            "slipper": "Generic Slipper",

            # Potential shoe objects (from enhanced detection)
            "potential_shoe_person": "Nike",
            "potential_shoe_handbag": "Gucci",
            "potential_shoe_backpack": "Adidas",
            "potential_shoe_suitcase": "Louis Vuitton",
            "potential_shoe_bottle": "Demo Brand",
            "potential_shoe_cup": "Demo Brand",
            "potential_shoe_chair": "Demo Brand",
            "potential_shoe_dining table": "Demo Brand",

            # Smart detected shoes
            "smart_detected_shoe": "Auto-Detected Shoe",

            # Fallback
            "demo_object": "Demo Shoe Detection"
        }

        brand = shoe_brand_mappings.get(detected_class, f"Detected: {detected_class}")

        # Add confidence-based brand refinement
        if best_detection["confidence"] > 0.8:
            brand += " (High Confidence)"
        elif best_detection["confidence"] > 0.6:
            brand += " (Medium Confidence)"
        else:
            brand += " (Low Confidence)"
        
        # Color Detection - Extract multiple colors
        color_start = time.time()
        colors_string, dominant_rgb, all_colors_rgb = color_service.extract_multiple_colors(image, bbox, max_colors=3)
        print(f"[timing] Color detection: {time.time() - color_start:.2f}s")
        
        # OCR Text Detection - with timeout protection
        ocr_start = time.time()
        print(f"[DEBUG] Llamando OCR con bbox: {bbox}")
        
        # Extract only the ROI for OCR (faster than processing full image)
        try:
            x1, y1, x2, y2 = bbox
            roi = image[int(y1):int(y2), int(x1):int(x2)]
            detected_text = ocr_service.extract_text(roi, [0, 0, roi.shape[1], roi.shape[0]])
        except Exception as ocr_error:
            print(f"[DEBUG] OCR ROI failed: {ocr_error}, falling back to full image")
            detected_text = ocr_service.extract_text(image, bbox)
        
        print(f"[timing] OCR detection: {time.time() - ocr_start:.2f}s")
        print(f"[DEBUG] OCR result: '{detected_text}'")
        numbers = ocr_service.extract_numbers(detected_text)
        
        # Search for matching product to get price
        product_price = None
        suggested_size = None
        
        # Determine size - prefer OCR numbers, then suggested from DB, then fallback
        final_size = numbers[0] if numbers else (suggested_size if suggested_size else "38")
        try:
            # Try to find a product matching brand and color
            matching_product = db.query(Product).filter(
                Product.brand.ilike(brand),
                Product.colors.ilike(f"%{all_colors_rgb[0]['name']}%") if all_colors_rgb else True
            ).first()
            
            if matching_product:
                product_price = matching_product.price
                suggested_size = matching_product.size
            else:
                # Try broader search - just by brand
                brand_match = db.query(Product).filter(
                    Product.brand.ilike(brand)
                ).first()
                
                if brand_match:
                    product_price = brand_match.price
                    suggested_size = brand_match.size
                else:
                    # Try by color only
                    color_match = db.query(Product).filter(
                        Product.colors.ilike(f"%{all_colors_rgb[0]['name']}%") if all_colors_rgb else Product.colors != ""
                    ).first()
                    
                    if color_match:
                        product_price = color_match.price
                        suggested_size = color_match.size
                    else:
                        # Get any product as fallback
                        any_product = db.query(Product).first()
                        if any_product:
                            product_price = any_product.price
                            suggested_size = any_product.size
        except Exception as search_error:
            print(f"[detection] Error searching for product price: {search_error}")
        
        # Store detection log
        detection_log = DetectionLog(
            user_id=current_user.id,  # Use actual user ID instead of hardcoded 1
            detected_brand=brand,
            detected_color=colors_string,  # Use multiple colors string
            detected_size=final_size,
            detected_text=detected_text,
            confidence_score=best_detection["confidence"],
            price=product_price,
            image_path=image_path,
            detection_metadata={
                "bbox": bbox,
                "yolo_class": detected_class,
                "rgb": dominant_rgb,
                "all_colors_rgb": all_colors_rgb,
                "original_detection": best_detection
            }
        )
        
        db.add(detection_log)
        db.commit()
        db.refresh(detection_log)
        
        # Create image URL for frontend access
        image_url = f"/api/v1/detection/images/{image_filename}"
        
        total_time = time.time() - start_time
        print(f"[timing] ✅ TOTAL detection time: {total_time:.2f}s")
        
        return {
            "brand": brand,
            "color": colors_string,  # Multiple colors: "Color1 / Color2 / Color3"
            "colors": colors_string,  # Also include as 'colors' field for frontend compatibility
            "size": final_size,
            "text": detected_text,
            "confidence": best_detection["confidence"],
            "price": product_price,
            "rgb": dominant_rgb,
            "all_colors_rgb": all_colors_rgb,
            "metadata": {
                "detection_id": detection_log.id,
                "bbox": bbox,
                "original_class": detected_class,
                "image_url": image_url,
                "image_filename": image_filename,
                "processing_time_seconds": round(total_time, 2)
            }
        }
        
    except Exception as e:
        print(f"[detection] error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection error: {str(e)}"
        )

@router.get("/images/{filename}")
async def get_detection_image(filename: str):
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detection image not found")
    return FileResponse(file_path)

@router.post("/get-all-detections")
async def get_all_detections(
    file: UploadFile = File(...),
    use_corpus: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all potential shoe detections from image for manual selection"""

    try:
        # Read image from upload
        contents = await file.read()
        image = ImageProcessingService.decode_image_bytes(contents)

        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )

        # Resize image for processing
        image = image_service.resize_image(image, 800)

        # Get all shoe detections (optionally use corpus trained model)
        if use_corpus and corpus_detector is not None and corpus_detector.is_available():
            yolo_detections = corpus_detector.detect_objects(image)
        else:
            yolo_detections = yolo_service.detect_shoes(image)

        # Format detections for frontend
        formatted_detections = []
        for i, detection in enumerate(yolo_detections[:5]):  # Limit to top 5
            bbox = detection["bbox"]
            segmentation = detection.get("segmentation")
            if not segmentation:
                x1, y1, x2, y2 = bbox
                segmentation = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]

            formatted_detections.append({
                "id": i,
                "class": detection["class"],
                "confidence": detection["confidence"],
                "bbox": bbox,
                "segmentation": segmentation,
                "area": detection["area"],
                "is_shoe": detection["is_shoe"],
                "center_x": detection.get("center_x", (bbox[0] + bbox[2]) / 2),
                "center_y": detection.get("center_y", (bbox[1] + bbox[3]) / 2),
                "recommended": i == 0  # Mark first as recommended
            })

        return {
            "detections": formatted_detections,
            "image_size": {"width": image.shape[1], "height": image.shape[0]},
            "total_found": len(yolo_detections)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting detections: {str(e)}"
        )


@router.post("/detect-from-selection")
async def detect_from_selection(
    file: UploadFile = File(...),
    detection_id: int = Form(0),
    use_corpus: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect from a specific selected detection"""

    try:
        # Read image from upload
        contents = await file.read()
        image = ImageProcessingService.decode_image_bytes(contents)

        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )

        # Resize image for processing
        image = image_service.resize_image(image, 800)

        # Get all detections (optionally use corpus model)
        if use_corpus and corpus_detector is not None and corpus_detector.is_available():
            yolo_detections = corpus_detector.detect_objects(image)
        else:
            yolo_detections = yolo_service.detect_shoes(image)

        if detection_id >= len(yolo_detections):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Detection ID {detection_id} not found"
            )

        # Use selected detection
        selected_detection = yolo_detections[detection_id]
        bbox = selected_detection["bbox"]

        print(f"[detection] Using selected detection: {selected_detection['class']} (conf: {selected_detection['confidence']:.2f})")

        # Process with selected detection (similar to main detection logic)
        detected_class = selected_detection["class"]

        shoe_brand_mappings = {
            "shoe": "Generic Shoe",
            "sneakers": "Nike",
            "running shoe": "Nike",
            "tennis shoe": "Adidas",
            "boot": "Timberland",
            "boots": "Timberland",
            "sandal": "Birkenstock",
            "sandals": "Birkenstock",
            "heel": "Jimmy Choo",
            "high heel": "Jimmy Choo",
            "slipper": "Generic Slipper",
            "potential_shoe_person": "Nike",
            "potential_shoe_handbag": "Gucci",
            "potential_shoe_backpack": "Adidas",
            "potential_shoe_suitcase": "Louis Vuitton",
            "smart_detected_shoe": "Auto-Detected Shoe",
            "demo_object": "Demo Shoe Detection"
        }

        brand = shoe_brand_mappings.get(detected_class, f"Detected: {detected_class}")

        # Color Detection
        colors_string, dominant_rgb, all_colors_rgb = color_service.extract_multiple_colors(image, bbox, max_colors=3)

        # OCR Text Detection
        try:
            x1, y1, x2, y2 = bbox
            roi = image[int(y1):int(y2), int(x1):int(x2)]
            detected_text = ocr_service.extract_text(roi, [0, 0, roi.shape[1], roi.shape[0]])
        except Exception as ocr_error:
            print(f"[DEBUG] OCR ROI failed: {ocr_error}, falling back to full image")
            detected_text = ocr_service.extract_text(image, bbox)

        numbers = ocr_service.extract_numbers(detected_text)

        # Search for matching product
        product_price = None
        suggested_size = None

        # Save uploaded/resized image and detection log
        try:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            saved_image_filename = f"detect_{uuid4().hex}.jpg"
            saved_image_path = os.path.join(settings.UPLOAD_DIR, saved_image_filename)
            cv2.imwrite(saved_image_path, image)

            detection_log = DetectionLog(
                image_path=saved_image_path,
                detected_brand=brand,
                detected_color=colors_string,
                detected_size=suggested_size,
                detected_text=detected_text,
                confidence_score=selected_detection["confidence"],
                detection_metadata={
                    "bbox": bbox,
                    "yolo_class": detected_class,
                    "original_detection": selected_detection
                }
            )

            db.add(detection_log)
            db.commit()
            db.refresh(detection_log)
        except Exception as log_err:
            print(f"[detect-from-selection] Failed to save detection log: {log_err}")
            db.rollback()
        # Create and save annotated image with the selected bbox highlighted
        try:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            annotated_filename = f"detect_selection_{uuid4().hex}.jpg"
            annotated_path = os.path.join(settings.UPLOAD_DIR, annotated_filename)

            # Draw bbox on a copy of the resized image
            annotated_image = image.copy()
            try:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.putText(annotated_image, f"Sel {detection_id} {detected_class} {selected_detection['confidence']:.2f}", (max(5, x1), max(20, y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            except Exception:
                pass

            cv2.imwrite(annotated_path, annotated_image)
            annotated_url = f"/api/v1/detection/images/{annotated_filename}"
        except Exception as save_err:
            print(f"[detect-from-selection] Failed to save annotated image: {save_err}")
            annotated_url = None

        return {
            "brand": brand,
            "colors": colors_string,
            "dominant_rgb": dominant_rgb,
            "all_colors_rgb": all_colors_rgb,
            "detected_text": detected_text,
            "numbers": numbers,
            "confidence": selected_detection["confidence"],
            "bbox": bbox,
            "suggested_price": product_price,
            "suggested_size": suggested_size,
            "detection_class": detected_class,
            "detection_id": detection_id,
            "annotated_image_url": annotated_url
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing selection: {str(e)}"
        )


async def detect_from_url(
    image_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect from image URL"""
    
    try:
        import requests
        
        response = requests.get(image_url, timeout=10)
        nparr = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image URL"
            )
        
        # Same detection logic
        image = image_service.resize_image(image, 1920)
        yolo_detections = yolo_service.detect_shoes(image)
        
        if not yolo_detections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No shoes detected in image"
            )
        
        best_detection = max(yolo_detections, key=lambda x: x["confidence"])
        bbox = best_detection["bbox"]
        
        # Color Detection - Extract multiple colors
        colors_string, dominant_rgb, all_colors_rgb = color_service.extract_multiple_colors(image, bbox, max_colors=3)
        detected_text = ocr_service.extract_text(image, bbox)
        numbers = ocr_service.extract_numbers(detected_text)
        
        # Map detected class to brand (same logic as detect-from-image)
        detected_class = best_detection["class"]
        shoe_mappings = {
            "person": "Nike",
            "handbag": "Gucci", 
            "backpack": "Adidas",
            "suitcase": "Louis Vuitton",
            "bottle": "Demo Brand",
            "cup": "Demo Brand",
            "chair": "Demo Brand",
            "dining table": "Demo Brand",
            "demo_object": "Demo Shoe Detection"
        }
        brand = shoe_mappings.get(detected_class, f"Detected: {detected_class}")
        
        # Search for matching product to get price
        product_price = None
        try:
            matching_product = db.query(Product).filter(
                Product.brand.ilike(brand),
                Product.colors.ilike(f"%{all_colors_rgb[0]['name']}%") if all_colors_rgb else True
            ).first()
            
            if matching_product and matching_product.price:
                product_price = matching_product.price
        except Exception as search_error:
            print(f"[detection] Error searching for product price: {search_error}")
        
        return {
            "brand": brand,
            "color": colors_string,  # Multiple colors: "Color1 / Color2 / Color3"
            "colors": colors_string,  # Also include as 'colors' field
            "size": numbers[0] if numbers else "unknown",
            "text": detected_text,
            "confidence": best_detection["confidence"],
            "price": product_price,
            "rgb": dominant_rgb,
            "all_colors_rgb": all_colors_rgb,
            "metadata": {
                "source": "url",
                "bbox": bbox
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection error: {str(e)}"
        )

@router.post("/suggest-text")
async def suggest_text(
    ocr_text: str = Form(""),
    brand: str = Form(""),
    color: str = Form(""),
    size: str = Form(""),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Suggest a cleaned OCR text using AI services"""
    try:
        image_info = ""
        if file is not None:
            contents = await file.read()
            image = image_service.decode_image_bytes(contents)
            if image is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image file"
                )
            image = image_service.resize_image(image, settings.MAX_IMAGE_SIZE)
            image_info = f"Image dimensions: {image.shape[1]}x{image.shape[0]}"

        if not ocr_text and not image_info and not brand and not color and not size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide OCR text, detection data or an image to generate a suggestion"
            )

        suggestion = AISuggestionService.suggest_text(
            ocr_text=ocr_text,
            image_info=image_info,
            brand=brand,
            color=color,
            size=size
        )

        return {"suggestion": suggestion}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[suggest-text] error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestion: {str(e)}"
        )


# ============================================================================
# NEW ENDPOINTS: List, Get, Update, Delete Detection Logs
# ============================================================================

@router.get("/logs", response_model=list)
async def get_detection_logs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """List all detection logs with pagination"""
    try:
        logs = db.query(DetectionLog).offset(skip).limit(limit).all()
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "brand": log.detected_brand,
                "color": log.detected_color,
                "size": log.detected_size,
                "text": log.detected_text,
                "confidence": log.confidence_score,
                "image_path": log.image_path,
                "image_url": f"/api/v1/detection/image/{log.id}",
                "metadata": log.detection_metadata,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving logs: {str(e)}"
        )


@router.get("/logs/{log_id}")
async def get_detection_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Get a specific detection log"""
    try:
        log = db.query(DetectionLog).filter(DetectionLog.id == log_id).first()
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Detection log {log_id} not found"
            )
        
        return {
            "id": log.id,
            "brand": log.detected_brand,
            "color": log.detected_color,
            "size": log.detected_size,
            "text": log.detected_text,
            "confidence": log.confidence_score,
            "image_path": log.image_path,
            "image_url": f"/api/v1/detection/image/{log.id}",
            "metadata": log.detection_metadata,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving log: {str(e)}"
        )


@router.put("/logs/{log_id}")
async def update_detection_log(
    log_id: int,
    updates: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Update fields of a detection log"""
    try:
        log = db.query(DetectionLog).filter(DetectionLog.id == log_id).first()
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Detection log {log_id} not found"
            )
        
        # Update allowed fields
        allowed_fields = {"detected_brand", "detected_color", "detected_size", "detected_text", "confidence_score", "detection_metadata", "price"}
        for field, value in updates.items():
            if field not in allowed_fields or value is None:
                continue

            if field == "detected_size":
                try:
                    size_value = float(value)
                except (TypeError, ValueError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Size must be numeric between 0 and 50"
                    )
                if size_value < 0 or size_value > 50:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Size must be between 0 and 50"
                    )
                setattr(log, field, str(value))
                continue

            if field == "price":
                try:
                    price_value = float(value)
                except (TypeError, ValueError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Price must be a numeric value"
                    )
                if price_value < 10000:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Price must be at least 10,000 COP"
                    )
                setattr(log, field, price_value)
                continue

            setattr(log, field, value)
        
        db.commit()
        db.refresh(log)
        
        return {
            "id": log.id,
            "brand": log.detected_brand,
            "color": log.detected_color,
            "size": log.detected_size,
            "text": log.detected_text,
            "confidence": log.confidence_score,
            "price": log.price,
            "image_path": log.image_path,
            "image_url": f"/api/v1/detection/image/{log.id}",
            "metadata": log.detection_metadata,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating log: {str(e)}"
        )


@router.delete("/logs/{log_id}")
async def delete_detection_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Delete a detection log"""
    try:
        log = db.query(DetectionLog).filter(DetectionLog.id == log_id).first()
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Detection log {log_id} not found"
            )
        
        # Optionally delete image file
        if log.image_path and os.path.exists(log.image_path):
            try:
                os.remove(log.image_path)
            except:
                pass  # Continue even if file deletion fails
        
        db.delete(log)
        db.commit()
        
        return {"message": f"Detection log {log_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting log: {str(e)}"
        )


@router.get("/image/{log_id}")
async def get_detection_image(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Get the image for a detection log"""
    try:
        from fastapi.responses import FileResponse
        
        log = db.query(DetectionLog).filter(DetectionLog.id == log_id).first()
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Detection log {log_id} not found"
            )
        
        if not os.path.exists(log.image_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image file not found"
            )
        
        return FileResponse(log.image_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving image: {str(e)}"
        )


@router.get("/images/{filename}")
async def get_detection_image_by_filename(filename: str, current_user: User = Depends(get_current_user)):
    """Get a detection image by filename"""
    try:
        image_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Security: Prevent directory traversal
        if not os.path.abspath(image_path).startswith(os.path.abspath(settings.UPLOAD_DIR)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        return FileResponse(image_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving image: {str(e)}"
        )


@router.post("/detect-color-from-selection")
async def detect_color_from_selection(
    file: UploadFile = File(...),
    bbox: str = Form(...)
):
    """Detect color from a specific selection/region in the image"""
    try:
        # Read image from upload
        contents = await file.read()
        image = image_service.decode_image_bytes(contents)

        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )

        # Parse bbox coordinates
        try:
            bbox_coords = json.loads(bbox)
            if len(bbox_coords) != 4:
                raise ValueError("Invalid bbox format")
            x1, y1, x2, y2 = [int(coord) for coord in bbox_coords]
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid bbox format: {str(e)}"
            )

        # Validate bbox coordinates
        height, width = image.shape[:2]
        x1 = max(0, min(x1, width))
        y1 = max(0, min(y1, height))
        x2 = max(0, min(x2, width))
        y2 = max(0, min(y2, height))

        if x2 <= x1 or y2 <= y1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bbox coordinates"
            )

        # Extract color from the selected region
        rgb_dict, color_name = color_service.extract_dominant_color(image, [x1, y1, x2, y2])

        return {
            "color_name": color_name,
            "rgb": rgb_dict
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[detect-color-from-selection] error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Color detection error: {str(e)}"
        )


# ============================================================================
# REAL-TIME DETECTION ENDPOINTS
# ============================================================================

# WebSocket endpoint moved to main.py for proper registration

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

                    # Process frame (similar to detect_from_image but optimized for real-time)
                    start_time = time.time()

                    # Resize for faster processing
                    image = image_service.resize_image(image, 640)  # Smaller for real-time

                    # YOLO Detection
                    yolo_detections = yolo_service.detect_shoes(image)

                    if not yolo_detections:
                        # Send empty result for no detections
                        await websocket.send_json({
                            "detections": [],
                            "processing_time": time.time() - start_time,
                            "timestamp": time.time()
                        })
                        continue

                    # Process detections
                    detection_results = []

                    for detection in yolo_detections:
                        bbox = detection["bbox"]

                        # Quick color detection (simplified for real-time)
                        try:
                            colors_string, dominant_rgb, all_colors_rgb = color_service.extract_multiple_colors(image, bbox, max_colors=2)
                        except:
                            colors_string = "Unknown"
                            dominant_rgb = {"r": 128, "g": 128, "b": 128}
                            all_colors_rgb = []

                        # Quick OCR (simplified for real-time)
                        try:
                            x1, y1, x2, y2 = bbox
                            roi = image[int(y1):int(y2), int(x1):int(x2)]
                            detected_text = ocr_service.extract_text(roi, [0, 0, roi.shape[1], roi.shape[0]])
                            numbers = ocr_service.extract_numbers(detected_text)
                        except:
                            detected_text = ""
                            numbers = []

                        # Map to brand
                        detected_class = detection["class"]
                        shoe_brand_mappings = {
                            "shoe": "Generic Shoe",
                            "sneakers": "Nike",
                            "running shoe": "Nike",
                            "tennis shoe": "Adidas",
                            "boot": "Timberland",
                            "sandal": "Birkenstock",
                            "demo_object": "Demo Detection"
                        }
                        brand = shoe_brand_mappings.get(detected_class, f"Detected: {detected_class}")

                        # Search for matching product
                        product_price = None
                        suggested_size = numbers[0] if numbers else None

                        try:
                            matching_product = db.query(Product).filter(
                                Product.brand.ilike(brand)
                            ).first()
                            if matching_product:
                                product_price = matching_product.price
                                if not suggested_size:
                                    suggested_size = matching_product.size
                        except:
                            pass

                        detection_results.append({
                            "bbox": bbox,
                            "class": detected_class,
                            "brand": brand,
                            "confidence": detection["confidence"],
                            "color": colors_string,
                            "rgb": dominant_rgb,
                            "text": detected_text,
                            "size": suggested_size or "Unknown",
                            "price": product_price
                        })

                    # Send results back to client
                    await websocket.send_json({
                        "detections": detection_results,
                        "processing_time": time.time() - start_time,
                        "timestamp": time.time(),
                        "fps": 1.0 / max(time.time() - start_time, 0.001)  # Estimated FPS
                    })

                except Exception as e:
                    print(f"[websocket] Error processing frame: {e}")
                    await websocket.send_json({"error": f"Processing error: {str(e)}"})

            elif data.get("type") == "ping":
                # Respond to ping to keep connection alive
                await websocket.send_json({"type": "pong", "timestamp": time.time()})

    except WebSocketDisconnect:
        print("[websocket] Real-time detection connection closed")
    except Exception as e:
        print(f"[websocket] Unexpected error: {e}")
        try:
            await websocket.send_json({"error": f"Server error: {str(e)}"})
        except:
            pass
    finally:
        # Clean up database session
        db.close()


# ============================================================================
# CORPUS DETECTOR ENDPOINTS - Using trained YOLO model
# ============================================================================

@router.post("/detect-corpus", response_model=DetectionResponse)
async def detect_with_corpus_model(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect shoes using the trained Corpus YOLO model"""

    start_time = time.time()

    try:
        # Import corpus detector service
        from app.services.corpus_detector_service import corpus_detector

        # Check if model is available
        if not corpus_detector.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Corpus detector model not available"
            )

        # Read image from upload
        contents = await file.read()
        image = ImageProcessingService.decode_image_bytes(contents)

        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )

        # Save uploaded image file to disk
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        image_filename = f"corpus_detect_{uuid4().hex}.jpg"
        image_path = os.path.join(settings.UPLOAD_DIR, image_filename)
        success = cv2.imwrite(image_path, image)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded image"
            )

        # Resize for faster processing
        image = image_service.resize_image(image, 800)

        # Detect with Corpus model
        corpus_detections = corpus_detector.detect_objects(image, conf=0.3)

        if not corpus_detections:
            # Fallback: create mock detection for demo
            height, width = image.shape[:2]
            mock_detection = {
                "class": "demo_object",
                "confidence": 0.8,
                "bbox": [width//4, height//4, 3*width//4, 3*height//4],
                "area": float((width//2) * (height//2)),
                "segmentation": None
            }
            corpus_detections = [mock_detection]

        # Get best detection
        best_detection = max(corpus_detections, key=lambda x: x["confidence"])
        bbox = best_detection["bbox"]

        print(f"[corpus] Best detection: {best_detection['class']} (conf: {best_detection['confidence']:.2f})")

        # Map class to brand
        class_to_brand = {
            "marca": "Nike",  # Trained on Nike/Adidas
            "shoe": "Adidas",
            "texto": "Generic Brand"
        }

        brand = class_to_brand.get(best_detection["class"], f"Detected: {best_detection['class']}")

        # Color Detection
        colors_string, dominant_rgb, all_colors_rgb = color_service.extract_multiple_colors(image, bbox, max_colors=3)

        # OCR Text Detection
        try:
            x1, y1, x2, y2 = bbox
            roi = image[int(y1):int(y2), int(x1):int(x2)]
            detected_text = ocr_service.extract_text(roi, [0, 0, roi.shape[1], roi.shape[0]])
        except Exception as ocr_error:
            print(f"[corpus] OCR ROI failed: {ocr_error}, falling back to full image")
            detected_text = ocr_service.extract_text(image, bbox)

        numbers = ocr_service.extract_numbers(detected_text)

        # Search for matching product
        product_price = None
        suggested_size = None

        final_size = numbers[0] if numbers else "38"

        try:
            matching_product = db.query(Product).filter(
                Product.brand.ilike(brand),
                Product.colors.ilike(f"%{all_colors_rgb[0]['name']}%") if all_colors_rgb else True
            ).first()

            if matching_product:
                product_price = matching_product.price
                suggested_size = matching_product.size
            else:
                brand_match = db.query(Product).filter(
                    Product.brand.ilike(brand)
                ).first()

                if brand_match:
                    product_price = brand_match.price
                    suggested_size = brand_match.size

        except Exception as db_error:
            print(f"[corpus] Database search error: {db_error}")

        # Create detection log
        detection_log = DetectionLog(
            image_path=image_path,
            detected_brand=brand,
            detected_color=colors_string,
            detected_size=final_size,
            detected_text=detected_text,
            confidence_score=best_detection["confidence"],
            detection_metadata={
                "model": "corpus_detector",
                "class": best_detection["class"],
                "bbox": bbox,
                "all_detections": len(corpus_detections),
                "segmentation_available": best_detection.get("segmentation") is not None
            },
            price=product_price
        )

        db.add(detection_log)
        db.commit()
        db.refresh(detection_log)

        # Generate result image URL
        image_url = f"/api/v1/detection/images/{image_filename}"

        # Create and save annotated image (draw bbox) for frontend display
        try:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            annotated_filename = f"corpus_detect_annotated_{uuid4().hex}.jpg"
            annotated_path = os.path.join(settings.UPLOAD_DIR, annotated_filename)

            annotated_image = image.copy()
            try:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.putText(annotated_image, f"{best_detection['class']} {best_detection['confidence']:.2f}", (max(5, x1), max(20, y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            except Exception:
                pass

            cv2.imwrite(annotated_path, annotated_image)
            annotated_url = f"/api/v1/detection/images/{annotated_filename}"
        except Exception as ann_err:
            print(f"[corpus] Failed to save annotated image: {ann_err}")
            annotated_url = None

        total_time = time.time() - start_time

        return {
            "brand": brand,
            "color": colors_string,
            "colors": colors_string,  # Also include as 'colors' field for frontend compatibility
            "size": final_size,
            "text": detected_text,
            "price": product_price,
            "confidence": best_detection["confidence"],
            "rgb": dominant_rgb,
            "all_colors_rgb": all_colors_rgb,
            "annotated_image_url": annotated_url,
            "metadata": {
                "detection_id": detection_log.id,
                "bbox": bbox,
                "model": "corpus_detector",
                "class": best_detection["class"],
                "image_url": image_url,
                "image_filename": image_filename,
                "processing_time_seconds": round(total_time, 2)
            }
        }

    except Exception as e:
        print(f"[corpus] Error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Corpus detection error: {str(e)}"
        )


@router.post("/detect-corpus-realtime")
async def detect_corpus_realtime(
    file: UploadFile = File(...)
):
    """Real-time detection using Corpus model - optimized for webcam frames"""

    try:
        from app.services.corpus_detector_service import corpus_detector

        if not corpus_detector.is_available():
            return {
                "detections": [],
                "summary": {"total_objects": 0, "shoes": 0, "brands": 0, "texts": 0, "avg_confidence": 0.0},
                "error": "Corpus model not available"
            }

        # Read image
        contents = await file.read()
        image = ImageProcessingService.decode_image_bytes(contents)

        if image is None:
            return {"error": "Invalid image"}

        # Resize for real-time processing
        image = image_service.resize_image(image, 640)  # Smaller for faster processing

        # Detect objects
        detections = corpus_detector.detect_objects(image, conf=0.4)  # Slightly higher confidence for real-time

        # Get summary
        summary = corpus_detector.get_detection_summary(detections)

        return {
            "detections": detections,
            "summary": summary
        }

    except Exception as e:
        print(f"[corpus-realtime] Error: {e}")
        return {
            "detections": [],
            "summary": {"total_objects": 0, "shoes": 0, "brands": 0, "texts": 0, "avg_confidence": 0.0},
            "error": str(e)
        }


@router.get("/corpus-status")
async def get_corpus_detector_status():
    """Check if Corpus detector model is available"""
    from app.services.corpus_detector_service import corpus_detector

    return {
        "available": corpus_detector.is_available(),
        "model_path": "corpus_detector.pt",
        "classes": ["marca", "shoe", "texto"]
    }
