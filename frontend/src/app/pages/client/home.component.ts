import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ProductService } from '../../services/product.service';

@Component({
  selector: 'app-client-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  userFirstName = 'Cliente';
  totalProducts = 0;
  totalBrands = 0;
  bestConfidence = 0;
  featuredProducts: any[] = [];

  constructor(
    private authService: AuthService,
    private productService: ProductService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadUserInfo();
    this.loadDashboardStats();
  }

  loadUserInfo(): void {
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.userFirstName = user.full_name?.split(' ')[0] || user.username || 'Cliente';
      }
    });
  }

  loadDashboardStats(): void {
    this.productService.getProducts().subscribe({
      next: (products: any) => {
        this.totalProducts = products.length;
        
        // Calculate unique brands
        const brands = new Set(products.map((p: any) => p.brand));
        this.totalBrands = brands.size;
        
        // Find best confidence
        this.bestConfidence = Math.max(
          ...products.map((p: any) => p.yolo_confidence || 0),
          0
        );
        
        // Get featured products (top 3 by confidence)
        this.featuredProducts = products
          .sort((a: any, b: any) => (b.yolo_confidence || 0) - (a.yolo_confidence || 0))
          .slice(0, 3);
      },
      error: (err) => {
        console.error('Error loading products:', err);
      }
    });
  }

  navigateTo(path: string): void {
    this.router.navigate([path]);
  }

  onImageError(event: any): void {
    event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"%3E%3Crect fill="%23f3f4f6" width="100" height="100"/%3E%3Ctext x="50" y="50" text-anchor="middle" dy=".3em" fill="%239ca3af"%3E📷%3C/text%3E%3C/svg%3E';
  }

  logout(): void {
    this.authService.logout();
  }
}

