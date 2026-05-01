# Integración Batch Detection - Guía Completa

## 📋 Resumen

Se ha implementado un nuevo componente `BatchDetectionComponent` que soporta la carga y procesamiento de múltiples imágenes (hasta 10) con las siguientes características:

✅ Carga en lote de imágenes (drag & drop o selección)  
✅ Detección individual por imagen (YOLO + Color + OCR)  
✅ Galería interactiva para navegación  
✅ Canvas de selección por imagen  
✅ Gestión de imagen primaria  
✅ Eliminación de imágenes  
✅ Validación de máximo 10 imágenes  

---

## 🗂️ Estructura de Archivos Creados

```
frontend/src/app/
├── pages/detection/
│   ├── batch-detection.component.ts          (NEW - 365 líneas)
│   ├── batch-detection.component.html        (NEW - 280 líneas)
│   ├── batch-detection.component.scss        (NEW - 650 líneas)
│
└── pipes/
    └── file-preview.pipe.ts                 (NEW - 12 líneas)
```

---

## 🔗 Integración con Rutas

### app.routes.ts - Actualizado
```typescript
{
  path: 'batch-detection',
  loadComponent: () => import('./pages/detection/batch-detection.component').then(m => m.BatchDetectionComponent),
  canActivate: [AuthGuard]
}
```

**URL de Acceso:**
```
http://localhost:4200/batch-detection
```

---

## 🎯 Componentes y Servicios Utilizados

### Servicios Existentes (Reutilizados)
- `ProductImageService` - API calls para múltiples imágenes ✅
- `ProductService` - Obtener lista de productos ✅
- `DetectionService` - Ejecutar detección en imagen ✅
- `AuthService` - Autenticación ✅

### Componentes Internos
- `FilePreviewPipe` - Mostrar previsualizaciones de archivos locales
- Canvas HTML5 - Para dibujo de selecciones manuales
- Media API - Para captura de webcam (compatible)

---

## 🎨 Interfaz de Usuario

### Flujo de Uso

#### Fase 1: Upload (Sección de carga)
```
┌─────────────────────────────────────────┐
│  📸 Batch Image Upload & Detection      │
│                                         │
│  Step 1: Seleccionar Producto          │
│  [▼ Dropdown con productos]            │
│                                         │
│  Step 2: Seleccionar Imágenes          │
│  ┌──────────────────────────────────┐  │
│  │ Arrastra imágenes aquí           │  │
│  │ Máximo 10 imágenes, JPG/PNG      │  │
│  └──────────────────────────────────┘  │
│                                         │
│  Archivos seleccionados: 3/10          │
│  [Preview] [Preview] [Preview]         │
│                                         │
│  [🚀 Subir 3 Imágenes]                 │
└─────────────────────────────────────────┘
```

#### Fase 2: Gallery (Galería para procesamiento)
```
┌──────────────────────────────────────────────────────────┐
│                 IMAGEN PRINCIPAL (2/5)                   │
│  ┌────────────────────────────┐ ┌─────────────────────┐ │
│  │    [IMAGEN CON CANVAS]     │ │ 🔍 DETECCIÓN        │ │
│  │    (Dibuja para marcar)    │ │ [🎯 Detectar]       │ │
│  │                            │ │                     │ │
│  │                            │ │ Marca: Nike         │ │
│  │                            │ │ Color: Rojo         │ │
│  └────────────────────────────┘ │ Precio: $99.99      │ │
│                                 │ Confianza: 92%      │ │
│  [◀ Anterior] [2/5] [Siguiente] │                     │ │
│                                 │ 📐 SELECCIÓN        │ │
│                                 │ X1: 150, Y1: 200    │ │
│                                 │ X2: 450, Y2: 500    │ │
│                                 │ [💾 Guardar]        │ │
│                                 │                     │ │
│  ┌──────────────────────────┐  │ 📊 ESTADO           │ │
│  │ MINIATURAS DE IMÁGENES   │  │ detected ⭐          │ │
│  │ [1][2*][3][4][5]         │  │ [⭐ Hacer Principal]│ │
│  │                          │  │ [🗑️ Eliminar]      │ │
│  └──────────────────────────┘  └─────────────────────┘ │
│                                                          │
│  [✅ Finalizar]                                         │
└──────────────────────────────────────────────────────────┘
```

---

## 🔧 Métodos Principales

