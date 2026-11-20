import { Component, computed, inject, signal } from '@angular/core';
import { AuthLayout } from '../auth-layout/auth-layout';
import { AuthService } from '../../../services/auth/auth.service';
import { password } from '../shared/password.validator';
import { email, form, FormField, pattern, required } from '@angular/forms/signals';
import { HttpErrorResponse } from '@angular/common/http';

interface SignupForm {
  firstname: string;
  lastname: string;
  username: string;
  email: string;
  password: string;
}

@Component({
  imports: [AuthLayout, FormField],
  selector: 'app-signup',
  styleUrl: './signup.scss',
  templateUrl: './signup.html',
})
export class Signup {
  private readonly authService = inject(AuthService);

  protected readonly signupSuccess = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly isSubmitting = signal(false);
  protected readonly canResendVerification = signal(false);

  private signupModel = signal<SignupForm>({
    firstname: '',
    lastname: '',
    username: '',
    email: '',
    password: '',
  });

  protected form = form(this.signupModel, (schemaPath) => {
    required(schemaPath.firstname, { message: 'First name is required.' });
    required(schemaPath.lastname, { message: 'Last name is required.' });
    required(schemaPath.username, { message: 'Username is required.' });
    pattern(schemaPath.username, /^[a-zA-Z0-9_]+$/, { message: 'Username can only contain letters, numbers, and underscores.' });
    required(schemaPath.email, { message: 'Email is required.' });
    email(schemaPath.email, { message: 'Email format is invalid.' });
    required(schemaPath.password, { message: 'Password is required.' });
    password(schemaPath.password);
  });

  protected firstnameErrors = computed(() => this.form.firstname().touched() ? this.form.firstname().errors() : []);
  protected lastnameErrors = computed(() => this.form.lastname().touched() ? this.form.lastname().errors() : []);
  protected usernameErrors = computed(() => this.form.username().touched() ? this.form.username().errors() : []);
  protected emailErrors = computed(() => this.form.email().touched() ? this.form.email().errors() : []);
  protected passwordErrors = computed(() => this.form.password().touched() ? this.form.password().errors() : []);

  protected onSubmit(event: Event) {
    event.preventDefault();

    if (this.form().invalid()) {
      return;
    }
    
    const { firstname, lastname, username, email, password } = this.form().value();
    this.errorMessage.set('');
    this.canResendVerification.set(false);
    this.isSubmitting.set(true);

    this.authService.signup(firstname!, lastname!, username!, email!, password!).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.signupSuccess.set(true);
      },
      error: (error: unknown) => {
        this.isSubmitting.set(false);
        if (error instanceof HttpErrorResponse && error.status === 409) {
          this.errorMessage.set('That username is already taken. Please choose another.');
        } else if (error instanceof HttpErrorResponse && error.status === 503) {
          this.errorMessage.set('Your account was created, but the verification email could not be sent. Please try resending it.');
          this.canResendVerification.set(true);
        } else if (error instanceof HttpErrorResponse && error.status === 429) {
          this.errorMessage.set('Too many requests. Please try again later.');
        } else if (error instanceof HttpErrorResponse && error.status === 400) {
          const validationError = error.error?.error;
          this.errorMessage.set(
            typeof validationError === 'string'
              ? validationError
              : 'Please check your details and try again.'
          );
        } else {
          this.errorMessage.set('Unable to create your account. Please check your details and try again.');
        }
      }
    });
  }
}
