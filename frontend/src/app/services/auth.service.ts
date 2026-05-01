import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap, finalize } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/v1/auth';
  private tokenKey = 'access_token';
  private currentUserSubject: BehaviorSubject<any>;
  public currentUser$: Observable<any>;
  private isLoadingSubject: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  public isLoading$: Observable<boolean> = this.isLoadingSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    this.currentUserSubject = new BehaviorSubject<any>(this.getUserFromStorage());
    this.currentUser$ = this.currentUserSubject.asObservable();
  }

  register(username: string, email: string, fullName: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, {
      username,
      email,
      full_name: fullName,
      password
    });
  }

  login(username: string, password: string): Observable<any> {
    return this.http.post<{access_token: string}>(`${this.apiUrl}/login`, { username, password })
      .pipe(
        tap(response => {
          if (response && response.access_token) {
            localStorage.setItem(this.tokenKey, response.access_token);
            console.debug('[AuthService] login stored token', !!response.access_token);
            // Update current user immediately
            this.updateCurrentUser();
          }
        })
      );
  }

  logout(): void {
    // If no token, just clear and navigate
    if (!this.getToken()) {
      localStorage.removeItem(this.tokenKey);
      this.currentUserSubject.next(null);
      this.router.navigate(['/login']);
      return;
    }

    // Try to notify backend (best-effort). interceptor will attach token.
    this.http.post(`${this.apiUrl}/logout`, {})
      .pipe(
        finalize(() => {
          // Always clear local state regardless of backend result
          localStorage.removeItem(this.tokenKey);
          this.currentUserSubject.next(null);
          this.router.navigate(['/login']);
        })
      )
      .subscribe({
        next: () => {},
        error: (err) => console.warn('Logout backend call failed:', err)
      });
  }

  getCurrentUser(): Observable<any> {
    const token = this.getToken();
    if (token) {
      return this.http.get(`${this.apiUrl}/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    return this.http.get(`${this.apiUrl}/me`);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null {
    const t = localStorage.getItem(this.tokenKey);
    console.debug('[AuthService] getToken ->', !!t);
    return t;
  }

  public updateCurrentUser(): void {
    this.isLoadingSubject.next(true);
    const token = this.getToken();
    console.debug('[AuthService] updateCurrentUser token present?', !!token);

    if (!token) {
      console.warn('[AuthService] No token available when calling /me');
      this.currentUserSubject.next(null);
      this.isLoadingSubject.next(false);
      return;
    }

    this.getCurrentUser().subscribe(
      user => {
        console.debug('[AuthService] /me returned:', user);
        this.currentUserSubject.next(user);
        this.isLoadingSubject.next(false);
      },
      error => {
        console.error('Error loading user:', error);
        this.currentUserSubject.next(null);
        this.isLoadingSubject.next(false);
      }
    );
  }

  /**
   * Set a token manually (e.g., pasted token) and refresh current user.
   * Useful for development or token-based login flows.
   */
  public setToken(token: string): void {
    if (!token) return;
    localStorage.setItem(this.tokenKey, token);
    // Update current user immediately
    this.updateCurrentUser();
  }

  // Synchronous access to current user value
  public getCurrentUserValue(): any {
    // @ts-ignore
    return this.currentUserSubject?.value;
  }

  private getUserFromStorage(): any {
    // Do not return a placeholder user object — return null so components
    // wait for the real `/me` response (avoid rendering admin UI prematurely)
    return null;
  }
}
