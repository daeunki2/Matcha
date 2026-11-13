import { Component, computed, inject, signal } from '@angular/core';
import { AuthLayout } from '../auth-layout/auth-layout';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth/auth.service';
import { password } from '../shared/password.validator';
import { email, form, FormField, pattern, required } from '@angular/forms/signals';
import { NotificationService } from '../../../shared/services/notification.service';

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
  private readonly notificationService = inject(NotificationService);

  protected readonly signupSuccess = signal(false);
  protected readonly canResendEmail = signal(false);

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
      console.log('Form is invalid: ', this.form().errors());
      return;
    }
    
    const { firstname, lastname, username, email, password } = this.form().value();

    this.authService.signup(firstname!, lastname!, username!, email!, password!).subscribe({
      next: () => {
        this.notificationService.showSuccess('Signup successful! Please check your email to verify your account.');
        this.signupSuccess.set(true);
      },
      error: (error) => {
        if (error.status === 409) {
          this.notificationService.showError('Email or username already exists');
        }
      }
    });
  }
}
