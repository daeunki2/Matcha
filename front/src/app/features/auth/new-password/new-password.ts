import { HttpErrorResponse } from '@angular/common/http';
import { afterNextRender, Component, computed, inject, signal, WritableSignal } from '@angular/core';
import { form, required, FormField } from '@angular/forms/signals';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../services/auth/auth.service';
import { password } from '../shared/password.validator';
import { AuthLayout } from '../auth-layout/auth-layout';

@Component({
  imports: [AuthLayout, FormField],
  selector: 'app-new-password',
  styleUrl: './new-password.scss',
  templateUrl: './new-password.html',
})
export class NewPassword {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly authService = inject(AuthService);

  private readonly token: WritableSignal<string | null> = signal(null);
  protected readonly status = signal<'idle' | 'success' | 'error'>('idle');
  protected readonly errorMessage = signal('');
  protected readonly isSubmitting = signal(false);

  private passwordModel = signal<{ password: string }>({ password: '' });

  protected form = form(this.passwordModel, (schemaPath) => {
    required(schemaPath.password, { message: 'Password is required.' });
    password(schemaPath.password);
  });

  protected passwordErrors = computed(() => this.form.password().touched() ? this.form.password().errors() : []);

  constructor() {
    afterNextRender(() => {
      this.token.set(this.route.snapshot.queryParamMap.get('token'));

      if (!this.token()) {
        this.router.navigate(['/login']);
        return;
      }
    })
  }

  protected resetPassword(event: Event) {
    event.preventDefault();

    if (this.form().invalid()) {
      return;
    }
    const token = this.token();
    if (!token) {
      this.errorMessage.set('This password reset link is invalid or expired. Please request a new one.');
      this.status.set('error');
      return;
    }
    const { password } = this.form().value();
    this.isSubmitting.set(true);
    this.errorMessage.set('');

    this.authService.resetPassword(token, password!).subscribe({
      next: () => {
        this.status.set('success');
        this.isSubmitting.set(false);
      },
      error: (error: unknown) => {
        this.isSubmitting.set(false);
        this.status.set('error');
        if (error instanceof HttpErrorResponse && error.status === 429) {
          this.errorMessage.set('Too many requests. Please try again later.');
        } else if (error instanceof HttpErrorResponse && error.status === 400 && typeof error.error?.message === 'string') {
          this.errorMessage.set(error.error.message);
        } else {
          this.errorMessage.set('This password reset link is invalid or expired. Please request a new one.');
        }
      }
    });
  }
}
