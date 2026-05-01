import { Component, OnInit } from '@angular/core';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { take } from 'rxjs/operators';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  styleUrls: ['./login.component.scss'],
  template: `
  <div class="login-wrapper">
    <div class="login-box">
      <div class="login-header">
        <span class="eyebrow">Bienvenido a Inventory Corpus</span>
        <h1>Inicia sesión para continuar</h1>
        <p>Accede a tu panel de inventario, detección IA y gestión de zapatillas.</p>
      </div>

      <form (ngSubmit)="login()">
        <div class="form-group">
          <label>Usuario</label>
          <input type="text" [(ngModel)]="username" name="username" required />
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <input type="password" [(ngModel)]="password" name="password" required />
        </div>

        <button type="submit" [disabled]="loading">{{ loading ? 'Ingresando...' : 'Entrar' }}</button>
      </form>

      <p *ngIf="error" class="error">{{ error }}</p>
      <p>¿No tienes cuenta? <a routerLink="/register">Registrarse</a></p>
    </div>
  </div>
  `
})
export class LoginComponent implements OnInit {
  username = '';
  password = '';
  loading = false;
  error = '';
  constructor(private authService: AuthService, private router: Router, private route: ActivatedRoute) {}

  ngOnInit(): void {
    // If a token is provided in the URL as ?token=..., automatically use it
    this.route.queryParams.subscribe(params => {
      const raw = params['token'] || params['t'] || null;
      if (raw) {
        const token = raw.startsWith('Bearer ') ? raw.split(' ')[1] : raw;
        this.authService.setToken(token);
        // allow time to load /me and redirect
        setTimeout(() => this.redirectAfterAuth(), 400);
      } else if (this.authService.getToken()) {
        // Token already exists in storage, try to update user and redirect
        this.authService.updateCurrentUser();
        setTimeout(() => this.redirectAfterAuth(), 400);
      }
    });
  }

  login(): void {
    this.loading = true;
    this.error = '';
    this.authService.login(this.username, this.password).subscribe({
      next: () => {
        // Login successful, wait for user to be loaded and redirect
        this.authService.currentUser$
          .pipe(take(1))
          .subscribe(user => {
            if (user) {
              this.redirectAfterAuth();
            } else {
              this.error = 'No fue posible obtener el usuario';
              this.loading = false;
            }
          });
      },
      error: () => {
        this.error = 'Credenciales inválidas';
        this.loading = false;
      }
    });
  }

  private redirectAfterAuth(): void {
    const user = this.authService.getCurrentUserValue();
    if (user && user.role === 'admin') this.router.navigate(['/admin/dashboard']);
    else if (user) this.router.navigate(['/client/home']);
    else this.loading = false;
  }
}
