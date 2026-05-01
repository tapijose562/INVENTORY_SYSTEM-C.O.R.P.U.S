from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True)
    brand = Column(String(100), index=True)  # Nike, Adidas, Puma, etc.
    colors = Column(String(200))  # Formato: "Core Black / Cloud White / Cloud White"
    color_primary = Column(String(50), nullable=True)  # Legacy field
    color_secondary = Column(String(50), nullable=True)  # Legacy
    color_rgb = Column(JSON)  # {"r": 255, "g": 100, "b": 50} - color principal
    size = Column(String(20))
    stock = Column(Integer, default=0)
    price = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    
    # Image references (legacy - para backwards compatibility)
    image_url = Column(String(500), nullable=True)
    images_360 = Column(JSON)  # Array of image URLs
    
    # AI Detection metadata
    yolo_confidence = Column(Float)  # Confidence score from YOLO
    detected_text = Column(Text, nullable=True)  # OCR extracted text
    detection_metadata = Column(JSON)  # Additional detection data
    
    # User tracking
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Product {self.name} - {self.brand}>"


class ProductImage(Base):
    """Almacena múltiples imágenes por producto (máximo 10)"""
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    detection_log_id = Column(Integer, ForeignKey("detection_logs.id"), nullable=True)
    
    # Image data
    image_url = Column(String(500), index=True)  # Path or URL to the image
    image_filename = Column(String(200))  # Original filename
    image_size = Column(Integer)  # File size in bytes
    
    # Detection results (from when this image was detected)
    detected_brand = Column(String(100), nullable=True)
    detected_color = Column(String(50), nullable=True)
    detected_size = Column(String(20), nullable=True)
    detected_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    
    # Selection/Annotation data (Current Selection)
    selection_data = Column(JSON, nullable=True)  # {"x1": int, "y1": int, "x2": int, "y2": int}
    
    # Metadata
    detection_metadata = Column(JSON, nullable=True)  # BBOX, RGB, etc.
    image_metadata = Column(JSON, nullable=True)  # width, height, format, etc.
    
    # Status
    is_primary = Column(Integer, default=0)  # Imagen principal del producto (0 o 1)
    status = Column(String(20), default="pending")  # pending, detected, annotated, saved
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProductImage {self.id} - {self.image_filename}>"


class DetectionLog(Base):
    __tablename__ = "detection_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Detection results
    detected_brand = Column(String(100))
    detected_color = Column(String(50))
    detected_size = Column(String(20))
    detected_text = Column(Text)
    confidence_score = Column(Float)
    price = Column(Float, nullable=True)
    
    # Raw data
    image_path = Column(String(500))
    detection_metadata = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DetectionLog {self.detected_brand}>"


class TrainingSession(Base):
    __tablename__ = "training_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    status = Column(String(20))  # pending, running, completed, failed
    epochs = Column(Integer, default=10)
    batch_size = Column(Integer, default=16)
    dataset_size = Column(Integer)  # Number of images used
    
    # Results
    accuracy = Column(Float, nullable=True)
    loss = Column(Float, nullable=True)
    training_log = Column(Text, nullable=True)
    model_path = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<TrainingSession {self.name}>"


class Variant(Base):
    __tablename__ = "variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    color = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Variant {self.color} of product {self.product_id}>"


class Size(Base):
    __tablename__ = "sizes"

    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False, index=True)
    size = Column(Float, nullable=False)
    stock = Column(Integer, default=0)

    def __repr__(self):
        return f"<Size {self.size} (stock={self.stock}) of variant {self.variant_id}>"
