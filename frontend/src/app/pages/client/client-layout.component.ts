import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterOutlet } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-client-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet],
  template: `
    <div class="client-layout">
      <header class="client-header">
        <div class="brand-group">
          <span class="brand-icon">🛍️</span>
          <div>
            <div class="brand-title">Inventory Corpus</div>
            <div class="brand-subtitle">Tienda de zapatillas</div>
          </div>
        </div>

        <nav class="client-nav">
          <a routerLink="/client/home" routerLinkActive="active">Inicio</a>
          <a routerLink="/client/detection" routerLinkActive="active">Detectar zapatillas</a>
          <a routerLink="/client/products" routerLinkActive="active">Ver catálogo</a>
          <a routerLink="/client/profile" routerLinkActive="active">Mi perfil</a>
          <button type="button" class="logout-button" (click)="logout()">Cerrar sesión</button>
        </nav>
      </header>

      <main class="client-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styleUrls: ['./client-layout.component.scss']
})
export class ClientLayoutComponent {
  constructor(private authService: AuthService) {}

  logout(): void {
    this.authService.logout();
  }
}
