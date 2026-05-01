from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Union
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: int
    # Use plain string for email in responses to avoid strict EmailStr validation
    # (some internal/test emails may use local TLDs like 'inventory.local')
    email: str
    is_active: bool
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    brand: str
    colors: Optional[str] = None  # Formato: "Core Black / Cloud White / Cloud White"
    color_primary: Optional[str] = None  # Legacy field
    color_secondary: Optional[str] = None  # Legacy field
    color_rgb: dict = Field(default={})
    size: Union[str, float, int]
    stock: int = 0
    price: Optional[float] = None
    description: Optional[str] = None

class ProductCreate(ProductBase):
    yolo_confidence: float = 0.0
    detected_text: Optional[str] = None
    detection_metadata: dict = Field(default={})
    image_url: Optional[str] = None  # Direct image URL from detection
    price: Optional[float] = Field(None, ge=10000)
    detection_log_id: Optional[int] = None  # Link to detection log

    @validator('yolo_confidence')
    def validate_yolo_confidence(cls, value):
        if value < 0.0 or value > 1.0:
            raise ValueError('YOLO confidence must be between 0.0 and 1.0')
        return value

    @validator('color_rgb')
    def validate_color_rgb(cls, value):
        if not isinstance(value, dict):
            raise ValueError('Color RGB must be a dictionary')
        if 'r' in value and 'g' in value and 'b' in value:
            r, g, b = value['r'], value['g'], value['b']
            if not (isinstance(r, int) and isinstance(g, int) and isinstance(b, int)):
                raise ValueError('RGB values must be integers')
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                raise ValueError('RGB values must be between 0 and 255')
        return value

    @validator('brand')
    def validate_brand(cls, value):
        if not value or not value.strip():
            raise ValueError('Brand field is required and cannot be empty')
        return value.strip()

    @validator('name')
    def validate_name(cls, value):
        if not value or not value.strip():
            raise ValueError('Product name is required and cannot be empty')
        return value.strip()

    @validator('size')
    def validate_size(cls, value):
        try:
            size_value = float(value)
        except (TypeError, ValueError):
            raise ValueError('Size must be numeric between 0 and 50')

        if size_value < 0 or size_value > 50:
            raise ValueError('Size must be between 0 and 50')

        return str(value)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    color_rgb: Optional[dict] = None
    size: Optional[Union[str, float, int]] = None
    stock: Optional[int] = None
    price: Optional[float] = Field(None, ge=10000)
    description: Optional[str] = None

    @validator('size')
    def validate_size(cls, value):
        if value is None:
            return value
        try:
            size_value = float(value)
        except (TypeError, ValueError):
            raise ValueError('Size must be numeric between 0 and 50')

        if size_value < 0 or size_value > 50:
            raise ValueError('Size must be between 0 and 50')

        return str(value)

class ProductResponse(ProductBase):
    id: int
    image_url: Optional[str]
    images: list = Field(default_factory=list)  # All product images
    yolo_confidence: float
    detected_text: Optional[str]
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ProductImage Schemas (múltiples imágenes por producto)
class ProductImageBase(BaseModel):
    image_url: str
    image_filename: str
    image_size: int

class ProductImageCreate(ProductImageBase):
    product_id: Optional[int] = None
    detected_brand: Optional[str] = None
    detected_color: Optional[str] = None
    detected_size: Optional[str] = None
    detected_text: Optional[str] = None
    confidence_score: Optional[float] = None
    price: Optional[float] = None
    detection_metadata: Optional[dict] = None
    image_metadata: Optional[dict] = None
    is_primary: int = 0
    status: str = "pending"

class ProductImageUpdate(BaseModel):
    detected_brand: Optional[str] = None
    detected_color: Optional[str] = None
    detected_size: Optional[str] = None
    detected_text: Optional[str] = None
    confidence_score: Optional[float] = None
    price: Optional[float] = None
    selection_data: Optional[dict] = None
    status: Optional[str] = None
    is_primary: Optional[int] = None

class ProductImageResponse(ProductImageBase):
    id: int
    product_id: Optional[int]
    detection_log_id: Optional[int]
    detected_brand: Optional[str]
    detected_color: Optional[str]
    detected_size: Optional[str]
    detected_text: Optional[str]
    confidence_score: Optional[float]
    price: Optional[float]
    selection_data: Optional[dict]
    detection_metadata: Optional[dict]
    image_metadata: Optional[dict]
    is_primary: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProductImageListResponse(BaseModel):
    """Response para listar imágenes de un producto"""
    total_images: int
    images: list[ProductImageResponse]
    max_images: int = 10

# Detection Schemas
class DetectionRequest(BaseModel):
    image: Optional[str] = None  # Base64 encoded
    file_path: Optional[str] = None

class DetectionResponse(BaseModel):
    brand: str
    color: str  # Multiple colors: "Color1 / Color2 / Color3"
    colors: Optional[str] = None  # Alternative field name for multiple colors
    size: str
    text: str
    confidence: float
    price: Optional[float] = None
    rgb: dict
    all_colors_rgb: Optional[list] = None  # Array of RGB values for each color
    annotated_image_url: Optional[str] = None
    metadata: dict
    
    class Config:
        from_attributes = True

class DetectionLogResponse(BaseModel):
    id: int
    detected_brand: str
    detected_color: str
    detected_size: str
    detected_text: Optional[str] = None
    confidence_score: float
    price: Optional[float] = None
    image_path: str
    detection_metadata: dict
    created_at: datetime
    
    class Config:
        from_attributes = True

class DetectionLogUpdate(BaseModel):
    detected_brand: Optional[str] = None
    detected_color: Optional[str] = None
    detected_size: Optional[str] = None
    detected_text: Optional[str] = None
    confidence_score: Optional[float] = None

# Training Schemas
class AnnotationRequest(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    class_name: str = "Other_Shoe"

class ProductImageUploadResponse(BaseModel):
    image_url: str
    yolo_label_path: str

    class Config:
        from_attributes = True

class TrainingSessionCreate(BaseModel):
    name: str
    epochs: int = 10
    batch_size: int = 16

class TrainingSessionResponse(BaseModel):
    id: int
    name: str
    status: str
    dataset_size: int
    accuracy: Optional[float]
    loss: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Auth Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
