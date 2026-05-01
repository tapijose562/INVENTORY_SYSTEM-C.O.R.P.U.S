import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DetectionLog {
  id: number;
  brand: string;
  color: string;
  size: string;
  text: string;
  confidence: number;
  price?: number;
  image_path: string;
  image_url: string;
  metadata: any;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class DetectionLogService {
  private apiUrl = 'http://localhost:8000/api/v1/detection';

  constructor(private http: HttpClient) { }

  getDetectionLogs(skip: number = 0, limit: number = 50): Observable<DetectionLog[]> {
    return this.http.get<DetectionLog[]>(`${this.apiUrl}/logs?skip=${skip}&limit=${limit}`);
  }

  getDetectionLog(logId: number): Observable<DetectionLog> {
    return this.http.get<DetectionLog>(`${this.apiUrl}/logs/${logId}`);
  }

  updateDetectionLog(logId: number, updates: any): Observable<DetectionLog> {
    return this.http.put<DetectionLog>(`${this.apiUrl}/logs/${logId}`, updates);
  }

  deleteDetectionLog(logId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/logs/${logId}`);
  }

  getDetectionImage(logId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/image/${logId}`, { responseType: 'blob' });
  }
}