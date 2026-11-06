import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, map } from 'rxjs';

interface User {
  id: number;
  username: string;
  email: string;
  firstname: string;
  lastname: string;
}

interface AuthResponse {
  accessToken: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private http = inject(HttpClient);

  private readonly API_URL = '/api/auth';

  private _user = signal<User | null>(null);
  private _accessToken = signal<string | null>(null);

  public readonly user = this._user.asReadonly();
  public readonly accessToken = this._accessToken.asReadonly();

  public readonly isAuthenticated = computed(
    () => this._user() !== null && this._accessToken() !== null
  );

  public login(email: string, password: string): Observable<User> {

    return this.http.post<AuthResponse>(
      `${this.API_URL}/login`,
      { email, password }
    ).pipe(
      tap(response => {
        this._accessToken.set(response.accessToken);
        this._user.set(response.user);
      }),
      map(response => response.user)
    );
  }

  public signup(firstname: string, lastname: string, username: string, email: string, password: string): Observable<User> {

	return this.http.post<AuthResponse>(
      `${this.API_URL}/signup`,
      { first_name: firstname, last_name: lastname, username, email, password }
    ).pipe(
      tap(response => {
        this._accessToken.set(response.accessToken);
        this._user.set(response.user);
      }),
      map(response => response.user)
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
    this._accessToken.set(null);
  }
}