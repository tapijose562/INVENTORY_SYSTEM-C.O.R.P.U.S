"""Product Images Management API"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
import os
import cv2
import numpy as np
from uuid import uuid4
from typing import List
from app.db.database import get_db
from app.models.product import Product, ProductImage, DetectionLog
from app.models.user import User
from app.schemas import (
    ProductImageCreate,
    ProductImageUpdate,
    ProductImageResponse,
    ProductImageListResponse,
    DetectionResponse
)
from app.core.config import settings
from app.services.ai import (
    YOLODetectionService,
    ColorDetectionService,
    OCRService,
    ImageProcessingService
)
from app.core.security import get_current_user, require_roles

router = APIRouter()

# Initialize services
yolo_service = YOLODetectionService()
color_service = ColorDetectionService()
ocr_service = OCRService()
image_service = ImageProcessingService()

MAX_IMAGES_PER_PRODUCT = 10


@router.post("/upload-batch", response_model=ProductImageListResponse)
async def upload_batch_images(
    product_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Upload multiple images for a product (máximo 10)"""
    
    try:
        # Check product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        
        # Check current image count
        current_count = db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).count()
        
        # Validate we won't exceed the total limit
        if current_count + len(files) > MAX_IMAGES_PER_PRODUCT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot upload {len(files)} images. Would exceed limit of {MAX_IMAGES_PER_PRODUCT}. Current: {current_count}"
            )
        
        # Process each file
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        uploaded_images = []
        
        for file in files:
            try:
                # Read file
                contents = await file.read()
                img = image_service.decode_image_bytes(contents)
                
                if img is None:
                    continue  # Skip invalid images
                
                # Get image metadata
                height, width = img.shape[:2]
                
                # Save image
                image_filename = f"product_{product_id}_{uuid4().hex}.jpg"
                image_path = os.path.join(settings.UPLOAD_DIR, image_filename)
                cv2.imwrite(image_path, img)
                
                # Create ProductImage record
                product_image = ProductImage(
                    product_id=product_id,
                    image_url=f"/uploads/{image_filename}",
                    image_filename=image_filename,
                    image_size=len(contents),
                    is_primary=0 if uploaded_images else 1,  # First image is primary
                    status="pending",
                    image_metadata={
                        "width": width,
                        "height": height,
                        "format": "jpeg"
                    }
                )
                
                db.add(product_image)
                db.flush()
                db.refresh(product_image)
                uploaded_images.append(product_image)
                
            except Exception as e:
                print(f"[product_images] Error processing file {file.filename}: {e}")
                continue
        
        db.commit()
        
        # Refresh all images from database to ensure all fields are properly serialized
        for img in uploaded_images:
            db.refresh(img)
        
        # Return list of uploaded images
        return {
            "total_images": len(uploaded_images),
            "images": uploaded_images,
            "max_images": MAX_IMAGES_PER_PRODUCT
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[product_images] Error uploading batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading images: {str(e)}"
        )


