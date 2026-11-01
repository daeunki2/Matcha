import { Component, inject } from '@angular/core';
import { AuthLayout } from '../auth-layout/auth-layout';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { passwordValidator } from '../shared/password.validator';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth/auth.service';

@Component({
  imports: [AuthLayout, ReactiveFormsModule, MatButtonModule],
  selector: 'app-signup',
  styleUrl: './signup.scss',
  templateUrl: './signup.html',
})
export class Signup {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  protected form = new FormGroup({
    'lastname': new FormControl('', [Validators.required]),
    'firstname': new FormControl('', [Validators.required]),
    'username': new FormControl('', [Validators.required]),
    'email': new FormControl('', [Validators.required, Validators.email]),
    'password': new FormControl('', [Validators.required, passwordValidator]),
  });

  protected onSubmit() {
    this.form.markAllAsTouched();
    if (this.form.invalid) {
      console.error('Form is invalid');
      return;
    }
    
    const { firstname, lastname, username, email, password } = this.form.getRawValue();

    this.authService.signup(firstname!, lastname!, username!, email!, password!).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        console.error('Signup failed', error);
      }
    });
  }
}
