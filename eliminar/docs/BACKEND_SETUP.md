## Backend Setup

### Prerequisites
- Python 3.13+
- pip

### Installation

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations and create database:
```bash
python main.py
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

#### Products
- `GET /api/v1/products/` - List products
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/{id}` - Get product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

#### Detection
- `POST /api/v1/detection/detect-from-image` - Detect from uploaded image
- `POST /api/v1/detection/detect-from-url` - Detect from image URL

#### Training
- `POST /api/v1/training/start-training` - Start model training
- `GET /api/v1/training/sessions` - Get training sessions
- `GET /api/v1/training/sessions/{id}` - Get training session details

### Features

1. **YOLO Detection**
   - Real-time shoe detection
   - Multiple brand support (Nike, Adidas, Puma, Other)
   - Brand classification with confidence scores

2. **Color Detection**
   - RGB color extraction
   - Dominant color identification
   - Color naming

3. **OCR Text Recognition**
   - Tesseract-based text extraction
   - Size number extraction
   - Model identification

4. **Continuous Training**
   - Automated dataset preparation
   - Background training tasks
   - Model versioning

5. **Authentication**
   - JWT-based authentication
   - User roles (admin/user)
   - Secure password hashing
