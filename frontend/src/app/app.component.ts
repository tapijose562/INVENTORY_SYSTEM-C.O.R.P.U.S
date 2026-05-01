import { Component, OnInit } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd, Event } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AsyncPipe } from '@angular/common';
import { filter } from 'rxjs/operators';
import { NavbarComponent } from './components/navbar/navbar.component';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, AsyncPipe, NavbarComponent],
  template: `
    <app-navbar *ngIf="showNavbar"></app-navbar>
    <div *ngIf="auth.isLoading$ | async" class="global-loading">
      <div class="spinner">⏳ Cargando usuario...</div>
    </div>
    <router-outlet></router-outlet>
  `,
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'Inventory Corpus v2';
  showNavbar = true;
  private hiddenRoutes = [
    '/login',
    '/register',
    '/register-client',
    '/client/home',
    '/client/detection',
    '/client/products',
    '/client/profile',
    '/admin/dashboard',
    '/admin/detection',
    '/admin/products',
    '/admin/training'
  ];

  constructor(public auth: AuthService, private router: Router) {}

  ngOnInit(): void {
    // Load user info if token exists
    if (this.auth.getToken()) {
      this.auth.updateCurrentUser();
    }

    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: Event) => {
      const navEvent = event as NavigationEnd;
      const path = navEvent.urlAfterRedirects.split('?')[0];
      this.showNavbar = !this.hiddenRoutes.includes(path);
    });
  }
}
