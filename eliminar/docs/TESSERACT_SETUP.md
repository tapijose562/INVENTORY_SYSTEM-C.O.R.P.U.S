# Tesseract OCR - Setup Guide

## ¿Qué es Tesseract?

Tesseract es un motor OCR (Optical Character Recognition) de código abierto que reconoce texto en imágenes. Es esencial para leer marcas, tallas y números en fotos de zapatos.

## Instalación por Sistema Operativo

### 🪟 Windows

1. **Descargar Instalador**
   - Ir a: https://github.com/UB-Mannheim/tesseract/wiki
   - Descargar: `tesseract-ocr-w64-setup-v5.x.x.exe`
   - Versión recomendada: 5.3.0 o superior

2. **Ejecutar Instalador**
   - Double-click en el .exe
   - Siguiente → Siguiente → Instalar
   - Ruta por defecto: `C:\Program Files\Tesseract-OCR`
   - Seleccionar idiomas: English (obligatorio) + Spanish (opcional)

3. **Verificar Instalación**
   ```bash
   cd "C:\Program Files\Tesseract-OCR"
   tesseract.exe --version
   ```

4. **Configurar en Proyecto**
   
   Editar `backend/.env`:
   ```env
   PYTESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe
   ```

### 🐧 Linux (Ubuntu/Debian)

```bash
# Instalar Tesseract
sudo apt-get update
sudo apt-get install tesseract-ocr

# Instalar idiomas adicionales
sudo apt-get install tesseract-ocr-spa  # Español

# Verificar instalación
tesseract --version
```

Editar `backend/.env`:
```env
PYTESSERACT_PATH=/usr/bin/tesseract
```

### 🍎 macOS

```bash
# Instalar con Homebrew
brew install tesseract

# Instalar idiomas
brew install tesseract-lang

# Verificar
tesseract --version
```

Editar `backend/.env`:
```env
PYTESSERACT_PATH=/usr/local/bin/tesseract
```

---

## Testing Tesseract

### Verificar Instalación en Python

```python
import pytesseract
from PIL import Image

# Probar OCR
try:
    text = pytesseract.image_to_string(Image.open("shoe.jpg"))
    print("OCR Text:", text)
except Exception as e:
    print("Error:", e)
```

### Ejecutar desde Backend

```bash
cd backend
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

---

## Lenguajes de OCR

### Descargar Idiomas Adicionales

**Windows:**
- Descargar archivos `.traineddata` desde: https://github.com/UB-Mannheim/tesseract/blob/master/tessdata/
- Guardar en: `C:\Program Files\Tesseract-OCR\tessdata\`

**Linux/Mac:**
```bash
# Español
sudo apt-get install tesseract-ocr-spa

# Francés
sudo apt-get install tesseract-ocr-fra
```

### Usar Idioma en Código

```python
# Español
text = pytesseract.image_to_string(Image.open("shoe.jpg"), lang='spa')

# Inglés + Español
text = pytesseract.image_to_string(Image.open("shoe.jpg"), lang='eng+spa')
```

---

## Troubleshooting

### ❌ "tesseract is not installed or it's not in your PATH"

**Solución 1 - Verificar ruta en .env**
```env
PYTESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe
```

**Solución 2 - Test directo**
```bash
# Windows
where tesseract

# Linux/Mac
which tesseract
```

**Solución 3 - Instalar pytesseract**
```bash
pip install pytesseract --upgrade
```

### ❌ "TesseractNotFoundError"

```python
# En backend/app/services/ai.py, antes de pytesseract:
import pytesseract
from app.core.config import settings

# Configurar ruta
if settings.PYTESSERACT_PATH:
    pytesseract.pytesseract.pytesseract_cmd = settings.PYTESSERACT_PATH
```

### ❌ Bajo reconocimiento de texto

Mejorar imagen antes de OCR:

```python
import cv2
import pytesseract

image = cv2.imread("shoe.jpg")

# Preprocessing
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# OCR en imagen procesada
text = pytesseract.image_to_string(thresh)
```

---

## Optimización para Nuestro Caso (Shoes)

```python
# Configuración recomendada para OCR de etiquetas de zapatos
def extract_shoe_text(image):
    import pytesseract
    
    # Redimensionar si es muy pequeño
    if image.shape[0] < 100:
        image = cv2.resize(image, None, fx=2, fy=2)
    
    # Preprocesar
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # OCR multiidioma
    text = pytesseract.image_to_string(binary, lang='eng+spa')
    
    return text.strip()
```

---

## Próximos pasos

✅ Tesseract instalado  
→ Configurar en backend  
→ Probar con imágenes reales  
→ Integrar en Detection API
