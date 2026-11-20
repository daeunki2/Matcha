import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { AuthLayout } from '../auth-layout/auth-layout';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth/auth.service';
import { debounce, form, FormField, required } from '@angular/forms/signals';

interface LoginForm {
  username: string;
  password: string;
}

@Component({
  imports: [AuthLayout, FormField],
  selector: 'app-login',
  styleUrl: './login.scss',
  templateUrl: './login.html',
})
export class Login {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  protected loginModel = signal<LoginForm>({
    username: '',
    password: '',
  });

  protected form = form(this.loginModel, (schemaPath) => {
    debounce(schemaPath.username, 500);
    required(schemaPath.username, { message: 'Username is required.' });

    debounce(schemaPath.password, 500);
    required(schemaPath.password, { message: 'Password is required.' });
  });

  protected usernameErrors = computed(() => this.form.username().touched() ? this.form.username().errors() : []);
  protected passwordErrors = computed(() => this.form.password().touched() ? this.form.password().errors() : []);
  protected readonly errorMessage = signal('');
  protected readonly isSubmitting = signal(false);

  protected onSubmit(event: Event) {
    event.preventDefault();

    if (this.form().invalid()) {
      return;
    }
    
    const { username, password } = this.form().value();
    this.errorMessage.set('');
    this.isSubmitting.set(true);

    this.authService.login(username!, password!).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (error: unknown) => {
        this.isSubmitting.set(false);
        if (error instanceof HttpErrorResponse && error.status === 401) {
          this.errorMessage.set('Invalid username or password.');
        } else if (error instanceof HttpErrorResponse && error.status === 403) {
          this.errorMessage.set('Please verify your email before logging in.');
        } else if (error instanceof HttpErrorResponse && error.status === 429) {
          this.errorMessage.set('Too many login attempts. Please try again later.');
        } else {
          this.errorMessage.set('Unable to log in right now. Please try again later.');
        }
      }
    });
  }

  protected loginWithGoogle() {
    console.log('Login with Google clicked');
  }
  
  protected loginWith42() {
    console.log('Login with 42 clicked');
  }
}
