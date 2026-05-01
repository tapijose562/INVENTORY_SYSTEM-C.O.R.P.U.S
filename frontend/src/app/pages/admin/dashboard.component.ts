import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="admin-dashboard">
      <h1>Admin Dashboard</h1>
      <p>Acciones rápidas:</p>
      <ul>
        <li><a routerLink="/admin/products">Manage Products</a></li>
        <li><a routerLink="/admin/training">Training</a></li>
        <li><a routerLink="/admin/detection">Detection</a></li>
      </ul>
    </div>
  `
})
export class DashboardComponent {}
