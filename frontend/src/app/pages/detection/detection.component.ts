import { Component, OnInit, ViewChild, ElementRef, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { DetectionService } from '../../services/detection.service';
import { ProductService } from '../../services/product.service';
import { AuthService } from '../../services/auth.service';
import { DetectionLogService } from '../../services/detection-log.service';
import { ProductImageService, ProductImage } from '../../services/product-image.service';
import { FilePreviewPipe } from '../../pipes/file-preview.pipe';
import { VariantEditorComponent } from '../../components/variant-editor/variant-editor.component';
// MatDialog removed (manual selection dialog deprecated)
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
// DetectionDialogComponent (manual dialog) removed

@Component({
  selector: 'app-detection',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    FilePreviewPipe,
    
    MatButtonModule,
    MatIconModule,
    VariantEditorComponent
  ],
  templateUrl: './detection.component.html',
  styleUrls: ['./detection.component.scss']
})
export class DetectionComponent implements OnInit {
  @ViewChild('webcam') webcamElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvas') canvasElement!: ElementRef<HTMLCanvasElement>;
  @ViewChild('annotationCanvas') annotationCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('resultImageElement') resultImageElement!: ElementRef<HTMLImageElement>;
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
  @ViewChild('fullscreenImage') fullscreenImage!: ElementRef<HTMLImageElement>;
  // Variant editor child
  @ViewChild(VariantEditorComponent) variantEditor?: VariantEditorComponent;

  webcamStream: MediaStream | null = null;
  webcamActive = false;
  selectedFiles: File[] = []; // Changed to array for multiple files
  selectedFileIndex = 0; // Current selected file for detection
  detectionResult: any = null;
  resultImage: string = '';
  loading = false;
  loadingStatus = '';
  batchProgress = 0;
  batchTotal = 0;
  detectingAll = false;
  suggestionLoading = false;
  error = '';
  dragOver = false;
  uploadingImages = false; // Track image upload progress

  // Annotation state
  annotationBox: { x: number; y: number; w: number; h: number } | null = null;
  drawing = false;
  resizing = false;
  resizeHandle: 'nw' | 'ne' | 'sw' | 'se' | null = null;
  readonly handleSize = 10; // pixels
  startX = 0;
  startY = 0;
  currentX = 0;
  currentY = 0;
  currentImage: HTMLImageElement | null = null;

  // Fullscreen state
  isFullscreen = false;
  fullscreenSelectionMode = false;
  scaleFactor = 1;
  // Buyer view modal state
  isBuyerViewOpen = false;
  buyerImageDataUrl: string | null = null;
  savingToServer = false;

  // Mobile nav state
  mobileMenuOpen = false;
  currentUser: any = null;

  createdProductId: number | null = null;
  currentDetectionLogId: number | null = null;

  // Product images for current detection
  productImages: ProductImage[] = [];

  // Detection results per image (for individual saving)
  imageDetectionResults: any[] = [];
  batchSharedDetectionInfo: any = null;

  // Real-time detection properties
  realtimeMode = false;
  realtimeDetectionActive = false;
  captureInterval: any = null;
  captureIntervalMs = 1500; // Capturar cada 1.5 segundos
  realtimeResults: any[] = [];
  lastFrameTime = Date.now();
  frameCount = 0;
  fps = 0;
  realtimeCanvas: HTMLCanvasElement | null = null;
  realtimeCtx: CanvasRenderingContext2D | null = null;

  // Corpus detector properties
  useCorpusModel = true; // Default to trained model
  corpusStatus: any = null;

  constructor(
    private detectionService: DetectionService,
    private productService: ProductService,
    private authService: AuthService,
    private detectionLogService: DetectionLogService,
    private productImageService: ProductImageService,
    private router: Router
  ) { }
  success = '';

  ngOnInit(): void {
    this.checkWebcamSupport();
    this.checkCorpusStatus();
    this.authService.currentUser$.subscribe(user => this.currentUser = user);
  }

  prefillVariantsFromDetection(result: any): void {
    if (!this.variantEditor) return;
    const rawColors = result.colors || result.color || '';
    // split common separators
    const colors = (rawColors || '').split(/[,\/|]+/).map((s: string) => s.trim()).filter((s: string) => s.length > 0);
    if (colors.length > 0) {
      this.variantEditor.prefillColors(colors);
    }
    // also fill product_name and brand
    const name = result.name || result.product_name || '';
    const brand = result.brand || result.detection_class || '';
    if (name) this.variantEditor.form.get('product_name')?.setValue(name);
    if (brand) this.variantEditor.form.get('brand')?.setValue(brand);
  }

  checkCorpusStatus(): void {
    this.detectionService.getCorpusStatus().subscribe({
      next: (status) => {
        this.corpusStatus = status;
        console.log('Corpus detector status:', status);
      },
      error: (err) => {
        console.error('Failed to check corpus status:', err);
        this.corpusStatus = { available: false, error: 'Failed to check status' };
      }
    });
  }

