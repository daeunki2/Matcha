import { afterNextRender, Component, computed, inject, signal, WritableSignal } from '@angular/core';
import { form, required, FormField } from '@angular/forms/signals';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../services/auth/auth.service';
import { NotificationService } from '../../../shared/services/notification.service';
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
  private readonly notificationService = inject(NotificationService);

  private readonly token: WritableSignal<string | null> = signal(null);

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
      console.log("Form is invalid", this.form().errors());
    }
    const { password } = this.form().value();

    this.authService.resetPassword(this.token()!, password!).subscribe({
      next: () => {
        this.notificationService.showSuccess('Your password was successfully updated!');
        setTimeout(() => this.router.navigate(['/login']), 3000);
        
      },
      error: () => {
        this.notificationService.showSuccess('Error while updating your new password...');
        setTimeout(() => this.router.navigate(['/login']), 3000);
      }
    });
  }
}
