import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { AuthService } from '../../../services/auth/auth.service';
import { NotificationService } from '../../../shared/services/notification.service';

@Component({
  imports: [RouterLink, RouterOutlet],
  selector: 'app-main-layout',
  styleUrl: './main-layout.scss',
  templateUrl: './main-layout.html',
})
export class MainLayout {
  protected readonly authService = inject(AuthService);
  protected readonly currentYear = new Date().getFullYear();
  protected readonly isLoggingOut = signal(false);

  private readonly router = inject(Router);
  private readonly notificationService = inject(NotificationService);

  protected logout(): void {
    if (this.isLoggingOut()) {
      return;
    }

    this.isLoggingOut.set(true);
    this.authService.logout().subscribe({
      next: () => {
        this.isLoggingOut.set(false);
        void this.router.navigate(['/login']);
      },
      error: () => {
        this.isLoggingOut.set(false);
        this.notificationService.showError('Unable to complete logout. Please try again.');
        void this.router.navigate(['/login']);
      },
    });
  }
}