### Métodos de Carga de Archivos
```typescript
// Seleccionar archivos por diálogo
browseFiles(): void

// Manejar drag & drop
onDrop(event: DragEvent): void
onDragOver(event: DragEvent): void
onDragLeave(): void

// Agregar archivos a la selección
addFiles(files: File[]): void

// Remover archivo antes de subir
removeFile(index: number): void
```

### Métodos de Procesamiento
```typescript
// Subir todas las imágenes al servidor
startUpload(): void

// Ejecutar detección en imagen actual
detectCurrentImage(): void

// Guardar selección/anotación
saveCurrentImage(): void

// Marcar como imagen primaria
setAsPrimary(imageId: number): void

// Eliminar imagen
deleteImage(imageId: number, index: number): void
```

### Métodos de Navegación
```typescript
// Navegar entre imágenes
nextImage(): void
previousImage(): void

// Finalizar y volver a detección normal
finish(): void

// Resetear estado completo
resetState(): void
```

### Métodos de Canvas (Selección Manual)
```typescript
// Manejo de eventos del canvas
onCanvasMouseDown(event: MouseEvent): void
onCanvasMouseMove(event: MouseEvent): void
onCanvasMouseUp(event: MouseEvent): void

// Redibujar canvas con selección
redrawCanvas(): void
```

---

## 📊 Estados del Componente

| Estado | Descripción | Campos Activos |
|--------|-------------|----------------|
| `upload` | Selección de producto e imágenes | `productId`, `selectedFiles`, `availableProducts` |
| `processing` | Subiendo imágenes | `loading`, `error` |
| `gallery` | Visualización y procesamiento | `images`, `currentDetection`, `currentSelection` |

---

## 🛡️ Validaciones Implementadas

### Validación de Archivos
- ✅ Máximo 10 imágenes por lote
- ✅ Solo tipos JPEG/PNG/WebP
- ✅ Conteo en tiempo real (X/10)
- ✅ Impedir duplicados de cantidad

### Validación de Producto
- ✅ Producto requerido antes de upload
- ✅ Verificación de existe en base de datos
- ✅ Manejo de promesas de carga de productos

### Validación de Selección
- ✅ Mínimo 10x10 píxeles para considerarse válida
- ✅ Coordenadas dentro de límites del canvas
- ✅ Prevención de selecciones inválidas

---

## 🔄 Flujo de Datos API

### Secuencia de Operaciones

```
1. Usuario selecciona producto
        ↓
2. Usuario selecciona 1-10 imágenes (local)
        ↓
3. Usuario hace clic en "Subir X Imágenes"
        ↓
4. POST /api/v1/product-images/upload-batch
   - Headers: Auth token
   - Body: FormData con archivos
   - Validación: max 10 imágenes, product_id existe
   - Response: ProductImageListResponse
        ↓
5. Componente carga lista de ProductImage[] en gallery
        ↓
6. Usuario navega entre imágenes
        ↓
7. Usuario hace clic "🎯 Detectar Imagen"
        ↓
8. POST /api/v1/product-images/detect/{image_id}
   - Headers: Auth token
   - Backend: Ejecuta YOLO + Color + OCR + Búsqueda de precio
   - Response: DetectionResponse { brand, color, size, text, confidence, price, rgb }
        ↓
9. Usuario dibuja selección en canvas
        ↓
10. Usuario hace clic "💾 Guardar Selección"
        ↓
11. PATCH /api/v1/product-images/{image_id}
    - Body: { selection_data: {x1,y1,x2,y2}, status: "annotated" }
        ↓
12. Usuario marca como "Principal" (opcional)
        ↓
13. POST /api/v1/product-images/{image_id}/set-primary
        ↓
14. Usuario hace clic "✅ Finalizar"
        ↓
15. Componente se resetea, redirige a dashboard
```

---

## 🎯 Integración con Detección Existente

### El nuevo componente NO afecta:
- ✅ `DetectionComponent` original (sin cambios)
- ✅ Flujo de detección individual (webcam, upload, realtime)
- ✅ Sistema de productos existente
- ✅ Rutas de autenticación

### Coexistencia:
```
/detection           → DetectionComponent (existente)
/batch-detection     → BatchDetectionComponent (nuevo)
```

---

## 💻 Ejemplo de Uso desde Frontend

```typescript
// En un componente padre, enlazar al batch-detection
<a routerLink="/batch-detection" class="nav-link">
  📸 Batch Upload
</a>

// El componente se carga automáticamente
// y maneja todo el ciclo de vida
```

