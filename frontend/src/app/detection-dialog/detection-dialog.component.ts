import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { DetectionSelectorComponent } from '../detection-selector/detection-selector.component';
import { DetectionService, DetectionResult, DetectionResponse } from '../services/detection.service';

export interface DetectionDialogData {
  imageFile: File;
  imageUrl: string;
  useCorpus?: boolean;
}

@Component({
  selector: 'app-detection-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    DetectionSelectorComponent
  ],
  template: `
    <div class="detection-dialog">
      <h2 mat-dialog-title>Selección Manual de Detección</h2>

      <mat-dialog-content>
        <div class="image-preview">
          <img [src]="data.imageUrl" alt="Imagen a analizar" class="preview-image">
        </div>

        <app-detection-selector
          *ngIf="!loading && detections"
          [detections]="detections"
          [loading]="false"
          [imageUrl]="data.imageUrl"
          (detectionSelected)="onDetectionSelected($event)"
          (selectionConfirmed)="onSelectionConfirmed($event)"
        ></app-detection-selector>

        <div class="loading-container" *ngIf="loading">
          <mat-spinner></mat-spinner>
          <p>Analizando imagen y obteniendo detecciones...</p>
        </div>
      </mat-dialog-content>

      <mat-dialog-actions align="end">
        <button mat-button (click)="onCancel()">Cancelar</button>
        <button mat-raised-button color="primary" [disabled]="!selectedDetectionId" (click)="confirmSelection()">
          Confirmar Selección
        </button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .detection-dialog {
      min-width: 600px;
      max-width: 90vw;
      max-height: 90vh;
    }

    .image-preview {
      text-align: center;
      margin-bottom: 20px;
    }

    .preview-image {
      max-width: 100%;
      max-height: 300px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px;
      gap: 16px;
    }

    .loading-container p {
      color: #666;
      font-size: 1.1em;
    }

    mat-dialog-actions {
      padding: 16px 24px;
    }
  `]
})
export class DetectionDialogComponent implements OnInit {
  detections: DetectionResult | null = null;
  loading = true;
  selectedDetectionId: number | null = null;

  constructor(
    public dialogRef: MatDialogRef<DetectionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: DetectionDialogData,
    private detectionService: DetectionService
  ) {}

  ngOnInit() {
    this.loadDetections();
  }

  loadDetections() {
    this.loading = true;
    const useCorpus = !!this.data.useCorpus;
    this.detectionService.getAllDetections(this.data.imageFile, useCorpus).subscribe({
      next: (result) => {
        this.detections = result;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading detections:', error);
        this.loading = false;
        // Fallback to automatic detection
        this.fallbackToAutoDetection();
      }
    });
  }

  onDetectionSelected(detectionId: number) {
    this.selectedDetectionId = detectionId;
  }

  onSelectionConfirmed(detectionId: number) {
    this.selectedDetectionId = detectionId;
    this.confirmSelection();
  }

  confirmSelection() {
    if (this.selectedDetectionId === null) return;

    this.loading = true;
    const useCorpus = !!this.data.useCorpus;
    this.detectionService.detectFromSelection(this.data.imageFile, this.selectedDetectionId, useCorpus).subscribe({
      next: (result: DetectionResponse) => {
        this.loading = false;
        this.dialogRef.close(result);
      },
      error: (error) => {
        console.error('Error processing selection:', error);
        this.loading = false;
        // Fallback to automatic detection
        this.fallbackToAutoDetection();
      }
    });
  }

  fallbackToAutoDetection() {
    this.detectionService.detectFromImage(this.data.imageFile).subscribe({
      next: (result) => {
        this.dialogRef.close(result);
      },
      error: (error) => {
        console.error('Error in fallback detection:', error);
        this.dialogRef.close(null);
      }
    });
  }

  onCancel() {
    this.dialogRef.close(null);
  }
}