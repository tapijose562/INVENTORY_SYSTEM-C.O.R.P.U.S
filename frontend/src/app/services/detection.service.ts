import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { webSocket } from 'rxjs/webSocket';

export interface Detection {
  id: number;
  class: string;
  confidence: number;
  bbox: number[];
  segmentation?: number[][];
  area: number;
  is_shoe: boolean;
  center_x: number;
  center_y: number;
  recommended: boolean;
}

export interface DetectionResult {
  detections: Detection[];
  image_size: { width: number; height: number };
  total_found: number;
}

export interface DetectionResponse {
  brand: string;
  colors: string;
  dominant_rgb: number[];
  all_colors_rgb: number[][];
  detected_text: string;
  numbers: string[];
  confidence: number;
  bbox: number[];
  suggested_price: number | null;
  suggested_size: string | null;
  detection_class: string;
  detection_id: number;
}

@Injectable({
  providedIn: 'root'
})
export class DetectionService {
  private apiUrl = 'http://localhost:8000/api/v1/detection';

  constructor(private http: HttpClient) { }

  detectFromImage(file: File, useCorpus: boolean = false): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (useCorpus) {
      formData.append('use_corpus', 'true');
    }
    return this.http.post(`${this.apiUrl}/detect-from-image`, formData);
  }

  detectFromUrl(imageUrl: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/detect-from-url`, { image_url: imageUrl });
  }

  detectColorFromSelection(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/detect-color-from-selection`, formData);
  }

  suggestText(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/suggest-text`, formData);
  }

  getAllDetections(imageFile: File, useCorpus: boolean = false): Observable<DetectionResult> {
    const formData = new FormData();
    formData.append('file', imageFile);
    if (useCorpus) {
      formData.append('use_corpus', 'true');
    }

    return this.http.post<DetectionResult>(`${this.apiUrl}/get-all-detections`, formData);
  }

  detectFromSelection(imageFile: File, detectionId: number, useCorpus: boolean = false): Observable<DetectionResponse> {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('detection_id', detectionId.toString());
    if (useCorpus) {
      formData.append('use_corpus', 'true');
    }

    return this.http.post<DetectionResponse>(`${this.apiUrl}/detect-from-selection`, formData);
  }

  // WebSocket for real-time detection
  private realtimeWebSocket: any = null;
  private realtimeSubject = new Subject<any>();

  startRealtimeDetection(): Observable<any> {
    if (this.realtimeWebSocket) {
      this.realtimeWebSocket.unsubscribe();
    }

    // Create WebSocket connection
    this.realtimeWebSocket = webSocket({
      url: 'ws://localhost:8000/api/v1/detection/ws/real-time-detection',
      deserializer: (e) => JSON.parse(e.data)
    });

    // Handle incoming messages
    this.realtimeWebSocket.subscribe({
      next: (message: any) => {
        if (message.error) {
          console.error('WebSocket error:', message.error);
        } else {
          this.realtimeSubject.next(message);
        }
      },
      error: (error: any) => {
        console.error('WebSocket error:', error);
        this.realtimeSubject.error(error);
      },
      complete: () => {
        console.log('WebSocket connection closed');
      }
    });

    return this.realtimeSubject.asObservable();
  }

  sendRealtimeFrame(imageData: string, model: 'roboflow' | 'corpus' = 'roboflow'): void {
    if (this.realtimeWebSocket && !this.realtimeWebSocket.closed) {
      this.realtimeWebSocket.next({
        type: 'frame',
        model: model,
        image: imageData
      });
    }
  }

  stopRealtimeDetection(): void {
    if (this.realtimeWebSocket) {
      this.realtimeWebSocket.unsubscribe();
      this.realtimeWebSocket = null;
    }
  }

  pingRealtimeConnection(): void {
    if (this.realtimeWebSocket && !this.realtimeWebSocket.closed) {
      this.realtimeWebSocket.next({ type: 'ping' });
    }
  }

  // ============================================================================
  // CORPUS DETECTOR METHODS - Using trained YOLO model
  // ============================================================================

  detectWithCorpus(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/detect-corpus`, formData);
  }

  detectCorpusRealtime(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/detect-corpus-realtime`, formData);
  }

  getCorpusStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/corpus-status`);
  }
}
