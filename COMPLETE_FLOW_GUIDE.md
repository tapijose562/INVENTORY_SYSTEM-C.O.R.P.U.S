# 🎓 Complete Guide: Product Registration + Database Storage + YOLO Training

## ✅ System Status

**Backend**: ✅ Running on `http://localhost:8000`
- Database: SQLite with Nullable `created_by` (productss save without user ref)
- All products endpoints: GET /products, POST /products, POST /{id}/upload-image, POST /{id}/annotate

**Frontend**: Ready to display products from database  
- ProductsComponent updated to call ProductService.getProducts()
- Products pulled from database automatically

**Storage**: ✅ Verified working
- Database: `backend/inventory.db`
- Images: `backend/uploads/product_{{ID}}_{{UUID}}.jpg`
- YOLO Labels: `backend/uploads/labels/product_{{ID}}.txt`

---

## 📋 Complete Flow: From Detection to YOLO Training

### Step 1️⃣: Detection & Product Creation (UI + Backend)
**What happens:**
1. User in Detection page uploads image (NIKEGATO.jpg)
2. Clicks "Detect" → Image sent to `/api/v1/detection/detect-from-image`
3. Backend runs YOLO + Color Detection + OCR
4. Returns: `{ brand, color, size, text, bbox, confidence, rgb, metadata }`
5. User draws bbox on canvas
6. Clicks "✅ Save as Product + Annotate" button

**Backend automatically:**
```
POST /api/v1/products
{
  "name": "Nike Gato",
  "brand": "Nike",
  "color_primary": "green",
  "color_rgb": {"r":89, "g":121, "b":46},
  "size": "40",
  "stock": 5,
  "price": 99.99,
  "yolo_confidence": 0.75,
  "detected_text": "Nike",
  "description": "...",
  "detection_metadata": {...}
}
→ Returns: { id: 1, name, brand, ... }
```

---

### Step 2️⃣: Image Upload
**Frontend calls (automatically in save flow):**
```
POST /api/v1/products/{product_id}/upload-image
Content-Type: multipart/form-data
Body: { file: <image.jpg> }

→ Returns: { image_url: "uploads/product_1_abc123.jpg", ... }
```

**Backend action:**
- Saves image to: `backend/uploads/product_1_abc123.jpg`
- Updates product.image_url in database
- → Image now stored and referenced in DB

---

### Step 3️⃣: Annotation (Bbox to YOLO Labels)
**Frontend sends bbox coordinates:**
```
POST /api/v1/products/{product_id}/annotate
{
  "x1": 400,
  "y1": 300,
  "x2": 1200,
  "y2": 900,
  "class_name": "other_shoe"
}
```

**Backend converts to YOLO format:**
- Reads image: `backend/uploads/product_1_abc123.jpg`
- Gets image dimensions: e.g., 1600×1200
- Converts bbox to normalized YOLO format:
  ```
  x_center = (400+1200)/2 / 1600 = 0.5
  y_center = (300+900)/2 / 1200 = 0.5
  width = (1200-400) / 1600 = 0.5
  height = (900-300) / 1200 = 0.5
  ```
- Saves label file: `backend/uploads/labels/product_1.txt`
  ```
  0 0.5 0.5 0.5 0.5
  (class_id x_center y_center width height)
  ```
- Creates DetectionLog entry recording the annotation
- Updates product.detection_metadata with bbox info

---

### Step 4️⃣: Products Display (Database → UI)
**When users visit Products page:**

**Frontend (ProductsComponent):**
```typescript
ngOnInit() {
  this.productService.getProducts().subscribe(products => {
    // products = [
    //   { id:1, name:'Nike Gato', brand:'Nike', stock:5, 
    //     color_primary:'green', size:'40', price:99.99, 
    //     image_url:'uploads/product_1_abc123.jpg', ... }
    // ]
    this.products = products;
    this.extractBrands();
    this.filterProducts();
  });
}
```

**Backend returns:**
```
GET /api/v1/products
[
  {
    "id": 1,
    "name": "Nike Gato",
    "brand": "Nike",
    "color_primary": "green",
    "color_rgb": {"r":89, "g":121, "b":46},
    "size": "40",
    "stock": 5,
    "price": 99.99,
    "image_url": "uploads/product_1_abc123.jpg",
    "yolo_confidence": 0.75,
    "detected_text": "Nike",
    "created_at": "2026-03-31T21:04:36"
  }
]
```

