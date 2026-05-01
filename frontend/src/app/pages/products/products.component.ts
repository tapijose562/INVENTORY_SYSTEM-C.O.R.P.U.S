import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ProductService } from '../../services/product.service';
import { ProductImageService, ProductImage } from '../../services/product-image.service';

interface Product {
  id: number;
  name: string;
  brand: string;
  color_primary: string;
  color_secondary?: string;
  color_rgb: { r: number; g: number; b: number };
  size: string;
  stock: number;
  price?: number;
  description?: string;
  yolo_confidence: number;
  detected_text?: string;
  created_at: string;
  updated_at?: string;
  image_url?: string;
  images?: ProductImage[];
}

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.scss']
})
export class ProductsComponent implements OnInit {
  products: Product[] = [];
  filteredProducts: Product[] = [];
  uniqueBrands: string[] = [];
  searchQuery = '';
  selectedBrand = '';
  sortBy = 'created_at';
  viewMode: 'grid' | 'list' = 'grid';
  
  // Image carousel and zoom state
  currentImageIndex: { [key: number]: number } = {};
  zoomLevel: { [key: number]: number } = {};
  showZoomControls: { [key: number]: boolean } = {};
  
  // Fullscreen image modal
  showFullscreenModal = false;
  fullscreenProduct: Product | null = null;
  fullscreenImageUrl: string | null = null;
  
  // Edit modal state
  editingProduct: Product | null = null;
  editLoading = false;
  editError = '';
  
  // General loading
  loading = false;
  deleteLoading: { [key: number]: boolean } = {};
  imagesLoading: { [key: number]: boolean } = {}; // Track loading state per product
  currentUser: any = null;

  private backendUrl = 'http://localhost:8000';

  constructor(
    private authService: AuthService,
    private productService: ProductService,
    private productImageService: ProductImageService
  ) { }

  ngOnInit(): void {
    this.loadProducts();
    this.authService.currentUser$.subscribe(user => this.currentUser = user);
  }

  loadProducts(): void {
    this.loading = true;
    this.productService.getProducts().subscribe({
      next: (products: Product[]) => {
        this.products = products.map(product => ({
          ...product,
          image_url: this.normalizeImageUrl(product.image_url) || product.image_url
        }));
        
        // Load images for each product
        this.products.forEach(product => {
          this.loadProductImages(product);
        });
        
        this.extractBrands();
        this.filterProducts();
        this.loading = false;
        console.log('✅ Products loaded from database:', products.length);
        console.log('📸 Sample product images:', this.products.slice(0, 3).map(p => ({ 
          name: p.name, 
          image_url: p.image_url,
          images_count: p.images?.length || 0
        })));
      },
      error: (error: any) => {
        console.error('❌ Error loading products:', error);
        this.loading = false;
      }
    });
  }

  normalizeImageUrl(url?: string): string | undefined {
    if (!url) {
      return undefined;
    }

    const trimmed = url.trim();
    if (!trimmed) {
      return undefined;
    }

    if (trimmed.startsWith('/uploads/')) {
      return `${this.backendUrl}${trimmed}`;
    }

    if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
      return trimmed;
    }

