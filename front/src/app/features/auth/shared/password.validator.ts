import { FormControl, ValidationErrors } from "@angular/forms";

export function passwordValidator(control: FormControl): ValidationErrors | null {
		const password = control.value;
		const hasUpperCase = /[A-Z]/.test(password);
		const hasLowerCase = /[a-z]/.test(password);
		const hasNumber = /\d/.test(password);
		const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
		const isValidLength = password.length >= 8;

		const errors: ValidationErrors = {};

		if (!hasUpperCase) {
			errors['uppercase'] = 'Password must contain at least one uppercase letter.';
		}
		if (!hasLowerCase) {
			errors['lowercase'] = 'Password must contain at least one lowercase letter.';
		}
		if (!hasNumber) {
			errors['number'] = 'Password must contain at least one number.';
		}
		if (!hasSpecialChar) {
			errors['specialChar'] = 'Password must contain at least one special character.';
		}
		if (!isValidLength) {
			errors['length'] = 'Password must be at least 8 characters long.';
		}

		return Object.keys(errors).length ? errors : null; // Password is valid
		
};