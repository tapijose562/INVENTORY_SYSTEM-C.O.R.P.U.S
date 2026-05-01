import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

interface TrainingSession {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
  epochs: number;
  batch_size: number;
  learning_rate: number;
  progress: number;
  loss: number;
  accuracy: number;
  val_loss?: number;
  val_accuracy?: number;
}

@Component({
  selector: 'app-training',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './training.component.html',
  styleUrls: ['./training.component.scss']
})
export class TrainingComponent implements OnInit {
  activeSessions: TrainingSession[] = [];
  sessionsHistory: TrainingSession[] = [];
  isTraining = false;
  filterText = '';

  trainingConfig = {
    epochs: 100,
    batch_size: 32,
    learning_rate: 0.001,
    use_gpu: false
  };

  constructor(private authService: AuthService) { }

  ngOnInit(): void {
    this.loadSessions();
    // Reload every 5 seconds if training is active
    setInterval(() => {
      if (this.isTraining) {
        this.loadSessions();
      }
    }, 5000);
  }

  startTraining(): void {
    this.isTraining = true;
    console.log('Starting training with config:', this.trainingConfig);
    
    // In production, this would call a backend endpoint
    // this.trainingService.startTraining(this.trainingConfig).subscribe(...);
    
    // Mock active session
    const mockSession: TrainingSession = {
      id: 'session_' + Date.now(),
      status: 'running',
      created_at: new Date().toISOString(),
      epochs: this.trainingConfig.epochs,
      batch_size: this.trainingConfig.batch_size,
      learning_rate: this.trainingConfig.learning_rate,
      progress: 0,
      loss: 0.5,
      accuracy: 0.8
    };

    this.activeSessions = [mockSession];
    this.simulateTrainingProgress(mockSession);
  }

  pauseTraining(): void {
    if (this.activeSessions.length > 0) {
      this.activeSessions[0].status = 'pending';
    }
  }

  stopTraining(): void {
    if (this.activeSessions.length > 0) {
      const session = this.activeSessions[0];
      session.status = 'completed';
      session.completed_at = new Date().toISOString();
      this.sessionsHistory.unshift(session);
      this.activeSessions = [];
      this.isTraining = false;
    }
  }

  loadSessions(): void {
    // In production: this.trainingService.getSessions().subscribe(...)
    console.log('Loading sessions...');
  }

  downloadModel(session: TrainingSession): void {
    console.log('Downloading model:', session.id);
    // In production: this.trainingService.downloadModel(session.id)
  }

  deployModel(session: TrainingSession): void {
    console.log('Deploying model:', session.id);
    // In production: this.trainingService.deployModel(session.id)
  }

  calculateDuration(start: string, end: string): string {
    const startTime = new Date(start).getTime();
    const endTime = new Date(end).getTime();
    const diffMs = endTime - startTime;
    const diffMins = Math.floor(diffMs / 60000);
    return `${diffMins} minutes`;
  }

  private simulateTrainingProgress(session: TrainingSession): void {
    const interval = setInterval(() => {
      if (session.progress < 100 && session.status === 'running') {
        session.progress += Math.random() * 15;
        session.loss *= 0.95;
        session.accuracy += 0.01;
      } else {
        clearInterval(interval);
      }
    }, 2000);
  }

  logout(): void {
    this.authService.logout();
  }
}
