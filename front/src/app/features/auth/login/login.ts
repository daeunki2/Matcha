import { Component, computed, inject, signal } from '@angular/core';
import { AuthLayout } from '../auth-layout/auth-layout';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth/auth.service';
import { debounce, email, form, FormField, required } from '@angular/forms/signals';
import { password } from '../shared/password.validator';

interface LoginForm {
  email: string;
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
    email: '',
    password: '',
  });

  protected form = form(this.loginModel, (schemaPath) => {
    debounce(schemaPath.email, 500);
    required(schemaPath.email, { message: 'Email is required.' });
    email(schemaPath.email, { message: 'Email format is invalid.' });

    debounce(schemaPath.password, 500);
    required(schemaPath.password, { message: 'Password is required.' });
  });

  protected emailErrors = computed(() => this.form.email().touched() ? this.form.email().errors() : []);
  protected passwordErrors = computed(() => this.form.password().touched() ? this.form.password().errors() : []);

  protected onSubmit(event: Event) {
    event.preventDefault();

    if (this.form().invalid()) {
      console.error('Form is invalid');
      return;
    }
    
    const { email, password } = this.form().value();

    this.authService.login(email!, password!).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        console.error('Login failed', error);
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
