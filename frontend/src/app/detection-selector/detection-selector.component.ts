import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

interface Detection {
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

interface DetectionResult {
  detections: Detection[];
  image_size: { width: number; height: number };
  total_found: number;
}

@Component({
  selector: 'app-detection-selector',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="detection-selector" *ngIf="detections">
      <h3>Selecciona la detección correcta</h3>
      <p class="subtitle">Se encontraron {{ detections.total_found }} objetos. Selecciona el que mejor representa el calzado:</p>

      <div class="detections-grid">
        <mat-card
          *ngFor="let detection of detections.detections"
          [class.selected]="selectedDetectionId === detection.id"
          [class.recommended]="detection.recommended"
          class="detection-card"
          (click)="selectDetection(detection.id)"
        >
          <mat-card-header>
            <mat-card-title>{{ detection.class }}</mat-card-title>
            <mat-card-subtitle>
              Confianza: {{ (detection.confidence * 100).toFixed(1) }}%
              <span *ngIf="detection.recommended" class="recommended-badge">Recomendado</span>
            </mat-card-subtitle>
          </mat-card-header>

          <mat-card-content>
            <div class="detection-info">
              <div class="bbox-preview" [style.width.px]="previewWidth" [style.height.px]="previewHeight">
                <svg [attr.width]="previewWidth" [attr.height]="previewHeight" class="preview-svg">
                  <polygon
                    *ngIf="detection.segmentation?.length"
                    [attr.points]="getScaledPolygon(detection.segmentation)"
                    class="segmentation-polygon"
                  />
                  <rect
                    *ngIf="!detection.segmentation?.length"
                    [attr.x]="getScaledX(detection.bbox[0])"
                    [attr.y]="getScaledY(detection.bbox[1])"
                    [attr.width]="getScaledWidth(detection.bbox)"
                    [attr.height]="getScaledHeight(detection.bbox)"
                    class="bbox-overlay"
                  />
                </svg>
              </div>
              <div class="detection-details">
                <p><strong>Posición:</strong> Centro ({{ detection.center_x.toFixed(0) }}, {{ detection.center_y.toFixed(0) }})</p>
                <p><strong>Área:</strong> {{ detection.area.toFixed(0) }} px²</p>
                <p><strong>Es calzado:</strong> {{ detection.is_shoe ? 'Sí' : 'No' }}</p>
              </div>
            </div>
          </mat-card-content>

          <mat-card-actions>
            <button mat-raised-button color="primary" (click)="confirmSelection(detection.id)">
              <mat-icon>check</mat-icon>
              Seleccionar
            </button>
          </mat-card-actions>
        </mat-card>
      </div>

      <div class="actions" *ngIf="selectedDetectionId !== null">
        <button mat-button (click)="cancelSelection()">
          <mat-icon>cancel</mat-icon>
          Cancelar
        </button>
        <button mat-raised-button color="accent" (click)="confirmSelection(selectedDetectionId)">
          <mat-icon>done</mat-icon>
          Confirmar Selección
        </button>
      </div>
    </div>

    <div class="loading" *ngIf="loading">
      <mat-spinner></mat-spinner>
      <p>Analizando imagen...</p>
    </div>
  `,
  styles: [`
    .detection-selector {
      padding: 20px;
    }

    .subtitle {
      color: #666;
      margin-bottom: 20px;
    }

    .detections-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .detection-card {
      cursor: pointer;
      transition: all 0.3s ease;
      border: 2px solid transparent;
    }

    .detection-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .detection-card.selected {
      border-color: #1976d2;
      background-color: #e3f2fd;
    }

    .detection-card.recommended {
      border-color: #388e3c;
      background-color: #e8f5e8;
    }

    .recommended-badge {
      background-color: #388e3c;
      color: white;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.75em;
      margin-left: 8px;
    }

    .detection-info {
      display: flex;
      gap: 16px;
      align-items: flex-start;
    }

    .bbox-preview {
      position: relative;
      border: 1px solid #ccc;
      background-color: #f5f5f5;
      border-radius: 4px;
      overflow: hidden;
    }

    .bbox-overlay {
      
      stroke: #1976d2; stroke-width: 2;
      fill: rgba(25, 118, 210, 0.2);
      pointer-events: none;
    }

    .detection-details {
      flex: 1;
    }

    .detection-details p {
      margin: 4px 0;
      font-size: 0.9em;
    }

    .actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 20px;
    }

    .loading {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px;
      gap: 16px;
    }

    .loading p {
      color: #666;
      font-size: 1.1em;
    }
  `]
})
export class DetectionSelectorComponent {
  @Input() detections: DetectionResult | null = null;
  @Input() loading = false;
  @Input() imageUrl: string | null = null;

  @Output() detectionSelected = new EventEmitter<number>();
  @Output() selectionConfirmed = new EventEmitter<number>();

  selectedDetectionId: number | null = null;
  previewWidth = 150;
  previewHeight = 100;

  selectDetection(detectionId: number) {
    this.selectedDetectionId = detectionId;
    this.detectionSelected.emit(detectionId);
  }

  confirmSelection(detectionId: number) {
    this.selectionConfirmed.emit(detectionId);
  }

  cancelSelection() {
    this.selectedDetectionId = null;
  }

  getScaledX(x: number): number {
    if (!this.detections) return 0;
    return (x / this.detections.image_size.width) * this.previewWidth;
  }

  getScaledY(y: number): number {
    if (!this.detections) return 0;
    return (y / this.detections.image_size.height) * this.previewHeight;
  }

  getScaledWidth(bbox: number[]): number {
    if (!this.detections) return 0;
    const width = bbox[2] - bbox[0];
    return (width / this.detections.image_size.width) * this.previewWidth;
  }

  getScaledHeight(bbox: number[]): number {
    if (!this.detections) return 0;
    const height = bbox[3] - bbox[1];
    return (height / this.detections.image_size.height) * this.previewHeight;
  }

  getScaledPolygon(segmentation: number[][] | undefined): string {
    if (!this.detections || !segmentation?.length) return '';
    return segmentation
      .map(([x, y]) => `${(x / this.detections!.image_size.width) * this.previewWidth},${(y / this.detections!.image_size.height) * this.previewHeight}`)
      .join(' ');
  }
}




