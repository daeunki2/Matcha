import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { Observable, tap, map, catchError, throwError } from 'rxjs';
import { NotificationService } from '../../shared/services/notification.service';

interface User {
  id: number;
  username: string;
  email: string;
  firstname: string;
  lastname: string;
  isVerified: boolean;
  profileCompleted: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private http = inject(HttpClient);

  private readonly API_URL = '/api/auth';

  private _user = signal<User | null>(null);
  private _isAuthenticated = signal<boolean | null>(null);

  public readonly user = this._user.asReadonly();
  public readonly isAuthenticated = this._isAuthenticated.asReadonly();

  public userIsNotAuthenticated() {
    this._isAuthenticated.set(false);
  }

  public login(email: string, password: string): Observable<HttpResponse<void>> {

    return this.http.post<void>(
      `${this.API_URL}/login`,
      { email, password },
      { observe: 'response' }
    ).pipe(
      tap((response) => response.status === 202 ? this._isAuthenticated.set(true) : this._isAuthenticated.set(false))
    )
  }

  public signup(firstname: string, lastname: string, username: string, email: string, password: string): Observable<HttpResponse<void>> {
    return this.http.post<void>(
        `${this.API_URL}/signup`,
        { first_name: firstname, last_name: lastname, username, email, password },
        { observe: 'response' }
      );
  }

  public resendVerificationEmail(email: string): Observable<HttpResponse<void>> {
    return this.http.post<void>(
     `${this.API_URL}/resend-verification`,
     { email },
     { observe: 'response' }
    )
  }

  public verifyEmail(token: string): Observable<HttpResponse<void>> {
    return this.http.post<void>(
     `${this.API_URL}/verify-email`,
     { token },
     { observe: 'response' }
    )
  }

  public forgotPassword(email: string): Observable<HttpResponse<void>> {

    return this.http.post<void>(
      `${this.API_URL}/forgot-password`,
      { email },
      { observe: 'response' }
    );
  }

  public resetPassword(token: string, password: string): Observable<HttpResponse<void>> {
    return this.http.post<void>(
      `${this.API_URL}/reset-password`,
      { token, new_password: password },
      { observe: 'response' }
    );
  }

  public logout(): void {

    this.http.post(`${this.API_URL}/logout`, {}).subscribe({
      complete: () => this.clearSession(),
      error: () => this.clearSession()
    });
  }

  public loadUser(): Observable<User> {

    return this.http.get<User>(`${this.API_URL}/me`).pipe(
      tap(user => this._user.set(user))
    );
  }

  private clearSession(): void {
    this._user.set(null);
    this._isAuthenticated.set(null);
  }
}