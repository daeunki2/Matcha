import { SchemaPath, validate } from "@angular/forms/signals";

// export function phoneNumber(path: SchemaPath<string>, options?: {message?: string}) {
//   validate(path, ({value}) => {
//     const phoneRegex = /^\d{3}-\d{3}-\d{4}$/;

//     if (!phoneRegex.test(value())) {
//       return {
//         kind: 'phoneNumber',
//         message: options?.message || 'Phone must be in format: 555-123-4567',
//       };
//     }

//     return null;
//   });
// }

export function password(path: SchemaPath<string>) {
	validate(path, ({ value }): { kind: 'password', message: string }[] | null => {	
		const password = value();
		const hasUpperCase = /[A-Z]/.test(password);
		const hasLowerCase = /[a-z]/.test(password);
		const hasNumber = /\d/.test(password);
		const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
		const isValidLength = password.length >= 8;

		const errors: { kind: 'password', message: string }[] = [];

		if (!hasUpperCase) {
			errors.push({ kind: 'password', message: 'Password must contain at least one uppercase letter.' });
		}
		if (!hasLowerCase) {
			errors.push({ kind: 'password', message: 'Password must contain at least one lowercase letter.' });
		}
		if (!hasNumber) {
			errors.push({ kind: 'password', message: 'Password must contain at least one number.' });
		}
		if (!hasSpecialChar) {
			errors.push({ kind: 'password', message: 'Password must contain at least one special character.' });
		}
		if (!isValidLength) {
			errors.push({ kind: 'password', message: 'Password must be at least 8 characters long.' });
		}

		return errors.length ? errors : null; // Password is valid
	});		
};