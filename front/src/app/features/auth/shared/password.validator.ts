import { SchemaPath, validate } from "@angular/forms/signals";

export function password(path: SchemaPath<string>) {
  validate(path, ({ value }): { kind: 'password'; message: string }[] | null => {
    const currentPassword = value();
    const errors: { kind: 'password'; message: string }[] = [];

    if (!/[A-Z]/.test(currentPassword)) {
      errors.push({ kind: 'password', message: 'Password must contain at least one uppercase letter.' });
    }
    if (!/[a-z]/.test(currentPassword)) {
      errors.push({ kind: 'password', message: 'Password must contain at least one lowercase letter.' });
    }
    if (!/\d/.test(currentPassword)) {
      errors.push({ kind: 'password', message: 'Password must contain at least one number.' });
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(currentPassword)) {
      errors.push({ kind: 'password', message: 'Password must contain at least one special character.' });
    }
    if (currentPassword.length < 8) {
      errors.push({ kind: 'password', message: 'Password must be at least 8 characters long.' });
    }

    return errors.length ? errors : null;
  });
}