  checkWebcamSupport(): void {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      this.error = 'Webcam not supported in this browser';
    }
  }

  startWebcam(): void {
    navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment',
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    }).then(stream => {
      this.webcamStream = stream;
      this.webcamActive = true;
      setTimeout(() => {
        if (this.webcamElement) {
          this.webcamElement.nativeElement.srcObject = stream;
        }
      }, 100);
    }).catch(err => {
      this.error = 'Failed to access webcam: ' + err.message;
    });
  }

  captureFrame(): void {
    if (!this.webcamElement || !this.canvasElement) return;

    const video = this.webcamElement.nativeElement;
    const canvas = this.canvasElement.nativeElement;
    const ctx = canvas.getContext('2d');

    if (ctx && video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);

      canvas.toBlob(blob => {
        if (blob) {
          const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' });
          this.selectedFiles.push(file);
          if (this.selectedFiles.length === 1) {
            this.selectedFileIndex = 0;
          }
          this.selectFileForDetection(this.selectedFiles.length - 1);
        }
      }, 'image/jpeg');
    }
  }

  stopWebcam(): void {
    if (this.webcamStream) {
      this.webcamStream.getTracks().forEach(track => track.stop());
      this.webcamStream = null;
    }
    this.webcamActive = false;
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = false;
  }

  onUploadZoneClick(): void {
    this.fileInput.nativeElement.click();
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = false;

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.addFiles(files);
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.addFiles(input.files);
    }
  }

  detectFromUpload(): void {
    const currentFile = this.getCurrentFile();
    if (!currentFile) return;

    this.loading = true;
    this.loadingStatus = '📥 Uploading and processing image...';
    this.error = '';

    // Use Corpus model if selected
    const detectionService = this.useCorpusModel ?
      this.detectionService.detectWithCorpus(currentFile) :
      this.detectionService.detectFromImage(currentFile);

    detectionService.subscribe({
      next: (result) => {
        this.loadingStatus = '✅ Detection complete!';
        this.detectionResult = result;
        console.debug('Detection result (backend payload):', result);
        this.currentDetectionLogId = result.metadata?.detection_id || null;
        // Prefer annotated image returned by backend when available
        const annotated = result.annotated_image_url || result.annotated_image || result.metadata?.annotated_image_url;
        if (annotated) {
          this.resultImage = annotated.startsWith('http') ? annotated : (window.location.origin + annotated);
        } else {
          this.resultImage = result.image_url || result.metadata?.image_url || URL.createObjectURL(currentFile);
        }

        // Store detection results for current image and preserve per-image state
        this.imageDetectionResults[this.selectedFileIndex] = {
          ...result,
          saved: false,
          processedAt: new Date(),
          metadata: {
            ...result.metadata,
            annotation_box: this.annotationBox
          }
        };
        this.setBatchSharedDetectionInfo(result);

        // Load product images if product exists
        if (result.metadata?.product_id) {
          this.loadProductImages(result.metadata.product_id);
        } else {
          this.productImages = []; // Clear if no existing product
        }

        setTimeout(() => {
          this.setAnnotationCanvas();
          if (result.bbox) {
            this.drawBoundingBox(result.bbox);
          }
          // Prefill variant editor if present
          try {
            this.prefillVariantsFromDetection(result);
          } catch (e) {
            console.debug('prefillVariantsFromDetection error', e);
          }
        }, 100);

        this.loading = false;
        this.loadingStatus = '';
      },
      error: (err) => {
        console.error('Detection error response:', err);
        this.error = err.error?.detail || err.message || 'Detection failed';
        this.loading = false;
        this.loadingStatus = '';
      }
    });
  }

  // openManualDetectionDialog removed — manual selection dialog deprecated

  async detectAllFromUpload(): Promise<void> {
    if (this.selectedFiles.length === 0) {
      return;
    }

    this.loading = true;
    this.detectingAll = true;
    this.error = '';
    this.batchProgress = 0;
    this.batchTotal = this.selectedFiles.length;

    const currentIndex = this.selectedFileIndex;
    const failedFiles: string[] = [];

    for (let i = 0; i < this.selectedFiles.length; i++) {
      const file = this.selectedFiles[i];

      try {
        const result = await firstValueFrom(this.detectionService.detectFromImage(file, this.useCorpusModel));
        const annotatedUrl = result.annotated_image_url || result.annotated_image || result.metadata?.annotated_image_url;
        this.imageDetectionResults[i] = {
          ...result,
          saved: false,
          processedAt: new Date(),
          metadata: {
            ...result.metadata,
            annotation_box: null,
            annotated_image_url: annotatedUrl || result.metadata?.annotated_image_url || null
          }
        };
        this.batchProgress = i + 1;
      } catch (err: any) {
        console.error('Batch detection failed on file:', file.name, err);
        failedFiles.push(file.name);
        this.batchProgress = i + 1;
        continue;
      }
    }

    this.loading = false;
    this.detectingAll = false;

    if (this.selectedFiles[currentIndex] && this.imageDetectionResults[currentIndex]) {
      this.selectedFileIndex = currentIndex;
      this.detectionResult = { ...this.imageDetectionResults[currentIndex] };
      this.resultImage = URL.createObjectURL(this.selectedFiles[currentIndex]);
      this.annotationBox = this.detectionResult.metadata?.annotation_box || null;
      setTimeout(() => {
        this.setAnnotationCanvas();
        if (this.detectionResult.metadata?.bbox) {
          this.drawBoundingBox(this.detectionResult.metadata.bbox);
        }
      }, 100);
    }

    if (failedFiles.length > 0) {
      this.error = `Detección completada con errores en: ${failedFiles.join(', ')}`;
    } else {
      this.error = '';
    }

    if (this.batchProgress === this.batchTotal) {
      this.setBatchSharedDetectionInfo(this.imageDetectionResults[0]);
    }
  }

  saveDetection(): void {
    if (!this.detectionResult || this.selectedFiles.length === 0) return;

    // Get image URL from detection metadata
    const imageUrl = this.detectionResult.metadata?.image_url || null;

    if (!this.isSizeValid(this.detectionResult.size)) {
      this.error = 'La talla debe ser un valor numérico entre 0 y 50.';
      return;
    }

    if (this.detectionResult.price !== null && this.detectionResult.price !== undefined && !this.isPriceValid(this.detectionResult.price)) {
      this.error = 'El precio debe ser mínimo 10.000 COP.';
      return;
    }

    const priceValue = this.normalizePrice(this.detectionResult.price);

    const productName = this.detectionResult.name?.trim();
    const productData = {
      name: productName && productName.length > 0
        ? productName
        : `${this.detectionResult.brand} - ${this.detectionResult.color}`,
      brand: this.detectionResult.brand,
      color_primary: this.detectionResult.color,
      color_rgb: this.detectionResult.rgb,
      size: this.detectionResult.size,
      stock: 1,
      price: priceValue,
      yolo_confidence: this.detectionResult.confidence,
      detected_text: this.detectionResult.text,
      detection_metadata: this.detectionResult.metadata,
      image_url: imageUrl  // Auto-link detection image
    };

    this.productService.createProduct(productData).subscribe({
      next: (created) => {
        this.createdProductId = created.id;

        // Upload all selected images to the product
        if (this.selectedFiles.length > 0) {
          this.productImageService.uploadBatchImages(created.id, this.selectedFiles).subscribe({
            next: (_uploadResult) => {
              this.error = '';

              // If image_url was auto-linked and we have annotation, add annotation
              if (imageUrl && this.annotationBox) {
                const annotation = {
                  x1: this.annotationBox.x,
                  y1: this.annotationBox.y,
                  x2: this.annotationBox.x + this.annotationBox.w,
                  y2: this.annotationBox.y + this.annotationBox.h,
                  class_name: this.detectionResult.brand || 'Other_Shoe'
                };

                this.productService.annotateProductImage(created.id, annotation).subscribe({
                  next: () => {
                    alert(`✅ Producto guardado con ${this.selectedFiles.length} imagen(es) y anotación ¡listo!`);
                    this.loadProductImages(created.id);
                    this.clearResults();
                  },
                  error: (err) => {
                    this.error = 'Error al anotar producto: ' + (err.error?.detail || err.message);
                  }
                });
              } else {
                alert(`✅ Producto guardado con ${this.selectedFiles.length} imagen(es) ¡listo!`);
                this.loadProductImages(created.id);
                this.clearResults();
              }
            },
            error: (err) => {
              this.error = 'Error al subir imágenes: ' + (err.error?.detail || err.message);
            }
          });
        } else {
          alert('Producto guardado pero sin imágenes.');
          this.loadProductImages(created.id);
          this.clearResults();
        }
      },
      error: (err) => {
        this.error = 'Error al crear producto: ' + (err.error?.detail || err.message);
      }
    });
  }

  // Save detection results for current image only (individual saving)
  saveCurrentImageDetection(): void {
    if (!this.detectionResult || this.selectedFiles.length === 0) {
      this.error = 'No hay resultados de detección para guardar';
      return;
    }

    const currentImageIndex = this.selectedFileIndex;

    if (!this.isSizeValid(this.detectionResult.size)) {
      this.error = 'La talla debe ser un valor numérico entre 0 y 50.';
      return;
    }

    if (this.detectionResult.price !== null && this.detectionResult.price !== undefined && !this.isPriceValid(this.detectionResult.price)) {
      this.error = 'El precio debe ser mínimo 10.000 COP.';
      return;
    }

    // Save result locally for this image only
    this.detectionResult = {
      ...this.detectionResult,
      saved: true,
      metadata: {
        ...this.detectionResult.metadata,
        annotation_box: this.annotationBox
      }
    };

    this.imageDetectionResults[currentImageIndex] = {
      ...this.detectionResult,
      saved: true,
      savedAt: new Date()
    };

    this.setBatchSharedDetectionInfo(this.imageDetectionResults[currentImageIndex]);
    this.propagateSharedInfoToOtherImages(currentImageIndex);

    this.error = '';
    alert(`✅ Resultados guardados localmente para imagen ${currentImageIndex + 1}`);
  }

  // Save complete product with all processed images
  saveCompleteProduct(): void {
    if (this.selectedFiles.length === 0) {
      this.error = 'No hay imágenes para crear el producto';
      return;
    }

    // Check if at least one image has detection results and is saved
    const savedCount = this.imageDetectionResults
      .filter((result: any) => result?.saved).length;

    if (savedCount === 0) {
      this.error = 'Debes guardar al menos un resultado de detección antes de crear el producto';
      return;
    }

    // Use the most recently saved result as base
    const savedResults = this.imageDetectionResults.filter((result: any) => result?.saved);
    if (savedResults.length === 0) {
      this.error = 'No hay resultados de detección guardados disponibles';
      return;
    }

    const baseResult = savedResults[savedResults.length - 1];

    // Validate Brand - Required
    if (!baseResult.brand || baseResult.brand.trim().length === 0) {
      this.error = 'El campo "Brand" es requerido para crear el producto.';
      return;
    }

    if (!this.isSizeValid(baseResult.size)) {
      this.error = 'La talla debe ser un valor numérico entre 0 y 50.';
      return;
    }

    if (baseResult.price !== null && baseResult.price !== undefined && !this.isPriceValid(baseResult.price)) {
      this.error = 'El precio debe ser mínimo 10.000 COP.';
      return;
    }

    const priceValue = this.normalizePrice(baseResult.price);

    const productName = baseResult.name?.trim();
    const safeSavedResults = savedResults.map((item: any) => ({
      ...item,
      metadata: {
        ...item.metadata,
        annotation_box: item.metadata?.annotation_box || null
      }
    }));

    const productData = {
      name: productName && productName.length > 0
        ? productName
        : `${baseResult.brand} - ${baseResult.colors || baseResult.color} (Completo)`,
      brand: baseResult.brand,
      colors: baseResult.colors || baseResult.color || '',
      color_rgb: baseResult.rgb || { r: 0, g: 0, b: 0 },
      size: baseResult.size,
      stock: 1,
      price: priceValue,
      yolo_confidence: baseResult.confidence || 0.5,
      detected_text: baseResult.text || '',
      detection_metadata: {
        ...baseResult.metadata,
        batch_images: this.selectedFiles.length,
        individual_results: safeSavedResults
      }
    };

    console.log('✓ Validaciones completadas. Enviando producto al backend:', productData);
    this.loading = true;
    this.uploadingImages = true;

    this.productService.createProduct(productData).subscribe({
      next: (created) => {
        console.log('✓ Producto creado exitosamente con ID:', created.id);
        this.createdProductId = created.id;
        this.uploadingImages = true;

        // Upload all images with their detection results
        if (this.selectedFiles.length > 0) {
          this.productImageService.uploadBatchImages(created.id, this.selectedFiles).subscribe({
            next: (_uploadResult) => {
              this.uploadingImages = false;
              this.loading = false;
              this.error = '';
              console.log('✓ Imágenes subidas exitosamente');

              // Link detection logs to product images
              this.linkDetectionLogsToProduct(created.id);

              const savedCount = this.imageDetectionResults
                .filter((result: any) => result?.saved).length;
              alert(`✅ Producto completo guardado con ${this.selectedFiles.length} imagen(es) y ${savedCount} resultados de detección ¡listo!`);
              this.loadProductImages(created.id);
              this.clearResults();
            },
            error: (err) => {
              this.uploadingImages = false;
              this.loading = false;
              console.error('✗ Error al subir imágenes:', err);
              const errorMsg = err.error?.detail || err.statusText || err.message || 'Error desconocido al subir imágenes';
              this.error = 'Error al subir imágenes: ' + errorMsg;
            }
          });
        }
      },
      error: (err) => {
        this.loading = false;
        this.uploadingImages = false;
        console.error('✗ Error al crear producto:', err);
        let errorMsg = 'Error desconocido al crear producto';

        // Manejo de diferentes tipos de errores
        if (err.status === 0) {
          errorMsg = 'No hay conexión con el servidor. Verifica que el backend esté corriendo.';
        } else if (err.error?.detail) {
          errorMsg = typeof err.error.detail === 'string' 
            ? err.error.detail 
            : JSON.stringify(err.error.detail, null, 2);
        } else if (err.error?.message) {
          errorMsg = err.error.message;
        } else if (err.message) {
          errorMsg = err.message;
        } else if (typeof err.error === 'string') {
          errorMsg = err.error;
        }

        this.error = 'Error al crear producto completo: ' + errorMsg;
        console.error('Mensaje de error final:', this.error);
      }
    });
  }

  // Link saved detection logs to product images
  private linkDetectionLogsToProduct(productId: number): void {
    Object.entries(this.imageDetectionResults).forEach(([_imageIndex, result]) => {
      if (result.detectionLogId) {
        // Update the detection log to link it to the product
        this.detectionLogService.updateDetectionLog(result.detectionLogId, {
          product_id: productId
        }).subscribe({
          next: () => {
            console.log(`Linked detection log ${result.detectionLogId} to product ${productId}`);
          },
          error: (err) => {
            console.error(`Error linking detection log ${result.detectionLogId}:`, err);
          }
        });
      }
    });
  }

  // Get count of processed images
  getProcessedImagesCount(): number {
    return this.imageDetectionResults.filter((result: any) => !!result).length;
  }

  // Get count of images the user has saved locally
  getSavedImagesCount(): number {
    return this.imageDetectionResults.filter((result: any) => result?.saved).length;
  }

  isPriceValid(value: any): boolean {
    const price = Number(value);
    return !isNaN(price) && price >= 10000;
  }

  isSizeValid(value: any): boolean {
    if (value === null || value === undefined || value === '') {
      return false;
    }
    const size = Number(value);
    return !isNaN(size) && size >= 0 && size <= 50;
  }

  normalizePrice(value: any): number | null {
    if (value === null || value === undefined || value === '') {
      return null;
    }
    const price = Number(value);
    return isNaN(price) ? null : price;
  }

  formatConfidence(): string {
    const conf = this.detectionResult?.confidence ?? this.detectionResult?.metadata?.confidence;
    if (conf === null || conf === undefined) return 'N/A';
    const perc = Math.round(Number(conf) * 100);
    return `${perc}%`;
  }

  clearResults(): void {
    this.detectionResult = null;
    this.currentDetectionLogId = null;
    this.resultImage = '';
    this.selectedFiles = []; // Clear all files
    this.selectedFileIndex = 0;
    this.annotationBox = null;
    this.drawing = false;
    this.productImages = []; // Clear product images
    this.imageDetectionResults = []; // Clear individual results
    if (this.annotationCanvas) {
      const ctx = this.annotationCanvas.nativeElement.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, this.annotationCanvas.nativeElement.width, this.annotationCanvas.nativeElement.height);
      }
    }
  }

  // Multi-file management methods
  addFiles(files: FileList): void {
    const maxFiles = 10;
    const currentCount = this.selectedFiles.length;
    const hadNoFiles = currentCount === 0;
    const availableSlots = maxFiles - currentCount;

    if (availableSlots <= 0) {
      this.error = 'Maximum 10 images allowed';
      return;
    }

    const filesToAdd = Math.min(files.length, availableSlots);
    for (let i = 0; i < filesToAdd; i++) {
      const file = files[i];
      // Validate file type
      if (!file.type.match('image/(jpeg|jpg|png|webp)')) {
        continue; // Skip invalid files
      }
      this.selectedFiles.push(file);
    }

    if (hadNoFiles && this.selectedFiles.length > 0) {
      this.selectFileForDetection(0);
    } else if (this.selectedFiles.length > 0 && this.selectedFileIndex >= this.selectedFiles.length) {
      this.selectedFileIndex = 0;
    }

    this.error = '';
  }

  removeFile(index: number): void {
    if (index >= 0 && index < this.selectedFiles.length) {
      this.selectedFiles.splice(index, 1);
      this.imageDetectionResults.splice(index, 1);

      // Adjust selected index if necessary
      if (this.selectedFileIndex >= this.selectedFiles.length && this.selectedFiles.length > 0) {
        this.selectedFileIndex = this.selectedFiles.length - 1;
        this.loadCurrentSelectionState();
      } else if (this.selectedFiles.length === 0) {
        this.selectedFileIndex = 0;
        this.clearResults();
      }
    }
  }

  selectFileForDetection(index: number): void {
    if (index >= 0 && index < this.selectedFiles.length) {
      this.persistCurrentImageResult();

      this.selectedFileIndex = index;
      this.resultImage = URL.createObjectURL(this.selectedFiles[index]);

      // Load saved detection results for this image if available
      if (this.imageDetectionResults[index]) {
        this.detectionResult = { ...this.imageDetectionResults[index] };
        this.annotationBox = this.detectionResult.metadata?.annotation_box || null;
      } else if (this.batchSharedDetectionInfo) {
        this.imageDetectionResults[index] = {
          ...this.batchSharedDetectionInfo,
          saved: false,
          metadata: {
            annotation_box: null
          }
        };
        this.detectionResult = { ...this.imageDetectionResults[index] };
        this.annotationBox = null;
      } else {
        this.detectionResult = {
          saved: false,
          metadata: {
            annotation_box: null
          }
        } as any;
        this.annotationBox = null;
      }

      // Reset canvas
      setTimeout(() => {
        this.setAnnotationCanvas();
      }, 100);
    }
  }

  private persistCurrentImageResult(): void {
    if (this.selectedFiles.length === 0 || !this.detectionResult) {
      return;
    }

    this.imageDetectionResults[this.selectedFileIndex] = {
      ...this.detectionResult,
      metadata: {
        ...this.detectionResult.metadata,
        annotation_box: this.annotationBox
      }
    };
  }

  private loadCurrentSelectionState(): void {
    const index = this.selectedFileIndex;
    if (this.imageDetectionResults[index]) {
      this.detectionResult = { ...this.imageDetectionResults[index] };
      this.annotationBox = this.detectionResult.metadata?.annotation_box || null;
      this.resultImage = URL.createObjectURL(this.selectedFiles[index]);
      setTimeout(() => this.setAnnotationCanvas(), 100);
    } else {
      this.detectionResult = null;
      this.annotationBox = null;
      this.resultImage = '';
    }
  }

  private setBatchSharedDetectionInfo(result: any): void {
    if (!result) {
      return;
    }

    this.batchSharedDetectionInfo = {
      brand: result.brand,
      color: result.color,
      rgb: result.rgb,
      size: result.size,
      price: result.price,
      text: result.text,
      confidence: result.confidence
    };
  }

  private propagateSharedInfoToOtherImages(sourceIndex: number): void {
    if (!this.batchSharedDetectionInfo) {
      return;
    }

    this.imageDetectionResults = this.imageDetectionResults.map((result: any, index: number) => {
      if (index === sourceIndex || !result) {
        return result;
      }

      return {
        ...result,
        ...this.batchSharedDetectionInfo,
        metadata: {
          ...result.metadata,
          annotation_box: result.metadata?.annotation_box || null
        }
      };
    });
  }

  getCurrentFile(): File | null {
    return this.selectedFiles.length > 0 && this.selectedFileIndex < this.selectedFiles.length
      ? this.selectedFiles[this.selectedFileIndex]
      : null;
  }

  getSuggestedColors(): string[] {
    const raw = this.detectionResult?.colors || this.detectionResult?.color || '';
    if (!raw) return [];
    return (raw as string).split(/[,\/|]+/).map(s => s.trim()).filter(s => s.length > 0);
  }

  onVariantFormChange(payload: any): void {
    // When user edits variants, we may want to sync some fields back to detectionResult
    // Keep it minimal: update detectionResult.name and brand if present
    if (!payload) return;
    if (payload.product_name) {
      this.detectionResult = { ...this.detectionResult, name: payload.product_name };
    }
    if (payload.brand) {
      this.detectionResult = { ...this.detectionResult, brand: payload.brand };
    }
  }

  loadProductImages(productId: number): void {
    this.productImageService.getProductImages(productId).subscribe({
      next: (response) => {
        if (response.images && response.images.length > 0) {
          this.productImages = response.images;
          console.log(`✅ Loaded ${this.productImages.length} images for product ${productId}`);
          console.log('Product images:', this.productImages.map(i => i.image_url));
        } else {
          this.productImages = [];
        }
      },
      error: (err) => {
        console.error('Error loading product images:', err);
        this.productImages = [];
      }
    });
  }

  drawBoundingBox(bbox: number[]): void {
    if (!this.annotationCanvas) return;

    let x = bbox[0];
    let y = bbox[1];
    let width = bbox[2] - bbox[0];
    let height = bbox[3] - bbox[1];

    if (width < 0) { x += width; width = Math.abs(width); }
    if (height < 0) { y += height; height = Math.abs(height); }

    this.annotationBox = { x, y, w: width, h: height };
    this.redrawAnnotationCanvas();
  }

  redrawAnnotationCanvas(): void {
    if (!this.annotationCanvas) return;

    const canvas = this.annotationCanvas.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Dibujar solo la selección (el fondo queda en <img>)
    if (this.annotationBox) {
      ctx.strokeStyle = '#ff0000';
      ctx.lineWidth = 2.5;
      ctx.strokeRect(this.annotationBox.x, this.annotationBox.y, this.annotationBox.w, this.annotationBox.h);

      ctx.fillStyle = 'rgba(255, 0, 0, 0.2)';
      ctx.fillRect(this.annotationBox.x, this.annotationBox.y, this.annotationBox.w, this.annotationBox.h);

      ctx.fillStyle = '#ff0000';
      ctx.font = '14px Arial';
      // Always show a stable title for the selection box
      ctx.fillText('Current Selection', Math.max(5, this.annotationBox.x), Math.max(20, this.annotationBox.y - 8));

      this.annotationBox = {
        x: Math.max(0, this.annotationBox.x),
        y: Math.max(0, this.annotationBox.y),
        w: Math.max(1, Math.min(this.annotationBox.w, canvas.width - this.annotationBox.x)),
        h: Math.max(1, Math.min(this.annotationBox.h, canvas.height - this.annotationBox.y))
      };
    
      // Draw resize handles
      const hs = this.handleSize;
      const handles = [
        { x: this.annotationBox.x - hs, y: this.annotationBox.y - hs, name: 'nw' },
        { x: this.annotationBox.x + this.annotationBox.w - hs, y: this.annotationBox.y - hs, name: 'ne' },
        { x: this.annotationBox.x - hs, y: this.annotationBox.y + this.annotationBox.h - hs, name: 'sw' },
        { x: this.annotationBox.x + this.annotationBox.w - hs, y: this.annotationBox.y + this.annotationBox.h - hs, name: 'se' }
      ];
      ctx.fillStyle = '#ffffff';
      ctx.strokeStyle = '#ff0000';
      handles.forEach(h => {
        ctx.lineWidth = 1;
        ctx.fillRect(h.x, h.y, hs * 2, hs * 2);
        ctx.strokeRect(h.x, h.y, hs * 2, hs * 2);
      });
    }
  }

  // Draw detections returned by backend on the live webcam canvas.
  // Backend resizes images with max dimension 640; compute scale back to video size.
  drawRealtimeBoxes(detections: any[]): void {
    if (!this.canvasElement || !this.webcamElement) return;
    const canvas = this.canvasElement.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const video = this.webcamElement.nativeElement;
    const vidW = video.videoWidth || canvas.width || 640;
    const vidH = video.videoHeight || canvas.height || 480;

    // Clear previous overlay (video image is re-drawn elsewhere)
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Estimate backend resize: max dimension -> 640 (backend uses ImageProcessingService.resize_image with max_size=640)
    const maxDim = Math.max(vidW, vidH);
    const scale = maxDim > 640 ? 640 / maxDim : 1.0;
    const resizedW = Math.max(1, Math.round(vidW * scale));
    const resizedH = Math.max(1, Math.round(vidH * scale));

    const ratioX = vidW / resizedW;
    const ratioY = vidH / resizedH;

    // draw translucent overlay
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 2;
    ctx.fillStyle = 'rgba(0,255,0,0.12)';

    console.debug('Video size:', vidW, vidH, 'resized:', resizedW, resizedH, 'ratios:', ratioX.toFixed(2), ratioY.toFixed(2));

    detections.forEach(det => {
      const bbox = det.bbox || det.metadata?.bbox || null;
      if (!bbox) return;
      let x = bbox[0] * ratioX;
      let y = bbox[1] * ratioY;
      let w = (bbox[2] - bbox[0]) * ratioX;
      let h = (bbox[3] - bbox[1]) * ratioY;
      if (w < 0) { x += w; w = Math.abs(w); }
      if (h < 0) { y += h; h = Math.abs(h); }
      ctx.beginPath();
      ctx.strokeRect(x, y, w, h);
      ctx.fillRect(x, y, w, h);
      // label
      ctx.fillStyle = '#00FF00';
      ctx.font = '14px Arial';
      const label = `${det.class || det.detection_class || 'obj'} ${Number(det.confidence || 0).toFixed(2)}`;
      ctx.fillText(label, Math.max(5, x), Math.max(14, y - 6));
    });
  }

  setAnnotationCanvas(): void {
    if (!this.annotationCanvas || !this.resultImage) return;

    const canvas = this.annotationCanvas.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const image = new Image();
    image.onload = () => {
      this.currentImage = image;
      canvas.width = image.width;
      canvas.height = image.height;
      canvas.style.width = '100%';
      canvas.style.height = '100%';
      canvas.style.maxWidth = '100%';
      canvas.style.maxHeight = '100%';
      canvas.style.display = 'block';

      this.redrawAnnotationCanvas();
    };

    image.onerror = () => {
      console.error('Error loading annotation image');
      this.error = 'Error loading image for annotation';
    };

    image.src = this.resultImage;
  }

  openBuyerView(): void {
    if (!this.resultImage) {
      this.error = 'No image available for buyer view';
      return;
    }
    // generate annotated preview and open modal
    this.generateAnnotatedImage().then((dataUrl) => {
      this.buyerImageDataUrl = dataUrl;
      this.isBuyerViewOpen = true;
    }).catch(err => {
      console.error('Failed to generate annotated image:', err);
      this.error = 'Failed to prepare buyer preview';
    });
  }

  closeBuyerView(): void {
    this.isBuyerViewOpen = false;
    this.buyerImageDataUrl = null;
  }

  async generateAnnotatedImage(): Promise<string> {
    return new Promise<string>((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        try {
          const canvas = document.createElement('canvas');
          canvas.width = img.width;
          canvas.height = img.height;
          const ctx = canvas.getContext('2d');
          if (!ctx) throw new Error('No 2d context');
          ctx.drawImage(img, 0, 0);

          // draw annotation box if available
          if (this.annotationBox) {
            ctx.strokeStyle = '#ff0000';
            ctx.lineWidth = Math.max(2, Math.round(Math.max(canvas.width, canvas.height) / 320));
            ctx.fillStyle = 'rgba(255,0,0,0.15)';
            ctx.fillRect(this.annotationBox.x, this.annotationBox.y, this.annotationBox.w, this.annotationBox.h);
            ctx.strokeRect(this.annotationBox.x, this.annotationBox.y, this.annotationBox.w, this.annotationBox.h);

            // label text
            const cls = this.detectionResult?.brand || this.detectionResult?.detection_class || this.detectionResult?.label || 'Object';
            const conf = this.detectionResult?.confidence != null ? Math.round(this.detectionResult.confidence * 100) + '%' : '';
            const label = `${cls}${conf ? ' ' + conf : ''}`;
            ctx.fillStyle = '#00ff00';
            ctx.font = `${Math.max(14, Math.round(canvas.width / 60))}px Arial`;
            ctx.fillText(label, Math.max(5, this.annotationBox.x), Math.max(20, this.annotationBox.y - 8));
          }

          const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
          resolve(dataUrl);
        } catch (e) {
          reject(e);
        }
      };
      img.onerror = (e) => reject(e);
      img.src = this.resultImage as string;
    });
  }

  downloadAnnotatedImage(): void {
    if (!this.buyerImageDataUrl) return;
    const link = document.createElement('a');
    link.href = this.buyerImageDataUrl;
    link.download = 'detection_result_visualized.jpg';
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  async saveProductToServer(): Promise<void> {
    if (!this.variantEditor) {
      this.error = 'Variant editor not available';
      return;
    }
    if (!this.buyerImageDataUrl) {
      this.error = 'Preview image not ready';
      return;
    }

    this.savingToServer = true;
    this.error = '';

    try {
      // Convert dataURL to blob
      const res = await fetch(this.buyerImageDataUrl);
      const blob = await res.blob();
      const file = new File([blob], 'detection_result_visualized.jpg', { type: 'image/jpeg' });

      // Build payload
      const productPayload = this.variantEditor.getValue();
      // Merge detectionResult summary
      productPayload.confidence = this.detectionResult?.confidence ?? 0;
      productPayload.ocr_text = this.detectionResult?.text || this.detectionResult?.detected_text || '';
      productPayload.colors = this.getSuggestedColors();
      productPayload.detection_log_id = this.currentDetectionLogId;  // Link to detection log

      const formData = new FormData();
      formData.append('product_json', JSON.stringify(productPayload));
      formData.append('file', file);

      this.productService.createProductWithImage(formData).subscribe({
        next: (created: any) => {
          this.createdProductId = created?.id ?? null;
          this.success = 'Producto guardado correctamente';
          this.savingToServer = false;
          this.closeBuyerView();
          // Navigate to products list (no detail route exists); keep toast visible briefly
          setTimeout(() => {
            this.success = '';
            this.router.navigate(['/products']);
          }, 900);
        },
        error: (err) => {
          console.error('Save product error', err);
          this.error = err.error?.detail || err.message || 'Error saving product to server';
          this.savingToServer = false;
        }
      });

    } catch (e) {
      console.error('Failed to prepare product payload', e);
      this.error = 'Failed to prepare product payload';
      this.savingToServer = false;
    }
  }

  onCanvasMouseDown(event: MouseEvent): void {
    if (!this.annotationCanvas) return;
    const rect = this.annotationCanvas.nativeElement.getBoundingClientRect();
    const canvas = this.annotationCanvas.nativeElement;

    // Calcular escala entre canvas mostrado y real
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    // Si hay una anotación existente, comprobar si el click cae en un handle de esquina
    if (this.annotationBox) {
      const hb = this.handleSize;
      const handles = {
        nw: { x: this.annotationBox.x - hb, y: this.annotationBox.y - hb },
        ne: { x: this.annotationBox.x + this.annotationBox.w - hb, y: this.annotationBox.y - hb },
        sw: { x: this.annotationBox.x - hb, y: this.annotationBox.y + this.annotationBox.h - hb },
        se: { x: this.annotationBox.x + this.annotationBox.w - hb, y: this.annotationBox.y + this.annotationBox.h - hb }
      };
      for (const h of Object.keys(handles) as Array<keyof typeof handles>) {
        const hx = handles[h].x;
        const hy = handles[h].y;
        if (x >= hx && x <= hx + hb * 2 && y >= hy && y <= hy + hb * 2) {
          this.resizing = true;
          this.resizeHandle = h as any;
          return;
        }
      }
    }

    // Start drawing new annotation
    this.drawing = true;
    this.startX = x;
    this.startY = y;
  }

  onCanvasMouseMove(event: MouseEvent): void {
    if (!this.annotationCanvas) return;

    const rect = this.annotationCanvas.nativeElement.getBoundingClientRect();
    const canvas = this.annotationCanvas.nativeElement;

    // Calcular la escala entre el canvas mostrado y el canvas real
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    if (this.resizing && this.annotationBox && this.resizeHandle) {
      // Ajustar según el handle seleccionado
      let bx = this.annotationBox.x;
      let by = this.annotationBox.y;
      let bw = this.annotationBox.w;
      let bh = this.annotationBox.h;

      if (this.resizeHandle === 'nw') {
        const newX = Math.min(bx + bw - 1, x);
        bw = bw + (bx - newX);
        bx = newX;
      } else if (this.resizeHandle === 'ne') {
        const newW = Math.max(1, x - bx);
        bw = newW;
      } else if (this.resizeHandle === 'sw') {
        const newY = Math.min(by + bh - 1, y);
        bh = bh + (by - newY);
        by = newY;
      } else if (this.resizeHandle === 'se') {
        const newW = Math.max(1, x - bx);
        const newH = Math.max(1, y - by);
        bw = newW;
        bh = newH;
      }

      this.annotationBox = { x: Math.max(0, bx), y: Math.max(0, by), w: Math.max(1, Math.min(bw, canvas.width - bx)), h: Math.max(1, Math.min(bh, canvas.height - by)) };
      this.redrawAnnotationCanvas();
      return;
    }

    if (!this.drawing) return;

    this.currentX = x;
    this.currentY = y;

    this.redrawAnnotationCanvas();

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = this.currentX - this.startX;
    const height = this.currentY - this.startY;

    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    ctx.strokeRect(this.startX, this.startY, width, height);
  }

  onCanvasMouseUp(event: MouseEvent): void {
    if (!this.annotationCanvas) return;

    // Si estábamos redimensionando, terminar redimensionado
    if (this.resizing) {
      this.resizing = false;
      this.resizeHandle = null;
      return;
    }

    if (!this.drawing) return;
    this.drawing = false;

    const rect = this.annotationCanvas.nativeElement.getBoundingClientRect();
    const canvas = this.annotationCanvas.nativeElement;

    // Calcular la escala entre el canvas mostrado y el canvas real
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const endX = (event.clientX - rect.left) * scaleX;
    const endY = (event.clientY - rect.top) * scaleY;

    const x = Math.min(this.startX, endX);
    const y = Math.min(this.startY, endY);
    const w = Math.abs(endX - this.startX);
    const h = Math.abs(endY - this.startY);

    this.annotationBox = { x, y, w, h };
    this.redrawAnnotationCanvas();
  }

  onCanvasMouseLeave(event: MouseEvent): void {
    if (this.drawing) {
      this.onCanvasMouseUp(event);
    }
  }

  clearAnnotation(): void {
    this.annotationBox = null;
    this.redrawAnnotationCanvas();
  }

  adjustWidth(delta: number): void {
    if (!this.annotationBox) return;
    const newW = Math.max(1, this.annotationBox.w + delta);
    this.annotationBox = { ...this.annotationBox, w: newW };
    this.redrawAnnotationCanvas();
  }

  adjustHeight(delta: number): void {
    if (!this.annotationBox) return;
    const newH = Math.max(1, this.annotationBox.h + delta);
    this.annotationBox = { ...this.annotationBox, h: newH };
    this.redrawAnnotationCanvas();
  }

  getSelectionLabel(): string {
    if (!this.annotationBox) return 'Current Selection';

    if (this.detectionResult) {
      const cls = this.detectionResult.class || this.detectionResult.detection_class || this.detectionResult.label || this.detectionResult.brand || this.detectionResult.name || this.detectionResult.metadata?.class;
      const conf = this.detectionResult.confidence ?? this.detectionResult.metadata?.confidence ?? null;
      let label = cls || 'Selection';
      if (conf !== null && conf !== undefined) {
        label = `${label} ${Number(conf).toFixed(2)}`;
      }
      return label;
    }

    return 'Current Selection';
  }

  detectColorFromSelection(): void {
    const currentFile = this.getCurrentFile();
    if (!this.annotationBox || !currentFile) {
      this.error = 'No hay selección o imagen para detectar color';
      return;
    }

    this.loading = true;
    this.error = '';

    // Crear un FormData con la imagen y las coordenadas de la selección
    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('bbox', JSON.stringify([
      this.annotationBox.x,
      this.annotationBox.y,
      this.annotationBox.x + this.annotationBox.w,
      this.annotationBox.y + this.annotationBox.h
    ]));

    this.detectionService.detectColorFromSelection(formData).subscribe({
      next: (result) => {
        this.loading = false;
        // Actualizar el color en detectionResult
        this.detectionResult.color = result.color_name;
        this.detectionResult.rgb = result.rgb;
        this.error = '';
        alert('✅ Color detectado correctamente de la selección');
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Error al detectar color: ' + (err.error?.detail || err.message);
      }
    });
  }

  generateTextSuggestion(): void {
    if (!this.detectionResult) {
      this.error = 'No hay resultados de detección para generar sugerencia';
      return;
    }

    this.suggestionLoading = true;
    this.error = '';

    const formData = new FormData();
    formData.append('ocr_text', this.detectionResult.text || '');
    formData.append('brand', this.detectionResult.brand || '');
    formData.append('color', this.detectionResult.color || '');
    formData.append('size', this.detectionResult.size?.toString() || '');
    const currentFile = this.getCurrentFile();
    if (currentFile) {
      formData.append('file', currentFile);
    }

    this.detectionService.suggestText(formData).subscribe({
      next: (result) => {
        this.suggestionLoading = false;
        this.detectionResult.text = result.suggestion || this.detectionResult.text;
        this.error = '';
      },
      error: (err) => {
        this.suggestionLoading = false;
        this.error = 'Error al generar sugerencia IA: ' + (err.error?.detail || err.message);
      }
    });
  }

  updateDetectionResults(): void {
    if (!this.detectionResult || !this.currentDetectionLogId) {
      this.error = 'No hay resultados de detección para actualizar';
      return;
    }

    this.loading = true;
    this.error = '';

    const updates: any = {
      detected_brand: this.detectionResult.brand,
      detected_color: this.detectionResult.color,
      detected_size: this.detectionResult.size,
      detected_text: this.detectionResult.text
    };

    // Si hay un RGB actualizado, incluirlo en los metadatos
    if (this.detectionResult.rgb) {
      updates['detection_metadata'] = {
        ...this.detectionResult.metadata,
        rgb: this.detectionResult.rgb
      };
    }

    this.detectionLogService.updateDetectionLog(this.currentDetectionLogId, updates).subscribe({
      next: () => {
        this.loading = false;
        this.error = '';
        alert('✅ Resultados de detección actualizados correctamente');
        // Update local detectionResult with the updated values
        this.detectionResult = {
          ...this.detectionResult,
          ...updates
        };
        this.setBatchSharedDetectionInfo(this.detectionResult);
        this.propagateSharedInfoToOtherImages(this.selectedFileIndex);
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Error al actualizar resultados: ' + (err.error?.detail || err.message);
      }
    });
  }

  logout(): void {
    this.authService.logout();
  }

  // ============================================================================
  // REAL-TIME DETECTION METHODS
  // ============================================================================

  startRealtimeDetection(): void {
    if (this.realtimeDetectionActive) return;

    this.realtimeMode = true;
    this.realtimeDetectionActive = true;
    this.realtimeResults = [];
    this.frameCount = 0;
    this.lastFrameTime = Date.now();

    // Start WebSocket connection for real-time detection
    this.detectionService.startRealtimeDetection().subscribe({
      next: (result) => {
        if (result.detections && result.detections.length > 0) {
          // Process successful detection results
          const detection = result.detections[0]; // Use first/best detection

          // Add to results history
          this.realtimeResults.unshift({
            timestamp: new Date(),
            brand: detection.brand,
            color: detection.color,
            size: detection.size,
            text: detection.text,
            confidence: detection.confidence,
            price: detection.price,
            rgb: detection.rgb,
            bbox: detection.bbox,
            processing_time: result.processing_time,
            fps: result.fps
          });

          // Keep only last 10 results
          if (this.realtimeResults.length > 10) {
            this.realtimeResults.pop();
          }

          // Show latest result as current
          this.detectionResult = {
            brand: detection.brand,
            color: detection.color,
            size: detection.size,
            text: detection.text,
            confidence: detection.confidence,
            price: detection.price,
            rgb: detection.rgb,
            bbox: detection.bbox,
            processing_time: result.processing_time
          };
        } else {
          // No detections found
          this.detectionResult = null;
        }

        // Update FPS display
        if (result.fps) {
          this.fps = result.fps;
        }
      },
      error: (err) => {
        console.error('Real-time detection WebSocket error:', err);
        this.error = 'Real-time detection connection failed';
        this.stopRealtimeDetection();
      }
    });

    // Iniciar webcam si no está activa
    if (!this.webcamActive) {
      navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      }).then(stream => {
        this.webcamStream = stream;
        this.webcamActive = true;
        setTimeout(() => {
          if (this.webcamElement) {
            this.webcamElement.nativeElement.srcObject = stream;
            this.beginRealtimeCapture();
          }
        }, 500);
      }).catch(err => {
        this.error = 'Failed to access webcam: ' + err.message;
        this.realtimeDetectionActive = false;
        this.detectionService.stopRealtimeDetection();
      });
    } else {
      this.beginRealtimeCapture();
    }
  }

  beginRealtimeCapture(): void {
    // Capturar frames automáticamente
    this.captureInterval = setInterval(() => {
      this.captureRealtimeFrame();
    }, this.captureIntervalMs);
  }

  captureRealtimeFrame(): void {
    if (!this.webcamElement || !this.canvasElement || !this.realtimeDetectionActive) return;

    const video = this.webcamElement.nativeElement;
    const canvas = this.canvasElement.nativeElement;
    const ctx = canvas.getContext('2d');

    if (ctx && video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);

      canvas.toBlob(blob => {
        if (blob) {
          const file = new File([blob], 'realtime-frame.jpg', { type: 'image/jpeg' });
          this.performRealtimeDetection(file);
        }
      }, 'image/jpeg');

      // Actualizar FPS
      this.frameCount++;
      const now = Date.now();
      const elapsed = (now - this.lastFrameTime) / 1000;
      if (elapsed >= 1) {
        this.fps = this.frameCount / elapsed;
        this.frameCount = 0;
        this.lastFrameTime = now;
      }
    }
  }

  performRealtimeDetection(file: File): void {
    // Use Corpus real-time detection endpoint
    this.detectionService.detectCorpusRealtime(file).subscribe({
      next: (result) => {
        console.debug('Realtime detection response:', result);
        if (result.detections && result.detections.length > 0) {
          // Process successful detection results
          const detection = result.detections[0]; // Use first/best detection

          // Map Corpus classes to display format
          const classMapping: { [key: string]: string } = {
            'marca': 'Nike',
            'shoe': 'Adidas',
            'texto': 'Generic Brand'
          };

          // Add to results history
          this.realtimeResults.unshift({
            timestamp: new Date(),
            brand: classMapping[detection.class as string] || detection.class,
            color: 'Detected',
            size: 'Auto',
            text: detection.class,
            confidence: detection.confidence,
            price: null,
            rgb: null,
            bbox: detection.bbox,
            processing_time: Date.now(),
            fps: this.fps
          });

          // Keep only last 10 results
          if (this.realtimeResults.length > 10) {
            this.realtimeResults.pop();
          }

          // Show latest result as current
          this.detectionResult = {
            brand: classMapping[detection.class as string] || detection.class,
            color: 'Detected',
            size: 'Auto',
            text: detection.class,
            confidence: detection.confidence,
            price: null,
            rgb: null,
            bbox: detection.bbox,
            processing_time: Date.now()
          };
          // Draw boxes on the live webcam canvas (scale from backend resize)
          try {
            this.drawRealtimeBoxes(result.detections || []);
          } catch (err) {
            console.error('Error drawing realtime boxes:', err);
          }
        } else {
          // No detections found
          this.detectionResult = null;
        }
      },
      error: (err) => {
        console.error('Real-time Corpus detection error:', err);
        // Don't show error for real-time detection to avoid spam
      }
    });
  }

  stopRealtimeDetection(): void {
    if (this.captureInterval) {
      clearInterval(this.captureInterval);
      this.captureInterval = null;
    }

    this.realtimeDetectionActive = false;
    this.realtimeMode = false;
    this.detectionService.stopRealtimeDetection();
    this.stopWebcam();
  }

  setRealtimeInterval(ms: number): void {
    this.captureIntervalMs = ms;
    if (this.realtimeDetectionActive) {
      if (this.captureInterval) {
        clearInterval(this.captureInterval);
      }
      this.beginRealtimeCapture();
    }
  }

  @HostListener('document:keydown.escape')
  onEscapeKey(): void {
    if (this.realtimeDetectionActive) {
      this.stopRealtimeDetection();
    } else if (this.isFullscreen) {
      this.closeFullscreen();
    } else if (this.fullscreenSelectionMode) {
      this.exitFullscreenSelection();
    }
  }


  openFullscreen(): void {
    if (this.resultImage) {
      // Calcular el factor de escala basado en las dimensiones del canvas de anotación
      if (this.annotationCanvas) {
        const canvas = this.annotationCanvas.nativeElement;
        // El canvas tiene las dimensiones reales de la imagen, pero se muestra escalado
        // Calculamos cuánto se escala para mostrar en pantalla completa
        this.scaleFactor = Math.min(
          window.innerWidth * 0.8 / canvas.width,
          window.innerHeight * 0.8 / canvas.height
        );
      }
      this.isFullscreen = true;
    }
  }

  closeFullscreen(): void {
    this.isFullscreen = false;
  }

  // enterFullscreenSelection removed — selection mode deprecated

  exitFullscreenSelection(): void {
    this.fullscreenSelectionMode = false;
    // Mantener la imagen y selección para no perder el estado tras salir del modo selección completa
  }
}
