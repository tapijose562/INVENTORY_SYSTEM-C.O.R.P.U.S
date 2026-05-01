import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <nav class="navbar">
      <a routerLink="/">Home</a>
      <a *ngIf="isAdmin" routerLink="/admin/dashboard">Admin</a>
      <a *ngIf="isAuthenticated && !isAdmin" routerLink="/client/home">Client</a>
      <a *ngIf="isAuthenticated" [routerLink]="isAdmin ? '/admin/products' : '/client/products'">Products</a>
      <a *ngIf="isAuthenticated" [routerLink]="isAdmin ? '/admin/detection' : '/client/detection'">Detection</a>
      <button *ngIf="!isAuthenticated" routerLink="/login">Login</button>
      <button *ngIf="isAuthenticated" (click)="logout()">Logout</button>
    </nav>
  `
})
export class NavbarComponent {
  isAuthenticated = false;
  isAdmin = false;
  constructor(private auth: AuthService) {
    this.auth.currentUser$.subscribe(u => {
      this.isAuthenticated = !!u;
      this.isAdmin = !!u && u.role === 'admin';
    });
  }

  logout() {
    this.auth.logout();
  }
}
