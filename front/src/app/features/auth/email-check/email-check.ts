import { afterNextRender, Component, computed, inject, signal, WritableSignal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../../services/auth/auth.service';
import { AuthLayout } from '../auth-layout/auth-layout';
import { email, form, FormField, required } from '@angular/forms/signals';
import { NotificationService } from '../../../shared/services/notification.service';

@Component({
  imports: [AuthLayout, FormField],
  selector: 'app-email-check',
  styleUrl: './email-check.scss',
  templateUrl: './email-check.html',
})
export class EmailCheck {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);

  protected readonly status: WritableSignal<'success' | 'pending' | 'error' | 'errorMail' | 'resent'> = signal('pending');

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
        this.router.navigate(['/login']);
        return;
      }

      this.authService.verifyEmail(token).subscribe({
        next: () => {
          this.status.set('success');
          setTimeout(() => this.router.navigate(['/my-profile']), 3000)
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
      console.log("Form is invalid", this.form().errors());
    }
    const { email } = this.form().value();

    this.authService.resendVerificationEmail(email!).subscribe({
      next: () => {
        this.notificationService.showSuccess('Email sent ! Please check your email to verify your account.');
        this.status.set('resent');
      },
      error: () => {
        this.status.set('errorMail');
      }
    });
  }
}
