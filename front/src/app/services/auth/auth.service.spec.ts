import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;
  let httpTestingController: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(AuthService);
    httpTestingController = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTestingController.verify());

  it('logs in with a username and loads the current user', () => {
    let loadedUsername: string | undefined;

    service.login('matcha-user', 'Password123!').subscribe(user => {
      loadedUsername = user.username;
    });

    const loginRequest = httpTestingController.expectOne('/api/auth/login');
    expect(loginRequest.request.method).toBe('POST');
    expect(loginRequest.request.body).toEqual({
      username: 'matcha-user',
      password: 'Password123!',
    });
    expect(loginRequest.request.withCredentials).toBe(true);
    loginRequest.flush({ message: 'Login successful.' });

    const currentUserRequest = httpTestingController.expectOne('/api/auth/me');
    currentUserRequest.flush({
      id: 1,
      username: 'matcha-user',
      email: 'user@example.com',
      first_name: 'Matcha',
      last_name: 'User',
      is_verified: true,
    });

    expect(loadedUsername).toBe('matcha-user');
    expect(service.isAuthenticated()).toBe(true);
  });

  it('sends the backend reset-password field name', () => {
    service.resetPassword('reset-token', 'NewPassword123!').subscribe();

    const request = httpTestingController.expectOne('/api/auth/reset-password');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      token: 'reset-token',
      password: 'NewPassword123!',
    });
    request.flush({ message: 'Password reset successfully.' });
  });
});