---

## 🔐 Seguridad

### Protecciones Implementadas

1. **Path Traversal**
   - Backend: `abspath()` validation en `/file/{filename}`
   - Solo sirve archivos de carpeta uploads

2. **Tamaño de Archivos**
   - Frontend: Validación de `file.size`
   - Backend: Configuración FastAPI `max_body_size`

3. **Tipo de Archivos**
   - Frontend: `accept="image/*"`
   - Backend: Validación MIME type en `/upload-batch`

4. **Autenticación**
   - Todos los endpoints requieren JWT token
   - AuthGuard en ruta

5. **Autorización**
   - Usuario solo puede ver/editar sus propias imágenes
   - ProductId debe ser de productos del usuario

---

## 🐛 Manejo de Errores

```typescript
// Errores mostrados al usuario
error: string = '';

// Estados de carga
loading: boolean = false;
detectionProcessing: boolean = false;

// Validaciones antes de operaciones
- "Por favor selecciona un producto"
- "Por favor selecciona al menos una imagen"
- "Ya has seleccionado el máximo de X imágenes"
- "Por favor haz una selección antes de guardar"

// Toast 🔴 en esquina inferior derecha para errores
```

---

## 📱 Responsividad

### Breakpoints

| Tamaño | Grid | Comportamiento |
|--------|------|-----------------|
| Desktop (>1024px) | 2 columnas (imagen + panel) | Layout normal |
| Tablet (768px-1024px) | Auto-ajuste | Panel se mueve abajo |
| Mobile (<768px) | 1 columna | Stack vertical |

---

## 🚀 Características Futuras (Roadmap)

- [ ] Batch detection automático (detectar todas sin intervención)
- [ ] Exportar anotaciones como YOLO labels
- [ ] Comparar resultados entre imágenes
- [ ] Reordenar imágenes por drag & drop
- [ ] Rotar/Flipear imágenes antes de detectar
- [ ] Atajos de teclado (Arrow keys para navegar)
- [ ] Historial de cambios por imagen

---

## 📝 Notas Técnicas

### Por qué un componente separado?
1. **Responsabilidad única**: BatchDetectionComponent solo maneja batch
2. **No invasivo**: DetectionComponent sin cambios
3. **Ciclo de vida limpio**: Cada componente auto-suficiente
4. **Testing simplificado**: Lógica modular

### Comunicación API-Frontend

```typescript
// ProductImageService actúa como adapter
private apiUrl = '/api/v1/product-images';

uploadBatchImages(productId, files)    // POST /upload-batch
getProductImages(productId)             // GET /product/{id}
detectImage(imageId)                    // POST /detect/{id}
updateImage(imageId, data)              // PATCH /{id}
setImageAsPrimary(imageId)              // POST /{id}/set-primary
deleteImage(imageId)                    // DELETE /{id}
```

---

## 🔄 Actualización app.config.ts (Si aplica)

Si usas providers centralizados, asegúrate que ProductImageService esté disponible:

```typescript
// app.config.ts (si Angular 17+ standalone)
export const appConfig: ApplicationConfig = {
  providers: [
    // ProductImageService se inyecta automáticamente
    // en BatchDetectionComponent via constructor
  ]
};
```

---

## ✅ Checklist de Integración

- [x] Componentes TypeScript creados
- [x] Templates HTML creados
- [x] Estilos SCSS creados
- [x] Pipe FilePreview creado
- [x] Ruta agregada a app.routes.ts
- [x] ProductImageService disponible
- [x] Backend endpoints listos (/product-images/*)
- [x] Migraciones DB ejecutadas
- [x] Validaciones implementadas
- [x] Error handling completado

---

## 🎓 Para Debug

```typescript
// En DevTools, habilitar logs
localStorage.setItem('debug', 'batch-detection:*');

// Ver estado del componente
this.detectionResult    // Último resultado
this.currentSelection   // Coords actuales
this.images            // Lista de ProductImage
this.loading           // ¿Cargando?
```

---

## 📞 Soporte

Para cambios futuros:
1. Modificar `batch-detection.component.ts` para lógica
2. Actualizar `batch-detection.component.html` para UI
3. Ajustar `batch-detection.component.scss` para estilos
4. Registrar nuevas rutas en `app.routes.ts` si es necesario

---

**Fecha de Creación:** 2024-Q1  
**Última Actualización:** Auto-generated  
**Estado:** ✅ LISTO PARA PRODUCCIÓN
