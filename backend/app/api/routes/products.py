from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from uuid import uuid4
from app.db.database import get_db
from app.models.product import Product, DetectionLog, ProductImage
from app.models.user import User
from app.schemas import ProductCreate, ProductResponse, ProductUpdate, AnnotationRequest, ProductImageUploadResponse
from app.core.security import get_current_user, require_roles
from app.core.config import settings
from app.services.ai import YOLODetectionService, ColorDetectionService, OCRService, ImageProcessingService
import cv2
import numpy as np
from fastapi import Form
import json
from app.models.product import Variant, Size

router = APIRouter()

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Create a new product"""
    
    # Validate required fields
    if not product.name or not product.name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Product name is required"
        )
    
    if not product.brand or not product.brand.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Brand field is required"
        )
    
    # Use the new 'colors' field if provided, otherwise use color_primary for backwards compatibility
    colors_value = product.colors or product.color_primary or ""
    
    db_product = Product(
        name=product.name.strip(),
        brand=product.brand.strip(),
        colors=colors_value,
        color_primary=product.color_primary,
        color_secondary=product.color_secondary,
        color_rgb=product.color_rgb or {"r": 0, "g": 0, "b": 0},
        size=str(product.size),
        stock=product.stock,
        price=product.price,
        description=product.description,
        yolo_confidence=product.yolo_confidence or 0.5,
        detected_text=product.detected_text or "",
        detection_metadata=product.detection_metadata,
        image_url=product.image_url,  # Save image URL directly if provided
        created_by=current_user.id
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.post('/with-image', response_model=ProductResponse)
async def create_product_with_image(
    product_json: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Create product with variants and upload image in one request (multipart/form-data)
    Expects `product_json` as a JSON string with fields: product_name, brand, confidence, ocr_text, variants (array)
    """
    try:
        payload = json.loads(product_json)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid product_json: {e}")

    # Basic validation
    name = payload.get('product_name') or payload.get('name')
    brand = payload.get('brand')
    if not name or not brand:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="product_name and brand are required")

    # Save image
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1] or '.jpg'
    filename = f"product_{uuid4().hex}{file_ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, filename)
    content = await file.read()
    with open(save_path, 'wb') as f:
        f.write(content)

    # Create product
    colors_list = payload.get('colors') or []
    colors_str = ' / '.join(colors_list) if isinstance(colors_list, list) else (payload.get('colors') or '')

    db_product = Product(
        name=name.strip(),
        brand=brand.strip(),
        colors=colors_str,
        color_primary=colors_list[0] if isinstance(colors_list, list) and len(colors_list) > 0 else None,
        color_rgb=payload.get('rgb') or {},
        size=str(payload.get('size') or ''),
        stock=0,
        price=payload.get('price'),
        description=payload.get('ocr_text') or payload.get('detected_text') or None,
        yolo_confidence=payload.get('confidence') or 0.0,
        detected_text=payload.get('ocr_text') or None,
        detection_metadata=payload.get('detection_metadata') or {},
        image_url=f"{settings.UPLOAD_DIR}/{filename}",
        created_by=current_user.id,
        detection_log_id=payload.get('detection_log_id')  # Link to detection log if provided
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Variants
    variants = payload.get('variants') or []
    total_stock = 0
    for v in variants:
        color = v.get('color')
        if not color or not color.strip():
            continue
        variant = Variant(product_id=db_product.id, color=color.strip())
        db.add(variant)
        db.commit()
        db.refresh(variant)

        sizes = v.get('sizes') or []
        seen_sizes = set()
        for s in sizes:
            try:
                size_val = float(s.get('size'))
                stock_val = int(s.get('stock') or 0)
            except:
                continue
            if size_val < 0 or size_val > 50 or stock_val < 0:
                continue
            if size_val in seen_sizes:
                continue
            seen_sizes.add(size_val)
            sz = Size(variant_id=variant.id, size=size_val, stock=stock_val)
            db.add(sz)
            db.commit()
            db.refresh(sz)
            total_stock += stock_val

    # Update product stock
    db_product.stock = total_stock
    db.commit()
    db.refresh(db_product)

    return db_product

@router.post("/{product_id}/upload-image", response_model=ProductResponse)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Upload an image for a product and store path"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"product_{product_id}_{uuid4().hex}{file_ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, filename)

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    product.image_url = f"{settings.UPLOAD_DIR}/{filename}"
    db.commit()
    db.refresh(product)

    return product

@router.post("/{product_id}/annotate", response_model=ProductResponse)
async def annotate_product_image(
    product_id: int,
    annotation: AnnotationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Save annotation for product and create YOLO label"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if not product.image_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product must have an uploaded image before annotation")

    image_path = product.image_url.replace("/", os.sep)
    if not os.path.exists(image_path):
        image_path = os.path.join(settings.UPLOAD_DIR, os.path.basename(product.image_url))

    if not os.path.exists(image_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product image file not found")

    image = cv2.imread(image_path)
    if image is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    h, w = image.shape[:2]
    x1, y1, x2, y2 = map(float, (annotation.x1, annotation.y1, annotation.x2, annotation.y2))
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    x_center = ((x1 + x2) / 2.0) / w
    y_center = ((y1 + y2) / 2.0) / h
    box_width = (x2 - x1) / w
    box_height = (y2 - y1) / h

    class_mapping = {
        "Nike": 0,
        "Adidas": 1,
        "Puma": 2,
        "Other_Shoe": 3
    }
    class_id = class_mapping.get(annotation.class_name, 3)

    label_folder = os.path.join(settings.UPLOAD_DIR, "labels")
    os.makedirs(label_folder, exist_ok=True)

    label_file = os.path.join(label_folder, f"product_{product_id}.txt")
    with open(label_file, "w") as f:
        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")

    detection_log = DetectionLog(
        product_id=product.id,
        user_id=1,
        detected_brand=product.brand or annotation.class_name,
        detected_color=product.color_primary or "unknown",
        detected_size=product.size or "unknown",
        detected_text=product.description or "",
        confidence_score=1.0,
        image_path=product.image_url,
        detection_metadata={"bbox": [x1, y1, x2, y2], "class_name": annotation.class_name}
    )

    db.add(detection_log)
    db.commit()
    db.refresh(detection_log)

    product.detection_metadata = {**(product.detection_metadata or {}), "last_annotation": detection_log.detection_metadata}
    db.commit()
    db.refresh(product)

    return product

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get product by ID"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # If current user is not admin, return limited fields for buyer
    if current_user.role != "admin":
        limited = {
            "id": product.id,
            "name": product.name,
            "brand": product.brand,
            "colors": product.colors or product.color_primary,
            "size": product.size,
            "stock": product.stock,
            "price": product.price
        }
        return JSONResponse(content=limited)

    return product

@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    brand: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all products with optional filtering"""
    
    query = db.query(Product)
    
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    
    products = query.offset(skip).limit(limit).all()
    
    # Enrich products with images
    for product in products:
        # Get all images for this product
        product_images = db.query(ProductImage).filter(
            ProductImage.product_id == product.id
        ).order_by(ProductImage.is_primary.desc(), ProductImage.created_at).all()
        
        product.images = [
            {
                "id": img.id,
                "url": img.image_url,
                "filename": img.image_filename,
                "is_primary": img.is_primary == 1
            }
            for img in product_images
        ]
        
        # Set primary image URL for backwards compatibility
        if product_images:
            primary_image = next((img for img in product_images if img.is_primary == 1), product_images[0])
            product.image_url = primary_image.image_url
        else:
            product.image_url = None
        
        print(f"Product {product.id} ({product.name}): image_url = {product.image_url}, images_count = {len(product.images)}")
    
    db.commit()
    # If requester is not admin, filter fields
    if current_user.role != "admin":
        filtered = []
        for p in products:
            filtered.append({
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "colors": p.colors or p.color_primary,
                "size": p.size,
                "stock": p.stock,
                "price": p.price
            })
        return JSONResponse(content=filtered)

    return products

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Update a product"""
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    if product_update.name:
        db_product.name = product_update.name
    if product_update.brand:
        db_product.brand = product_update.brand
    if product_update.color_primary:
        db_product.color_primary = product_update.color_primary
    if product_update.color_secondary is not None:
        db_product.color_secondary = product_update.color_secondary
    if product_update.color_rgb is not None:
        db_product.color_rgb = product_update.color_rgb
    if product_update.size is not None:
        db_product.size = str(product_update.size)
    if product_update.stock is not None:
        db_product.stock = product_update.stock
    if product_update.price is not None:
        db_product.price = product_update.price
    if product_update.description is not None:
        db_product.description = product_update.description
    
    db.commit()
    db.refresh(db_product)
    
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Delete a product"""
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(db_product)
    db.commit()
    
    return {"message": f"Product {product_id} deleted successfully"}