@router.get("/product/{product_id}", response_model=ProductImageListResponse)
async def get_product_images(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all images for a product"""
    
    try:
        # Check product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        
        # Get images ordered by is_primary and created_at
        images = db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).order_by(
            desc(ProductImage.is_primary),
            ProductImage.created_at
        ).all()
        
        return {
            "total_images": len(images),
            "images": images,
            "max_images": MAX_IMAGES_PER_PRODUCT
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving images: {str(e)}"
        )


@router.post("/detect/{image_id}", response_model=DetectionResponse)
async def detect_single_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run detection on a specific ProductImage"""
    
    try:
        # Get image record
        product_image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
        if not product_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image {image_id} not found"
            )
        
        # Read image from file
        image_path = product_image.image_url.replace("/uploads/", "")
        full_path = os.path.join(settings.UPLOAD_DIR, image_path)
        
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image file not found"
            )
        
        image = cv2.imread(full_path)
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not read image file"
            )
        
        # Run detection
        image = image_service.resize_image(image, 1920)
        yolo_detections = yolo_service.detect_shoes(image)
        
        if not yolo_detections:
            height, width = image.shape[:2]
            mock_detection = {
                "class": "demo_object",
                "confidence": 0.8,
                "bbox": [width//4, height//4, 3*width//4, 3*height//4],
                "area": float((width//2) * (height//2))
            }
            yolo_detections = [mock_detection]
        
        best_detection = max(yolo_detections, key=lambda x: x["confidence"])
        bbox = best_detection["bbox"]
        detected_class = best_detection["class"]
        
        # Map class to brand
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
        
        # Color Detection
        color_rgb, color_name = color_service.extract_dominant_color(image, bbox)
        
        # OCR
        detected_text = ocr_service.extract_text(image, bbox)
        numbers = ocr_service.extract_numbers(detected_text)
        
        # Search for price
        product_price = None
        try:
            if product_image.product_id:
                product = db.query(Product).filter(Product.id == product_image.product_id).first()
                if product and product.price:
                    product_price = product.price
        except:
            pass
        
        # Update ProductImage with detection results
        product_image.detected_brand = brand
        product_image.detected_color = color_name
        product_image.detected_size = numbers[0] if numbers else "unknown"
        product_image.detected_text = detected_text
        product_image.confidence_score = best_detection["confidence"]
        product_image.price = product_price
        product_image.detection_metadata = {
            "bbox": bbox,
            "yolo_class": detected_class,
            "rgb": color_rgb,
            "original_detection": best_detection
        }
        product_image.status = "detected"
        
        db.commit()
        db.refresh(product_image)
        
        return {
            "brand": brand,
            "color": color_name,
            "size": numbers[0] if numbers else "unknown",
            "text": detected_text,
            "confidence": best_detection["confidence"],
            "price": product_price,
            "rgb": color_rgb,
            "metadata": {
                "image_id": image_id,
                "product_id": product_image.product_id,
                "bbox": bbox,
                "original_class": detected_class,
                "image_url": product_image.image_url
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[product_images] Detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection error: {str(e)}"
        )


@router.patch("/{image_id}", response_model=ProductImageResponse)
async def update_image_selection(
    image_id: int,
    update_data: ProductImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Update detection results or selection for a specific image"""
    
    try:
        product_image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
        if not product_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image {image_id} not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(product_image, key, value)
        
        db.commit()
        db.refresh(product_image)
        
        return product_image
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating image: {str(e)}"
        )


@router.post("/{image_id}/set-primary", response_model=ProductImageResponse)
async def set_primary_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Set image as primary for its product"""
    
    try:
        product_image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
        if not product_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image {image_id} not found"
            )
        
        if not product_image.product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image not associated with a product"
            )
        
        # Remove primary flag from other images
        db.query(ProductImage).filter(
            ProductImage.product_id == product_image.product_id
        ).update({"is_primary": 0})
        
        # Set this as primary
        product_image.is_primary = 1
        db.commit()
        db.refresh(product_image)
        
        return product_image
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting primary image: {str(e)}"
        )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Delete a product image"""
    
    try:
        product_image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
        if not product_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image {image_id} not found"
            )
        
        # Delete file
        try:
            image_path = product_image.image_url.replace("/uploads/", "")
            full_path = os.path.join(settings.UPLOAD_DIR, image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"[product_images] Warning: Could not delete file: {e}")
        
        # Delete record
        db.delete(product_image)
        db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting image: {str(e)}"
        )


@router.get("/file/{filename}")
async def get_image_file(filename: str, current_user: User = Depends(get_current_user)):
    """Get image file by filename"""
    
    try:
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Security: prevent path traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(settings.UPLOAD_DIR)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image file not found"
            )
        
        from fastapi.responses import FileResponse
        return FileResponse(file_path, media_type="image/jpeg")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving file: {str(e)}"
        )
