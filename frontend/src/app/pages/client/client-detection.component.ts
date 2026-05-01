import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DetectionService } from '../../services/detection.service';

@Component({
  selector: 'app-client-detection',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './client-detection.component.html',
  styleUrls: ['./client-detection.component.scss']
})
export class ClientDetectionComponent implements OnInit {
  @ViewChild('clientWebcam') clientWebcam?: ElementRef<HTMLVideoElement>;

  selectedFile: File | null = null;
  imagePreview: string | null = null;
  loading = false;
  error: string | null = null;
  result: any = null;
  summary: string | null = null;
  sizes: string[] = [];
  useCorpusModel = false;
  corpusStatus: any = null;
  realtimeModeActive = false;
  realtimeStatusMessage = 'Presiona el botón para iniciar la detección en tiempo real.';
  webcamActive = false;
  webcamStream: MediaStream | null = null;

  constructor(private detectionService: DetectionService) {}

  ngOnInit(): void {
    this.checkCorpusStatus();
  }

  onFileChange(event: Event): void {
    this.error = null;
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      this.result = null;
      const reader = new FileReader();
      reader.onload = () => {
        this.imagePreview = reader.result as string;
      };
      reader.readAsDataURL(this.selectedFile);
    }
  }

  startRealtimeDetection(): void {
    this.realtimeModeActive = true;
    this.error = null;
    this.realtimeStatusMessage = 'Iniciando cámara... por favor permite el acceso al sensor de video.';

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      this.error = 'Este navegador no soporta el acceso a la cámara.';
      this.realtimeModeActive = false;
      return;
    }

    navigator.mediaDevices
      .getUserMedia({
        video: {
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      })
      .then(stream => {
        this.webcamStream = stream;
        this.webcamActive = true;
        this.realtimeStatusMessage = 'Cámara activa. Ya puedes ver el feed en vivo.';

        setTimeout(() => {
          if (this.clientWebcam?.nativeElement) {
            this.clientWebcam.nativeElement.srcObject = stream;
            this.clientWebcam.nativeElement.play().catch(() => {});
          }
        }, 100);
      })
      .catch(err => {
        this.error = 'No se pudo activar la cámara: ' + (err?.message || err);
        this.realtimeModeActive = false;
        this.webcamActive = false;
        this.webcamStream = null;
      });
  }

  stopRealtimeDetection(): void {
    if (this.webcamStream) {
      this.webcamStream.getTracks().forEach(track => track.stop());
    }
    this.webcamStream = null;
    this.webcamActive = false;
    this.realtimeModeActive = false;
    this.realtimeStatusMessage = 'Detección en tiempo real detenida.';
  }

  checkCorpusStatus(): void {
    this.detectionService.getCorpusStatus().subscribe({
      next: (status) => {
        this.corpusStatus = status;
        this.useCorpusModel = status?.available ?? false;
      },
      error: (err) => {
        console.error('Error comprobando estado del corpus:', err);
        this.corpusStatus = { available: false, error: err?.message || 'No se pudo verificar el estado del modelo' };
        this.useCorpusModel = false;
      }
    });
  }

  submitDetection(): void {
    if (!this.selectedFile) {
      this.error = 'Selecciona una imagen primero.';
      return;
    }

    this.loading = true;
    this.error = null;
    this.result = null;
    this.summary = null;

    const detect$ = this.useCorpusModel && this.corpusStatus?.available
      ? this.detectionService.detectWithCorpus(this.selectedFile)
      : this.detectionService.detectFromImage(this.selectedFile, false);

    detect$.subscribe({
      next: (payload: any) => {
        this.result = this.mapBackendResult(payload);
        this.summary = this.buildSummaryFromResult(this.result);
        this.sizes = this.result.suggested_size ? [this.result.suggested_size] : [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Error en detección:', err);
        this.error = err?.error?.detail || 'Error al detectar la imagen';
        this.loading = false;
      }
    });
  }

  private buildSummaryFromResult(result: any): string {
    const brand = result.brand || result.detection_class || 'Zapatillas';
    const colors = result.colors || result.color || 'colores no detectados';
    const size = result.size || result.suggested_size || 'talla no detectada';
    return `${brand} · ${colors} · Talla: ${size}`;
  }

  private mapBackendResult(payload: any): any {
    if (!payload) {
      return null;
    }

    return {
      name: payload.name || payload.detection_class || payload.brand || 'Desconocido',
      brand: payload.brand || 'No detectada',
      confidence: payload.confidence ?? 0,
      colors: payload.colors || payload.color || 'No detectados',
      detected_text: payload.detected_text || payload.text || '',
      suggested_price: payload.suggested_price ?? payload.price ?? null,
      price: payload.price ?? null,
      size: payload.size || payload.suggested_size || null,
      stock: payload.stock ?? null,
      detection_class: payload.detection_class || payload.name || 'Desconocido'
    };
  }
}