**UI Shows:**
- Grid/List view with all products
- Filter by brand, search by name
- Color visualization (RGB circle)
- Stock indicator (red if < 5)
- Edit/Delete buttons

---

### Step 5️⃣: Training YOLO (With Collected Data)
**Goal:** Use the annotated products to improve YOLO shoe detection

**API Endpoint (create new or modify existing):**
```
POST /api/v1/training/start-training
{
  "name": "Training Session #1",
  "epochs": 10,
  "batch_size": 16
}

→ Returns: {
  "id": 1,
  "status": "pending",
  "dataset_size": 3,
  "epochs": 10,
  "batch_size": 16,
  "created_at": "2026-03-31T21:05:00"
}
```

**Backend Training Flow:**
1. Gathers all products with images and annotations
   ```python
   products = db.query(Product).filter(
     Product.image_url.isnot(None)
   ).all()
   ```
2. For each product:
   - Copy image to `ml-pipeline/training/datasets/images/train/`
   - Copy label to `ml-pipeline/training/datasets/labels/train/`
3. Calls YOLOTrainer.prepare_dataset()
   - Creates data.yaml with class definitions
   - Validates image/label pairs
4. Calls YOLOTrainer.train()
   - Runs: `yolo detect train data=data.yaml model=yolov8n.pt epochs=10 ...`
   - Saves trained model to `backend/models/yolov8n_trained.pt`
5. Updates TrainingSession with:
   - status: "completed"
   - accuracy, loss metrics
   - model_path

---

## 🗄️ Database Schema

### Products Table
```sql
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  name VARCHAR(200),
  brand VARCHAR(100),
  color_primary VARCHAR(50),
  color_secondary VARCHAR(50),
  color_rgb JSON,  -- {"r":89, "g":121, "b":46}
  size VARCHAR(20),
  stock INTEGER,
  price FLOAT,
  description TEXT,
  image_url VARCHAR(500),  -- "uploads/product_1_abc.jpg"
  yolo_confidence FLOAT,
  detected_text TEXT,
  detection_metadata JSON,  -- {"bbox":[...], "detection_id":...}
  created_by INTEGER NULL,  -- ForeignKey users.id (nullable)
  created_at DATETIME,
  updated_at DATETIME NULL
);
```

### DetectionLog Table
```sql
CREATE TABLE detection_logs (
  id INTEGER PRIMARY KEY,
  product_id INTEGER,  -- ForeignKey products.id
  user_id INTEGER,  -- ForeignKey users.id
  detected_brand VARCHAR(100),
  detected_color VARCHAR(50),
  detected_size VARCHAR(20),
  detected_text TEXT,
  confidence_score FLOAT,
  image_path VARCHAR(500),  -- "uploads/product_1_abc.jpg"
  detection_metadata JSON,  -- {"bbox":[x1,y1,x2,y2], "class_name":"..."}
  created_at DATETIME
);
```

### TrainingSession Table
```sql
CREATE TABLE training_sessions (
  id INTEGER PRIMARY KEY,
  name VARCHAR(200),
  status VARCHAR(20),  -- pending, running, completed, failed
  epochs INTEGER,
  batch_size INTEGER,
  dataset_size INTEGER,  -- number of annotated samples
  accuracy FLOAT,
  loss FLOAT,
  model_path VARCHAR(500),
  created_at DATETIME
);
```

---

## 🔄 API Endpoints Summary

### Detection API
- `POST /api/v1/detection/detect-from-image` - Send image, get detection results
- `POST /api/v1/detection/detect-from-url` - Send image URL, get detection results

### Products API
- `GET /api/v1/products` - List all products (with pagination, filtering)
- `GET /api/v1/products/{id}` - Get single product
- `POST /api/v1/products` - Create product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `POST /api/v1/products/{id}/upload-image` - Upload image for product
- `POST /api/v1/products/{id}/annotate` - Add bbox annotation → generates YOLO label

### Training API
- `POST /api/v1/training/start-training` - Start training session
- `GET /api/v1/training/sessions` - List all training sessions
- `GET /api/v1/training/sessions/{id}` - Get session details

---

## 🎬 How to Test Complete Flow

### 1. Backend Test (Python)
```bash
cd C:\Users\Juan rodriguez\systemasDiploma\Inventory-Corpus-v2
python test_complete_flow.py
```

