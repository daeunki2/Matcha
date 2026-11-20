import { afterNextRender, Component, computed, inject, signal, WritableSignal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../services/auth/auth.service';
import { AuthLayout } from '../auth-layout/auth-layout';
import { email, form, FormField, required } from '@angular/forms/signals';

@Component({
  imports: [AuthLayout, FormField],
  selector: 'app-email-check',
  styleUrl: './email-check.scss',
  templateUrl: './email-check.html',
})
export class EmailCheck {
  private readonly route = inject(ActivatedRoute);
  private readonly authService = inject(AuthService);

  protected readonly status: WritableSignal<'success' | 'pending' | 'error' | 'errorMail' | 'resent'> = signal('pending');
  protected readonly isResending = signal(false);

  private emailModel = signal<{ email: string }>({ email: '' });

  protected form = form(this.emailModel, (schemaPath) => {
    required(schemaPath.email, { message: 'Email is required.' });
    email(schemaPath.email, { message: 'Email format is invalid.' });
  });

  protected emailErrors = computed(() => this.form.email().touched() ? this.form.email().errors() : []);

  constructor() {
    afterNextRender(() => {
      const token = this.route.snapshot.queryParamMap.get('token');

      if (!token) {
        this.status.set('error');
        return;
      }

      this.authService.verifyEmail(token).subscribe({
        next: () => {
          this.status.set('success');
        },
        error: () => {
          this.status.set('error');
        }
      })
    })
  }

  protected resendEmail(event: Event) {
    event.preventDefault();

    if (this.form().invalid()) {
      return;
    }
    const { email } = this.form().value();
    this.isResending.set(true);

    this.authService.resendVerificationEmail(email!).subscribe({
      next: () => {
        this.status.set('resent');
      },
      error: () => {
        this.status.set('errorMail');
        this.isResending.set(false);
      },
      complete: () => {
        this.isResending.set(false);
      }
    });
  }
}
