import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProductService } from '../../services/product.service';

@Component({
  selector: 'app-client-products',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './client-products.component.html',
  styleUrls: ['./client-products.component.scss']
})
export class ClientProductsComponent implements OnInit {
  products: any[] = [];
  filteredProducts: any[] = [];
  brands: string[] = [];
  colors: string[] = [];
  searchQuery = '';
  selectedBrand = '';
  selectedColor = '';
  page = 1;
  pageSize = 12;

  constructor(private productService: ProductService) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.productService.getProducts(0, 200).subscribe({
      next: (data: any) => {
        this.products = data || [];
        // Parse colors and sizes from string to array
        this.products.forEach(p => {
          if (p.colors && typeof p.colors === 'string') {
            p.colors = p.colors.split(' / ').filter((c: string) => c.trim());
          } else if (!p.colors) {
            p.colors = [];
          }
          if (p.size && typeof p.size === 'string') {
            p.size = p.size.split(' / ').filter((s: string) => s.trim());
          } else if (!p.size) {
            p.size = [];
          }
        });
        this.brands = Array.from(new Set(this.products.map(p => p.brand).filter(Boolean)));
        const colorsArray = this.products.flatMap(p => p.colors || []).filter(Boolean);
        this.colors = Array.from(new Set(colorsArray));
        this.applyFilters();
      },
      error: (err) => {
        console.error('Error cargando productos:', err);
      }
    });
  }

  applyFilters(): void {
    this.filteredProducts = this.products.filter(product => {
      const matchesSearch = this.searchQuery
        ? [product.name, product.brand, product.color_primary].some((field: string) => field?.toLowerCase().includes(this.searchQuery.toLowerCase()))
        : true;
      const matchesBrand = this.selectedBrand ? product.brand === this.selectedBrand : true;
      const matchesColor = this.selectedColor ? (product.colors || []).includes(this.selectedColor) : true;
      return matchesSearch && matchesBrand && matchesColor;
    });
    this.page = 1;
  }

  get displayedProducts(): any[] {
    const start = (this.page - 1) * this.pageSize;
    return this.filteredProducts.slice(start, start + this.pageSize);
  }

  get totalPages(): number {
    return Math.ceil(this.filteredProducts.length / this.pageSize);
  }

  nextPage(): void {
    if (this.page * this.pageSize < this.filteredProducts.length) {
      this.page += 1;
    }
  }

  prevPage(): void {
    if (this.page > 1) {
      this.page -= 1;
    }
  }
}
