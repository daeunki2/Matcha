import { Component } from '@angular/core';
import { AuthLayout } from '../auth-layout/auth-layout';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  imports: [AuthLayout, ReactiveFormsModule],
  selector: 'app-forgot-password',
  styleUrl: './forgot-password.scss',
  templateUrl: './forgot-password.html',
})
export class ForgotPassword {
  protected form = new FormGroup({
    'email': new FormControl('', [Validators.required, Validators.email]),
  });

  protected onSubmit() {
    this.form.markAllAsTouched();
    if (this.form.invalid) {
      console.log('Form is invalid');
      return;
    }
    console.log('Forgot password for email:', this.form.value.email);
  }
}
