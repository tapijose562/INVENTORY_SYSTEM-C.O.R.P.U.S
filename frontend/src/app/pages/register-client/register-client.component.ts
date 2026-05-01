import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register-client',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './register-client.component.html',
  styleUrls: ['./register-client.component.scss']
})
export class RegisterClientComponent {
  username = '';
  email = '';
  fullName = '';
  password = '';
  loading = false;
  error = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) { }

  register(): void {
    this.loading = true;
    this.error = '';

    this.authService.register(this.username, this.email, this.fullName, this.password).subscribe({
      next: () => {
        // After creating a client account, redirect to login
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.error = err?.error?.detail || 'Error creating client account. Please try again.';
        this.loading = false;
      }
    });
  }
}
