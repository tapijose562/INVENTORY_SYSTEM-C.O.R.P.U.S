import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ProductImage {
  id: number;
  product_id?: number;
  detection_log_id?: number;
  image_url: string;
  image_filename: string;
  image_size: number;
  detected_brand?: string;
  detected_color?: string;
  detected_size?: string;
  detected_text?: string;
  confidence_score?: number;
  price?: number;
  selection_data?: any;
  detection_metadata?: any;
  image_metadata?: any;
  is_primary: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProductImageList {
  total_images: number;
  images: ProductImage[];
  max_images: number;
}

export interface DetectionResult {
  brand: string;
  color: string;
  size: string;
  text: string;
  confidence: number;
  price?: number;
  rgb: any;
  metadata: any;
}

@Injectable({
  providedIn: 'root'
})
export class ProductImageService {
  private apiUrl = '/api/v1/product-images';

  constructor(private http: HttpClient) {}

  /**
   * Upload multiple images for a product
   */
  uploadBatchImages(productId: number, files: File[]): Observable<ProductImageList> {
    const formData = new FormData();
    formData.append('product_id', productId.toString());
    
    files.forEach((file, _index) => {
      formData.append('files', file, file.name);
    });

    return this.http.post<ProductImageList>(`${this.apiUrl}/upload-batch`, formData);
  }

  /**
   * Get all images for a product
   */
  getProductImages(productId: number): Observable<ProductImageList> {
    return this.http.get<ProductImageList>(`${this.apiUrl}/product/${productId}`);
  }

  /**
   * Run detection on a specific image
   */
  detectImage(imageId: number): Observable<DetectionResult> {
    return this.http.post<DetectionResult>(`${this.apiUrl}/detect/${imageId}`, {});
  }

  /**
   * Run detection on multiple images sequentially
   */
  detectMultipleImages(imageIds: number[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/detect-batch`, { image_ids: imageIds });
  }

  /**
   * Update image detection results or selection
   */
  updateImage(
    imageId: number,
    updateData: Partial<ProductImage>
  ): Observable<ProductImage> {
    return this.http.patch<ProductImage>(
      `${this.apiUrl}/${imageId}`,
      updateData
    );
  }

  /**
   * Set image as primary
   */
  setImageAsPrimary(imageId: number): Observable<ProductImage> {
    return this.http.post<ProductImage>(
      `${this.apiUrl}/${imageId}/set-primary`,
      {}
    );
  }

  /**
   * Delete an image
   */
  deleteImage(imageId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${imageId}`);
  }

  /**
   * Get image file
   */
  getImageUrl(filename: string): string {
    return `${this.apiUrl}/file/${filename}`;
  }
}
