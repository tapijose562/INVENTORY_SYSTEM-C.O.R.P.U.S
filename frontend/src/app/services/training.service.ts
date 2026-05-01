import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TrainingService {
  private apiUrl = 'http://localhost:8000/api/v1/training';

  constructor(private http: HttpClient) { }

  startTraining(name: string, epochs: number = 10, batchSize: number = 16): Observable<any> {
    return this.http.post(`${this.apiUrl}/start-training`, {
      name,
      epochs,
      batch_size: batchSize
    });
  }

  getTrainingSessions(): Observable<any> {
    return this.http.get(`${this.apiUrl}/sessions`);
  }

  getTrainingSession(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/sessions/${id}`);
  }
}
