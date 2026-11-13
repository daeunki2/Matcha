import { Component, computed, signal } from '@angular/core';
import { AuthLayout } from '../auth-layout/auth-layout';
import { email, form, FormField, required } from '@angular/forms/signals';

@Component({
  imports: [AuthLayout, FormField],
  selector: 'app-forgot-password',
  styleUrl: './forgot-password.scss',
  templateUrl: './forgot-password.html',
})
export class ForgotPassword {
  private emailModel = signal<{ email: string }>({ email: '' });

  protected form = form(this.emailModel, (schemaPath) => {
    required(schemaPath.email, { message: 'Email is required.' });
    email(schemaPath.email, { message: 'Email format is invalid.' });
  });

  protected emailErrors = computed(() => this.form.email().touched() ? this.form.email().errors() : []);

  protected onSubmit(event: Event) {
    event.preventDefault();

    if (this.form().invalid()) {
      console.log('Form is invalid');
      return;
    }
    console.log('Forgot password for email:', this.form.email().value());
  }
}
