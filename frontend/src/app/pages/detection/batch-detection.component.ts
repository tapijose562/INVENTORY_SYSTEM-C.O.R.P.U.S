import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { take } from 'rxjs/operators';
import { AuthService } from '../../services/auth.service';
import { ProductService } from '../../services/product.service';
import { ProductImageService, ProductImage } from '../../services/product-image.service';
import { FilePreviewPipe } from '../../pipes/file-preview.pipe';

interface SelectionData {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  width: number;
  height: number;
  label?: string;
  created_at: Date;
}

@Component({
  selector: 'app-batch-detection',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, FilePreviewPipe],
  templateUrl: './batch-detection.component.html',
  styleUrls: ['./batch-detection.component.scss']
})
export class BatchDetectionComponent implements OnInit {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
  
  // State
  mode: 'upload' | 'processing' | 'gallery' = 'upload';
  selectedFiles: File[] = [];
  loading = false;
  error = '';
  dragOver = false;
  
  // Product selection
  productId: number | null = null;
  availableProducts: any[] = [];
  
  // Images and detection
  images: ProductImage[] = [];
  currentImageIndex = 0;
  currentDetection: any = null;
  detectionProcessing = false;
  
  // Batch detection
  batchDetectionInProgress = false;
  detectionProgress = 0;
  totalImagesForBatch = 0;
  
  // Selection/Annotation
  selections: { [imageId: number]: SelectionData[] } = {};
  currentSelections: SelectionData[] = [];
  drawing = false;
  startX = 0;
  startY = 0;
  editingSelectionIndex: number | null = null;
  
  // Constants
  MAX_IMAGES = 10;
  
  @ViewChild('canvasList', { read: ElementRef }) canvasList!: ElementRef;
  backLink = '/client/detection';

  constructor(
    private productImageService: ProductImageService,
    private productService: ProductService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadProducts();
    this.authService.currentUser$
      .pipe(take(1))
      .subscribe(user => {
        if (user?.role === 'admin') {
          this.backLink = '/admin/detection';
        }
      });
  }

  /**
   * Load available products
   */
  loadProducts(): void {
    this.productService.getProducts().subscribe({
      next: (products) => {
        this.availableProducts = products;
      },
      error: (err) => {
        console.error('Error loading products:', err);
      }
    });
  }

