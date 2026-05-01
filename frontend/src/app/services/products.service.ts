import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ProductsService {
  private api = 'http://localhost:8000/api/v1/products';
  constructor(private http: HttpClient) {}

  list(): Observable<any> {
    return this.http.get(this.api);
  }

  get(id: number): Observable<any> {
    return this.http.get(`${this.api}/${id}`);
  }
}