    return undefined;
  }

  loadProductImages(product: Product): void {
    this.imagesLoading[product.id] = true;
    this.productImageService.getProductImages(product.id).subscribe({
      next: (result: any) => {
        if (result.images && result.images.length > 0) {
          const normalizedImages: ProductImage[] = result.images
            .map((img: any) => ({
              ...img,
              image_url: this.normalizeImageUrl(img.image_url) || img.image_url
            }))
            .filter((img: ProductImage) => this.isValidImageUrl(img.image_url));

          product.images = normalizedImages;

          // Set primary image URL if not already set
          if (!product.image_url && normalizedImages.length > 0) {
            const primaryImage = normalizedImages.find((img: any) => img.is_primary === 1) || normalizedImages[0];
            product.image_url = this.normalizeImageUrl(primaryImage.image_url) || primaryImage.image_url;
          }
          console.log(`✅ Loaded ${result.images.length} images for product ${product.name}`);
        } else {
          console.warn(`⚠️ No images found for product ${product.name} (ID: ${product.id})`);
        }
        this.imagesLoading[product.id] = false;
      },
      error: (error: any) => {
        console.error(`❌ Error loading images for product ${product.id}:`, error);
        this.imagesLoading[product.id] = false;
      }
    });
  }

  extractBrands(): void {
    this.uniqueBrands = [...new Set(this.products.map(p => p.brand))].sort();
  }

  filterProducts(): void {
    let filtered = this.products;

    if (this.searchQuery) {
      const q = this.searchQuery.toLowerCase();
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.brand.toLowerCase().includes(q) ||
        p.color_primary.toLowerCase().includes(q)
      );
    }

    if (this.selectedBrand) {
      filtered = filtered.filter(p => p.brand === this.selectedBrand);
    }

    this.filteredProducts = filtered;
    this.sortProducts();
  }

  sortProducts(): void {
    this.filteredProducts.sort((a, b) => {
      switch (this.sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'stock':
          return b.stock - a.stock;
        case 'yolo_confidence':
          return b.yolo_confidence - a.yolo_confidence;
        case 'created_at':
        default:
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
    });
  }

  calculateTotalStock(): number {
    return this.products.reduce((sum, p) => sum + p.stock, 0);
  }

  calculateAvgConfidence(): number {
    if (this.products.length === 0) return 0;
    const sum = this.products.reduce((acc, p) => acc + p.yolo_confidence, 0);
    return sum / this.products.length;
  }

  editProduct(product: Product): void {
    this.editingProduct = { ...product };
    this.editError = '';
  }

  saveEdit(): void {
    if (!this.editingProduct) return;
    
    // Validation
    if (!this.editingProduct.name || !this.editingProduct.brand || !this.editingProduct.size) {
      this.editError = 'Please fill all required fields';
      return;
    }

    this.editLoading = true;
    this.editError = '';

    const updateData = {
      name: this.editingProduct.name,
      brand: this.editingProduct.brand,
      color_primary: this.editingProduct.color_primary,
      color_secondary: this.editingProduct.color_secondary || null,
      color_rgb: this.editingProduct.color_rgb,
      stock: this.editingProduct.stock,
      price: this.editingProduct.price || null,
      description: this.editingProduct.description || null
    };

    this.productService.updateProduct(this.editingProduct.id, updateData).subscribe({
      next: (updated) => {
        // Update local list
        const index = this.products.findIndex(p => p.id === updated.id);
        if (index > -1) {
          this.products[index] = updated;
        }
        this.filterProducts();
        this.editingProduct = null;
        this.editLoading = false;
        alert('✅ Product updated successfully!');
        console.log('✅ Product updated:', updated);
      },
      error: (error: any) => {
        this.editError = error.error?.detail || 'Error updating product';
        this.editLoading = false;
        console.error('❌ Error updating product:', error);
      }
    });
  }

  cancelEdit(): void {
    this.editingProduct = null;
    this.editError = '';
  }

  deleteProduct(id: number): void {
    if (!confirm('⚠️ Are you sure you want to delete this product? This action cannot be undone.')) {
      return;
    }

    this.deleteLoading[id] = true;

    this.productService.deleteProduct(id).subscribe({
      next: () => {
        // Remove from local list
        this.products = this.products.filter(p => p.id !== id);
        this.filterProducts();
        this.deleteLoading[id] = false;
        alert('✅ Product deleted successfully!');
        console.log('✅ Product deleted, ID:', id);
      },
      error: (error: any) => {
        console.error('❌ Error deleting product:', error);
        this.deleteLoading[id] = false;
        alert('❌ Error deleting product: ' + (error.error?.detail || error.message));
      }
    });
  }

  isValidImageUrl(url: string | undefined): boolean {
    if (!url) return false;
    const trimmed = url.trim();
    return trimmed.length > 0 && 
           !trimmed.includes('undefined') && 
           (trimmed.startsWith('http://') || trimmed.startsWith('https://'));
  }

  onImageError(event: any): void {
    const img = event.target;
    console.error('❌ Image load error:', {
      src: img.src,
      alt: img.alt,
      productName: img.alt
    });
    event.target.style.display = 'none';
    event.target.parentElement.classList.add('image-error');
  }

  // Image carousel methods
  getCurrentImage(product: Product): string | undefined {
    const validProductImageUrl = this.isValidImageUrl(product.image_url || undefined) ? product.image_url : undefined;

    if (!product.images || product.images.length === 0) {
      return validProductImageUrl;
    }

    const currentIndex = this.currentImageIndex[product.id] || 0;
    const currentImageUrl = product.images[currentIndex]?.image_url;
    if (this.isValidImageUrl(currentImageUrl)) {
      return currentImageUrl;
    }

    return validProductImageUrl;
  }

  nextImage(product: Product): void {
    if (!product.images || product.images.length <= 1) return;
    
    const currentIndex = this.currentImageIndex[product.id] || 0;
    this.currentImageIndex[product.id] = (currentIndex + 1) % product.images.length;
  }

  prevImage(product: Product): void {
    if (!product.images || product.images.length <= 1) return;
    
    const currentIndex = this.currentImageIndex[product.id] || 0;
    this.currentImageIndex[product.id] = currentIndex === 0 ? product.images.length - 1 : currentIndex - 1;
  }

  getCurrentImageIndex(product: Product): number {
    return this.currentImageIndex[product.id] || 0;
  }

  // Zoom methods
  getZoomLevel(productId: number): number {
    return this.zoomLevel[productId] || 1;
  }

  zoomIn(productId: number): void {
    const currentZoom = this.getZoomLevel(productId);
    if (currentZoom < 3) {
      this.zoomLevel[productId] = currentZoom + 0.25;
      this.showZoomControls[productId] = true;
    }
  }

  zoomOut(productId: number): void {
    const currentZoom = this.getZoomLevel(productId);
    if (currentZoom > 0.5) {
      this.zoomLevel[productId] = currentZoom - 0.25;
      this.showZoomControls[productId] = true;
    }
  }

  resetZoom(productId: number): void {
    this.zoomLevel[productId] = 1;
    this.showZoomControls[productId] = false;
  }

  onImageMouseEnter(productId: number): void {
    this.showZoomControls[productId] = true;
  }

  onImageMouseLeave(productId: number): void {
    // Keep zoom controls visible if zoomed
    if (this.getZoomLevel(productId) !== 1) {
      this.showZoomControls[productId] = true;
    } else {
      this.showZoomControls[productId] = false;
    }
  }

  // Fullscreen modal methods
  openFullscreenModal(product: Product): void {
    this.fullscreenProduct = product;
    this.fullscreenImageUrl = this.getCurrentImage(product) || null;
    this.showFullscreenModal = true;
  }

  closeFullscreenModal(): void {
    this.showFullscreenModal = false;
    this.fullscreenProduct = null;
    this.fullscreenImageUrl = null;
  }

  nextFullscreenImage(): void {
    if (!this.fullscreenProduct) return;
    this.nextImage(this.fullscreenProduct);
    this.fullscreenImageUrl = this.getCurrentImage(this.fullscreenProduct) || null;
  }

  prevFullscreenImage(): void {
    if (!this.fullscreenProduct) return;
    this.prevImage(this.fullscreenProduct);
    this.fullscreenImageUrl = this.getCurrentImage(this.fullscreenProduct) || null;
  }

  logout(): void {
    this.authService.logout();
  }
}
