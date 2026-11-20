import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { Observable, finalize, switchMap, tap } from 'rxjs';

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  is_verified: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private http = inject(HttpClient);

  private readonly API_URL = '/api/auth';

  private _user = signal<AuthUser | null>(null);
  private _isAuthenticated = signal<boolean | null>(null);

  public readonly user = this._user.asReadonly();
  public readonly isAuthenticated = this._isAuthenticated.asReadonly();

  public userIsNotAuthenticated() {
    this._user.set(null);
    this._isAuthenticated.set(false);
  }

  public login(username: string, password: string): Observable<AuthUser> {
    return this.http.post<void>(
      `${this.API_URL}/login`,
      { username, password },
      { withCredentials: true }
    ).pipe(switchMap(() => this.loadUser()));
  }

  public signup(firstname: string, lastname: string, username: string, email: string, password: string): Observable<HttpResponse<void>> {
    return this.http.post<void>(
        `${this.API_URL}/signup`,
        { first_name: firstname, last_name: lastname, username, email, password },
        { observe: 'response', withCredentials: true }
      );
  }

  public resendVerificationEmail(email: string): Observable<HttpResponse<void>> {
    return this.http.post<void>(
     `${this.API_URL}/resend-verification`,
     { email },
     { observe: 'response', withCredentials: true }
    )
  }

  public verifyEmail(token: string): Observable<HttpResponse<void>> {
    return this.http.post<void>(
     `${this.API_URL}/verify-email`,
     { token },
     { observe: 'response', withCredentials: true }
    )
  }

  public forgotPassword(email: string): Observable<HttpResponse<void>> {
    return this.http.post<void>(
      `${this.API_URL}/forgot-password`,
      { email },
      { observe: 'response', withCredentials: true }
    );
  }

  public resetPassword(token: string, password: string): Observable<HttpResponse<void>> {
    return this.http.post<void>(
      `${this.API_URL}/reset-password`,
      { token, password },
      { observe: 'response', withCredentials: true }
    );
  }

  public refreshSession(): Observable<void> {
    return this.http.post<void>(
      `${this.API_URL}/refresh`,
      {},
      { withCredentials: true }
    );
  }

  public logout(): Observable<void> {
    return this.http.post<void>(
      `${this.API_URL}/logout`,
      {},
      { withCredentials: true }
    ).pipe(
      finalize(() => this.clearSession())
    );
  }

  public loadUser(): Observable<AuthUser> {
    return this.http.get<AuthUser>(`${this.API_URL}/me`, { withCredentials: true }).pipe(
      tap(user => {
        this._user.set(user);
        this._isAuthenticated.set(true);
      })
    );
  }

  private clearSession(): void {
    this._user.set(null);
    this._isAuthenticated.set(false);
  }
}