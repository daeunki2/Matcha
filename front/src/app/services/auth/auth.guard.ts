import { HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { catchError, map, of, switchMap } from 'rxjs';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const loginUrl = router.createUrlTree(['/login']);

  return authService.loadUser().pipe(
    map(() => true),
    catchError((error: unknown) => {
      if (!(error instanceof HttpErrorResponse) || error.status !== 401) {
        return of(loginUrl);
      }

      return authService.refreshSession().pipe(
        switchMap(() => authService.loadUser()),
        map(() => true),
        catchError(() => of(loginUrl))
      );
    })
  );
};