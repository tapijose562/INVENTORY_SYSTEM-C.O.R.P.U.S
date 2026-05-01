# API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require JWT authentication. Include header:
```
Authorization: Bearer {access_token}
```

---

## Authentication Endpoints

### Register User
```
POST /auth/register
```
**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "securepassword123"
}
```
**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "role": "user",
  "created_at": "2024-03-30T10:00:00Z"
}
```

### Login
```
POST /auth/login
```
**Request:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User
```
GET /auth/me
```
**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "role": "user",
  "created_at": "2024-03-30T10:00:00Z"
}
```

---

## Products Endpoints

### List Products
```
GET /products/?skip=0&limit=100&brand=Nike
```
**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 100)
- `brand` (string): Filter by brand name

**Response:**
```json
[
  {
    "id": 1,
    "name": "Nike Air Max",
    "brand": "Nike",
    "color_primary": "red",
    "color_secondary": "white",
    "size": "42",
    "stock": 15,
    "price": 129.99,
    "yolo_confidence": 0.95,
    "created_at": "2024-03-30T10:00:00Z",
    "updated_at": "2024-03-30T10:00:00Z"
  }
]
```

### Get Product
```
GET /products/{id}
```
**Response:** Single product object

### Create Product
```
POST /products/
```
**Request:**
```json
{
  "name": "Nike Air Max",
  "brand": "Nike",
  "color_primary": "red",
  "color_secondary": "white",
  "color_rgb": {"r": 255, "g": 0, "b": 0},
  "size": "42",
  "stock": 15,
  "price": 129.99,
  "yolo_confidence": 0.95,
  "detected_text": "Nike Air Max 90",
  "detection_metadata": {}
}
```

### Update Product
```
PUT /products/{id}
```
**Request:**
```json
{
  "name": "Nike Air Max Updated",
  "stock": 20,
  "price": 139.99
}
```

### Delete Product
```
DELETE /products/{id}
```

---

## Detection Endpoints

### Detect from Image (Upload)
```
POST /detection/detect-from-image
Content-Type: multipart/form-data
```
**Body:**
- `file`: Image file (jpg, png)

**Response:**
```json
{
  "brand": "Nike",
  "color": "red",
  "size": "42",
  "text": "Nike Air Max 90",
  "confidence": 0.951,
  "rgb": {
    "r": 255,
    "g": 0,
    "b": 0
  },
  "metadata": {
    "detection_id": 123,
    "bbox": [100, 100, 300, 400]
  }
}
```

### Detect from URL
```
POST /detection/detect-from-url
```
**Request:**
```json
{
  "image_url": "https://example.com/shoe.jpg"
}
```
**Response:** Same as detect-from-image

---

## Training Endpoints

### Start Training
```
POST /training/start-training
```
**Request:**
```json
{
  "name": "Training Session v1",
  "epochs": 10,
  "batch_size": 16
}
```
**Response:**
```json
{
  "id": 1,
  "name": "Training Session v1",
  "status": "pending",
  "dataset_size": 50,
  "accuracy": null,
  "loss": null,
  "created_at": "2024-03-30T10:00:00Z",
  "completed_at": null
}
```

### Get Training Sessions
```
GET /training/sessions
```
**Response:**
```json
[
  {
    "id": 1,
    "name": "Training Session v1",
    "status": "completed",
    "dataset_size": 50,
    "accuracy": 0.92,
    "loss": 0.15,
    "created_at": "2024-03-30T10:00:00Z",
    "completed_at": "2024-03-30T10:30:00Z"
  }
]
```

### Get Training Session Details
```
GET /training/sessions/{id}
```
**Response:** Single training session object

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Status Codes

- **200**: Success
- **201**: Created
- **204**: No Content
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Server Error