**Output:**
```
1️⃣  Creating product...
✅ Product created! ID: 2

2️⃣  Uploading image...
✅ Image uploaded!
   Path: uploads/product_2_2b3f4cf3538a468b9a478a73be7c7c35.jpg

3️⃣  Adding annotation (bbox)...
✅ Annotation saved!
   BBox: (400, 300) - (1200, 900)

4️⃣  Fetching all products...
✅ Found 2 product(s)
```

### 2. Frontend Test (Angular)
1. Open browser: `http://localhost:4200`
2. Go to **Products** page
3. Should see products from database with:
   - Name, Brand, Size, Stock, Price
   - Color visualization
   - Confidence score
   - Edit/Delete buttons

### 3. Check Database Direct
```bash
cd C:\Users\Juan rodriguez\systemasDiploma\Inventory-Corpus-v2\backend
sqlite3 inventory.db "SELECT id, name, brand, stock, image_url FROM products;"
```

**Output:**
```
1|Nike Gato|Nike|5|
2|Nike Gato Premium|Nike|10|uploads/product_2_2b3f4cf3538a468b9a478a73be7c7c35.jpg
```

### 4. Check Images & Labels
```bash
ls -la backend/uploads/
ls -la backend/uploads/labels/

# Expected:
# uploads/
#   ├── product_1_abc123.jpg
#   ├── product_2_def456.jpg
#   └── labels/
#       ├── product_1.txt
#       └── product_2.txt
```

---

## 🚀 Next Steps

### 1. **Enable Display of Product Images in Products Page**
   - Add image preview in product cards
   - Show image_url from database

### 2. **Create Training UI**
   - Add Training page with progress bar
   - Show training sessions list
   - Display model accuracy/loss metrics

### 3. **Integrate Trained Model**
   - Use newly trained YOLO model in Detection
   - Compare detection results before/after training

### 4. **Re-enable Authentication**
   - Restore JWT auth in all endpoints
   - Map products to correct user

### 5. **Tesseract Installation** (Optional)
   - For full OCR text extraction
   - Currently returns empty text gracefully

---

## 📊 Data Flow Diagram

```
Detection Page
    ↓ [Upload Image]
Detection API (detect-from-image)
    ↓ [YOLO + Color + OCR]
Frontend gets: brand, color, bbox
    ↓ [Draw bbox on canvas]
User clicks "Save as Product + Annotate"
    ↓
1. POST /products → Create in DB
2. POST /{id}/upload-image → Save image file
3. POST /{id}/annotate → Convert bbox → Save YOLO label
    ↓
Database now has:
  - Product record (name, brand, size, stock, price)
  - Image file (backend/uploads/product_X_UUID.jpg)
  - YOLO label (backend/uploads/labels/product_X.txt)
    ↓
Products Page
    ↓ [GET /products]
Frontend shows all products in grid/list
    ↓
Training Page (future)
    ↓ [Gather all annotated products]
Training API
    ↓ [Prepare dataset, train YOLO]
New trained model saved
```

---

## ✅ Verified Working

- [x] Product creation (POST /products) → Status 200
- [x] Image upload (POST /{id}/upload-image) → Image saved
- [x] Annotation (POST /{id}/annotate) → BBox normalized + Label file created
- [x] Get all products (GET /products) → Returns DB records
- [x] Database persistence (products remain after server restart)
- [x] Frontend ProductService updated to use actual endpoints
- [x] Nullable user_id (products can be created without logged-in user)

---

## 🔧 Configuration Files

**Backend:**
- `backend/app/models/product.py` - Database models
- `backend/app/api/routes/products.py` - Product endpoints
- `backend/app/services/ai.py` - YOLO, Color, OCR services

**Frontend:**
- `frontend/src/app/services/product.service.ts` - API calls
- `frontend/src/app/pages/products/products.component.ts` - UI component
- `frontend/src/app/pages/detection/detection.component.ts` - Detection + save flow

**Database:**
- `backend/inventory.db` - SQLite database

---

## 🛠️ Commands Reference

### Start Backend
```powershell
cd "C:\Users\Juan rodriguez\systemasDiploma\Inventory-Corpus-v2\backend"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Start Frontend
```bash
cd "C:\Users\Juan rodriguez\systemasDiploma\Inventory-Corpus-v2\frontend"
ng serve
```

### Test Complete Flow
```bash
python test_complete_flow.py
```

### Query Database
```bash
sqlite3 backend/inventory.db "SELECT * FROM products;"
```

---

Generated: 2026-03-31
System: Inventory Corpus v2 - Advanced Shoe Detection with YOLO
