import { Injectable } from "@angular/core";

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  public showSuccess(message: string): void {
	console.log('Success:', message);
  }

  public showError(message: string): void {
	console.error('Error:', message);
  }

  public showInfo(message: string): void {
	console.info('Info:', message);
  }

  public showWarning(message: string): void {
	console.warn('Warning:', message);
  }
}