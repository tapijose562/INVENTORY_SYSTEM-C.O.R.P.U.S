import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private apiUrl = 'http://localhost:8000/api/v1/products';

  constructor(private http: HttpClient) { }

  getProducts(skip: number = 0, limit: number = 100, brand?: string): Observable<any> {
    let params = `?skip=${skip}&limit=${limit}`;
    if (brand) {
      params += `&brand=${brand}`;
    }
    return this.http.get(`${this.apiUrl}${params}`);
  }

  getProduct(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${id}`);
  }

  createProduct(product: any): Observable<any> {
    return this.http.post(this.apiUrl, product);
  }

  createProductWithImage(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/with-image`, formData);
  }

  uploadProductImage(productId: number, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/${productId}/upload-image`, formData);
  }

  annotateProductImage(productId: number, annotation: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${productId}/annotate`, annotation);
  }

  updateProduct(id: number, product: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, product);
  }

  deleteProduct(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