  /**
   * Handle file selection
   */
  onFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      const files = Array.from(input.files);
      this.addFiles(files);
    }
  }

  /**
   * Handle drag and drop
   */
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = true;
  }

  onDragLeave(): void {
    this.dragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = false;
    
    if (event.dataTransfer?.files) {
      const files = Array.from(event.dataTransfer.files);
      this.addFiles(files);
    }
  }

  /**
   * Add files to selection
   */
  addFiles(files: File[]): void {
    const remaining = this.MAX_IMAGES - this.selectedFiles.length;
    
    if (remaining <= 0) {
      this.error = `Ya has seleccionado el máximo de ${this.MAX_IMAGES} imágenes`;
      return;
    }

    const filesToAdd = files.slice(0, remaining);
    this.selectedFiles = [...this.selectedFiles, ...filesToAdd];
    this.error = '';
  }

  /**
   * Remove file from selection
   */
  removeFile(index: number): void {
    this.selectedFiles.splice(index, 1);
  }

  /**
   * Click to browse files
   */
  browseFiles(): void {
    this.fileInput.nativeElement.click();
  }

  /**
   * Start upload process
   */
  startUpload(): void {
    if (!this.productId) {
      this.error = 'Por favor selecciona un producto';
      return;
    }

    if (this.selectedFiles.length === 0) {
      this.error = 'Por favor selecciona al menos una imagen';
      return;
    }

    this.loading = true;
    this.error = '';

    this.productImageService.uploadBatchImages(
      this.productId,
      this.selectedFiles
    ).subscribe({
      next: (response) => {
        this.images = response.images;
        this.mode = 'gallery';
        this.currentImageIndex = 0;
        this.loadCurrentImageSelections(); // Load selections for first image
        
        // Auto-start batch detection after upload completes
        this.loading = false;
        this.startAutomaticBatchDetection();
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error uploading images';
        this.loading = false;
      }
    });
  }

  /**
   * Start automatic batch detection on all uploaded images
   */
  private startAutomaticBatchDetection(): void {
    if (this.images.length === 0) return;
    
    const imagesToDetect = this.images.filter(img => img.status !== 'detected');
    
    if (imagesToDetect.length === 0) {
      console.log('Todas las imágenes ya fueron detectadas');
      return;
    }

    this.batchDetectionInProgress = true;
    this.detectionProgress = 0;
    this.totalImagesForBatch = imagesToDetect.length;
    
    // Start processing queue
    this.processImageDetectionQueue(imagesToDetect, 0);
  }

  /**
   * Run detection on current image
   */
  detectCurrentImage(): void {
    if (!this.images[this.currentImageIndex]) return;

    const image = this.images[this.currentImageIndex];
    this.detectionProcessing = true;

    this.productImageService.detectImage(image.id).subscribe({
      next: (detection) => {
        this.currentDetection = detection;
        this.images[this.currentImageIndex] = {
          ...image,
          detected_brand: detection.brand,
          detected_color: detection.color,
          detected_size: detection.size,
          detected_text: detection.text,
          confidence_score: detection.confidence,
          price: detection.price,
          status: 'detected'
        };
        this.detectionProcessing = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Detection failed';
        this.detectionProcessing = false;
      }
    });
  }

  /**
   * Navigate to next image
   */
  nextImage(): void {
    if (this.currentImageIndex < this.images.length - 1) {
      this.currentImageIndex++;
      this.loadCurrentImageSelections();
      this.currentDetection = null;
    }
  }

  /**
   * Navigate to previous image
   */
  previousImage(): void {
    if (this.currentImageIndex > 0) {
      this.currentImageIndex--;
      this.loadCurrentImageSelections();
      this.currentDetection = null;
    }
  }

  /**
   * Change current image using thumbnail click
   */
  setCurrentImage(index: number): void {
    if (index === this.currentImageIndex) {
      return;
    }
    this.currentImageIndex = index;
    this.currentDetection = null;
    this.loadCurrentImageSelections();
  }

  /**
   * Load selections for current image
   */
  loadCurrentImageSelections(): void {
    const currentImage = this.images[this.currentImageIndex];
    if (currentImage) {
      this.currentSelections = this.selections[currentImage.id] || [];
      // Load from image data if exists
      if (currentImage.selection_data && Array.isArray(currentImage.selection_data)) {
        this.currentSelections = currentImage.selection_data.map((sel: any, index: number) => ({
          id: sel.id || `sel_${index}`,
          x1: sel.x1,
          y1: sel.y1,
          x2: sel.x2,
          y2: sel.y2,
          width: sel.x2 - sel.x1,
          height: sel.y2 - sel.y1,
          label: sel.label || `Selección ${index + 1}`,
          created_at: sel.created_at ? new Date(sel.created_at) : new Date()
        }));
        this.selections[currentImage.id] = this.currentSelections;
      }
    } else {
      this.currentSelections = [];
    }
    this.editingSelectionIndex = null;
    this.redrawCanvas();
  }

  /**
   * Calculate scale factor between canvas visual size and actual drawing dimensions
   * This fixes the misalignment issue when canvas CSS size differs from internal dimensions
   */
  private getCanvasScale(canvas: HTMLCanvasElement): { scaleX: number; scaleY: number } {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return { scaleX, scaleY };
  }

  /**
   * Canvas mouse events for selection
   */
  onCanvasMouseDown(event: MouseEvent): void {
    if (!this.images[this.currentImageIndex]) return;

    const canvas = event.target as HTMLCanvasElement;
    const rect = canvas.getBoundingClientRect();
    const { scaleX, scaleY } = this.getCanvasScale(canvas);
    
    this.drawing = true;
    this.startX = (event.clientX - rect.left) * scaleX;
    this.startY = (event.clientY - rect.top) * scaleY;
  }

  onCanvasMouseMove(event: MouseEvent): void {
    if (!this.drawing || !this.images[this.currentImageIndex]) return;

    const canvas = event.target as HTMLCanvasElement;
    const rect = canvas.getBoundingClientRect();
    const { scaleX, scaleY } = this.getCanvasScale(canvas);
    const currentX = (event.clientX - rect.left) * scaleX;
    const currentY = (event.clientY - rect.top) * scaleY;

    // Redraw canvas with current selections and drawing preview
    this.redrawCanvas();
    
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.strokeStyle = '#33d9b2';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.strokeRect(
        this.startX,
        this.startY,
        currentX - this.startX,
        currentY - this.startY
      );
      ctx.setLineDash([]);
    }
  }

  onCanvasMouseUp(event: MouseEvent): void {
    if (!this.drawing || !this.images[this.currentImageIndex]) return;

    const canvas = event.target as HTMLCanvasElement;
    const rect = canvas.getBoundingClientRect();
    const { scaleX, scaleY } = this.getCanvasScale(canvas);
    const endX = (event.clientX - rect.left) * scaleX;
    const endY = (event.clientY - rect.top) * scaleY;

    this.drawing = false;

    // Ensure coordinates are valid
    const x1 = Math.min(this.startX, endX);
    const y1 = Math.min(this.startY, endY);
    const x2 = Math.max(this.startX, endX);
    const y2 = Math.max(this.startY, endY);

    if (x2 - x1 > 10 && y2 - y1 > 10) {
      const newSelection: SelectionData = {
        id: `sel_${Date.now()}`,
        x1, y1, x2, y2,
        width: x2 - x1,
        height: y2 - y1,
        label: `Selección ${this.currentSelections.length + 1}`,
        created_at: new Date()
      };

      if (this.editingSelectionIndex !== null) {
        // Update existing selection
        this.currentSelections[this.editingSelectionIndex] = newSelection;
        this.editingSelectionIndex = null;
      } else {
        // Add new selection
        this.currentSelections.push(newSelection);
      }

      // Update selections map
      const currentImage = this.images[this.currentImageIndex];
      this.selections[currentImage.id] = this.currentSelections;

      this.redrawCanvas();
    }
  }

  /**
   * Redraw canvas with current selections
   */
  redrawCanvas(): void {
    const canvas = document.querySelector(
      `canvas[data-index="${this.currentImageIndex}"]`
    ) as HTMLCanvasElement;
    
    if (!canvas || !this.images[this.currentImageIndex]) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear and redraw image
    const img = new Image();
    img.src = this.images[this.currentImageIndex].image_url;
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      // Draw all selections
      this.currentSelections.forEach((selection, index) => {
        const isEditing = this.editingSelectionIndex === index;
        ctx.strokeStyle = isEditing ? '#ff9800' : '#33d9b2';
        ctx.lineWidth = isEditing ? 3 : 2;
        ctx.strokeRect(
          selection.x1,
          selection.y1,
          selection.width,
          selection.height
        );

        // Draw label
        ctx.fillStyle = isEditing ? '#ff9800' : '#33d9b2';
        ctx.font = '12px Arial';
        ctx.fillText(
          selection.label || `Sel ${index + 1}`,
          selection.x1 + 5,
          selection.y1 - 5
        );
      });
    };
  }

  /**
   * Run detection on all images sequentially
   */
  detectAllImages(): void {
    const imagesToDetect = this.images.filter(img => img.status !== 'detected');
    
    if (imagesToDetect.length === 0) {
      this.error = 'Todas las imágenes ya han sido detectadas';
      return;
    }

    this.batchDetectionInProgress = true;
    this.detectionProgress = 0;
    this.totalImagesForBatch = imagesToDetect.length;
    this.error = '';

    // Process images sequentially (manual trigger - show alert)
    this.processImageDetectionQueue(imagesToDetect, 0, true);
  }

  /**
   * Process detection queue recursively
   * @param imagesToDetect Array of images to process
   * @param index Current index in queue
   * @param showAlert Whether to show completion alert (manual trigger) or silent (automatic)
   */
  private processImageDetectionQueue(imagesToDetect: ProductImage[], index: number, showAlert: boolean = false): void {
    if (index >= imagesToDetect.length) {
      // All done
      this.batchDetectionInProgress = false;
      this.detectionProgress = 0;
      this.totalImagesForBatch = 0;
      
      if (showAlert) {
        alert(`✅ Detección completada:\n${imagesToDetect.length} imágenes procesadas`);
      }
      return;
    }

    const image = imagesToDetect[index];
    
    this.productImageService.detectImage(image.id).subscribe({
      next: (detection) => {
        // Find and update the image in the main array
        const mainIndex = this.images.findIndex(img => img.id === image.id);
        if (mainIndex !== -1) {
          this.images[mainIndex] = {
            ...this.images[mainIndex],
            detected_brand: detection.brand,
            detected_color: detection.color,
            detected_size: detection.size,
            detected_text: detection.text,
            confidence_score: detection.confidence,
            price: detection.price,
            detection_metadata: detection.metadata,
            status: 'detected'
          };
        }

        // Update progress
        this.detectionProgress = index + 1;

        // Process next image (pass showAlert to next call)
        this.processImageDetectionQueue(imagesToDetect, index + 1, showAlert);
      },
      error: (err) => {
        console.error(`Error detecting image ${image.id}:`, err);
        // Continue with next image even if this one fails
        this.detectionProgress = index + 1;
        this.processImageDetectionQueue(imagesToDetect, index + 1, showAlert);
      }
    });
  }

  /**
   * Save current image detection results
   */
  saveCurrentDetectionResults(): void {
    if (!this.images[this.currentImageIndex] || !this.currentDetection) {
      this.error = 'No hay resultados de detección para guardar';
      return;
    }

    const image = this.images[this.currentImageIndex];
    
    this.productImageService.updateImage(image.id, {
      detected_brand: this.currentDetection.brand,
      detected_color: this.currentDetection.color,
      detected_size: this.currentDetection.size,
      detected_text: this.currentDetection.text,
      confidence_score: this.currentDetection.confidence,
      price: this.currentDetection.price,
      detection_metadata: this.currentDetection.metadata,
      status: 'detected'
    }).subscribe({
      next: (_updated) => {
        this.images[this.currentImageIndex] = {
          ...image,
          detected_brand: this.currentDetection.brand,
          detected_color: this.currentDetection.color,
          detected_size: this.currentDetection.size,
          detected_text: this.currentDetection.text,
          confidence_score: this.currentDetection.confidence,
          price: this.currentDetection.price,
          detection_metadata: this.currentDetection.metadata,
          status: 'detected'
        };
        alert('✅ Resultados de detección guardados');
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error saving detection results';
      }
    });
  }

  /**
   * Edit a selection
   */
  editSelection(index: number): void {
    this.editingSelectionIndex = index;
    this.redrawCanvas();
  }

  /**
   * Delete a selection
   */
  deleteSelection(index: number): void {
    if (confirm('¿Eliminar esta selección?')) {
      this.currentSelections.splice(index, 1);
      const currentImage = this.images[this.currentImageIndex];
      this.selections[currentImage.id] = this.currentSelections;
      this.editingSelectionIndex = null;
      this.redrawCanvas();
    }
  }

  /**
   * Cancel editing selection
   */
  cancelEditSelection(): void {
    this.editingSelectionIndex = null;
    this.redrawCanvas();
  }

  /**
   * Update selection label
   */
  updateSelectionLabel(index: number, newLabel?: string): void {
    if (this.currentSelections[index]) {
      this.currentSelections[index].label = newLabel || `Selección ${index + 1}`;
      const currentImage = this.images[this.currentImageIndex];
      this.selections[currentImage.id] = this.currentSelections;
    }
  }

  /**
   * Save current image selections/annotation
   */
  saveCurrentImage(): void {
    if (!this.images[this.currentImageIndex] || this.currentSelections.length === 0) {
      this.error = 'Por favor crea al menos una selección antes de guardar';
      return;
    }

    const image = this.images[this.currentImageIndex];
    
    this.productImageService.updateImage(image.id, {
      selection_data: this.currentSelections,
      status: 'annotated'
    }).subscribe({
      next: (_updated) => {
        this.images[this.currentImageIndex] = {
          ...image,
          selection_data: this.currentSelections,
          status: 'annotated'
        };
        alert(`✅ ${this.currentSelections.length} selecciones guardadas`);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error saving selections';
      }
    });
  }

  /**
   * Set as primary image
   */
  setAsPrimary(imageId: number): void {
    this.productImageService.setImageAsPrimary(imageId).subscribe({
      next: () => {
        // Update is_primary flags
        this.images.forEach(img => {
          img.is_primary = img.id === imageId ? 1 : 0;
        });
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error setting primary image';
      }
    });
  }

  /**
   * Delete image
   */
  deleteImage(imageId: number, index: number): void {
    if (confirm('¿Estás seguro de que quieres eliminar esta imagen?')) {
      this.productImageService.deleteImage(imageId).subscribe({
        next: () => {
          this.images.splice(index, 1);
          if (this.currentImageIndex >= this.images.length) {
            this.currentImageIndex = Math.max(0, this.images.length - 1);
          }
        },
        error: (err) => {
          this.error = err.error?.detail || 'Error deleting image';
        }
      });
    }
  }

  /**
   * Finish and go back
   */
  finish(): void {
    if (confirm('¿Finalizar y volver al módulo principal?')) {
      this.resetState();
      this.mode = 'upload';
    }
  }

  /**
   * Reset to initial state
   */
  resetState(): void {
    this.selectedFiles = [];
    this.images = [];
    this.currentImageIndex = 0;
    this.currentDetection = null;
    this.currentSelections = [];
    this.productId = null;
    this.error = '';
  }

  /**
   * Get image URL
   */
  getImageUrl(image: ProductImage): string {
    if (image.image_url.startsWith('http')) {
      return image.image_url;
    }
    return this.productImageService.getImageUrl(image.image_filename);
  }
}
