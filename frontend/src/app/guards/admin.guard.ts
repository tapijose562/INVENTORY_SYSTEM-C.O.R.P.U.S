import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { map, first, switchMap, filter } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AdminGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(_route: ActivatedRouteSnapshot, _state: RouterStateSnapshot): Observable<boolean> {
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/login']);
      return of(false);
    }

    // Wait until loading completes, then check currentUser
    return this.auth.isLoading$.pipe(
      // proceed when not loading
      filter(isLoading => isLoading === false),
      first(),
      switchMap(() => this.auth.currentUser$.pipe(
        first(),
        map(user => {
          if (!user) {
            this.router.navigate(['/login']);
            return false;
          }
          if (user.role === 'admin') {
            return true;
          }
          // Non-admins should be redirected to products (comprador view)
          this.router.navigate(['/products']);
          return false;
        })
      ))
    );
  }
}
