import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { AuthLayout } from '../auth-layout/auth-layout';
import { email, form, FormField, required } from '@angular/forms/signals';
import { AuthService } from '../../../services/auth/auth.service';

@Component({
  imports: [AuthLayout, FormField],
  selector: 'app-forgot-password',
  styleUrl: './forgot-password.scss',
  templateUrl: './forgot-password.html',
})
export class ForgotPassword {
  private readonly authService = inject(AuthService);
  private emailModel = signal<{ email: string }>({ email: '' });
  protected readonly status = signal<'idle' | 'sending' | 'success' | 'error'>('idle');
  protected readonly errorMessage = signal('');

  protected form = form(this.emailModel, (schemaPath) => {
    required(schemaPath.email, { message: 'Email is required.' });
    email(schemaPath.email, { message: 'Email format is invalid.' });
  });

  protected emailErrors = computed(() => this.form.email().touched() ? this.form.email().errors() : []);

  protected onSubmit(event: Event) {
    event.preventDefault();

    if (this.form().invalid()) {
      return;
    }
    this.status.set('sending');
    this.errorMessage.set('');
    this.authService.forgotPassword(this.form.email().value()).subscribe({
      next: () => this.status.set('success'),
      error: (error: unknown) => {
        this.status.set('error');
        this.errorMessage.set(
          error instanceof HttpErrorResponse && error.status === 429
            ? 'Too many requests. Please try again later.'
            : 'Unable to send a recovery email right now. Please try again later.'
        );
      }
    });
  }
}
