import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { NotificationService } from '../services/notification.service';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../../services/auth/auth.service';
import { Router } from '@angular/router';

export const httpResponseInterceptor: HttpInterceptorFn = (req, next) => {
	const notificationService = inject(NotificationService);
	const authService = inject(AuthService);
	const router = inject(Router);

  return next(req).pipe(
	catchError((error) => {
		if (error.status === 400) {
			notificationService.showError('Bad Request. Please check your input.');
		} else if (error.status === 401) {
			authService.userIsNotAuthenticated();
			router.createUrlTree(['/login']);
		} else if (error.status === 404) {
			notificationService.showError('Not Found. The requested resource could not be found.');
		} else if (error.status === 429) {
			notificationService.showError('Too Many Requests. Please try again later.');
		} else if (error.status >= 500) {
			notificationService.showError('Server Error. Please try again later.');
		} else {
			notificationService.showError('An unexpected error occurred. Please try again later.');
		}
		return throwError(() => error);
	})
  );
}