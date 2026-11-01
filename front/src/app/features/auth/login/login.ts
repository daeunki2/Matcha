import { Component, inject } from '@angular/core';
import { AuthLayout } from '../auth-layout/auth-layout';
import { MatButtonModule } from '@angular/material/button';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { passwordValidator } from '../shared/password.validator';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth/auth.service';

@Component({
  imports: [AuthLayout, MatButtonModule, ReactiveFormsModule],
  selector: 'app-login',
  styleUrl: './login.scss',
  templateUrl: './login.html',
})
export class Login {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  protected form = new FormGroup({  
    'email': new FormControl('', [Validators.required, Validators.email]),
    'password': new FormControl('', [Validators.required, passwordValidator]),
  });

  protected onSubmit() {
    this.form.markAllAsTouched();
    if (this.form.invalid) {
      console.error('Form is invalid');
      return;
    }
    
    const { email, password } = this.form.getRawValue();

    this.authService.login(email!, password!).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        console.error('Login failed', error);
      }
    });
  }
}
