import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { AdminGuard } from './guards/admin.guard';
import { ClientGuard } from './guards/client.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./pages/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'register-client',
    loadComponent: () => import('./pages/register-client/register-client.component').then(m => m.RegisterClientComponent)
  },
  {
    path: 'admin',
    canActivate: [AuthGuard, AdminGuard],
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent)
      },
      {
        path: 'training',
        loadComponent: () => import('./pages/training/training.component').then(m => m.TrainingComponent)
      },
      {
        path: 'detection',
        loadComponent: () => import('./pages/detection/detection.component').then(m => m.DetectionComponent)
      },
      {
        path: 'products',
        loadComponent: () => import('./pages/products/products.component').then(m => m.ProductsComponent)
      }
    ]
  },
  {
    path: 'client',
    canActivate: [AuthGuard, ClientGuard],
    loadComponent: () => import('./pages/client/client-layout.component').then(m => m.ClientLayoutComponent),
    children: [
      {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full'
      },
      {
        path: 'home',
        loadComponent: () => import('./pages/client/home.component').then(m => m.HomeComponent)
      },
      {
        path: 'detection',
        loadComponent: () => import('./pages/client/client-detection.component').then(m => m.ClientDetectionComponent)
      },
      {
        path: 'products',
        loadComponent: () => import('./pages/client/client-products.component').then(m => m.ClientProductsComponent)
      },
      {
        path: 'profile',
        loadComponent: () => import('./pages/client/client-profile.component').then(m => m.ClientProfileComponent)
      }
    ]
  },
  {
    path: 'batch-detection',
    loadComponent: () => import('./pages/detection/batch-detection.component').then(m => m.BatchDetectionComponent),
    canActivate: [AuthGuard]
  }
];
