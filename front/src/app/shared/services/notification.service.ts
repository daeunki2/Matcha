import { Injectable, signal } from "@angular/core";

export interface AppNotification {
  id: number;
  kind: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private nextId = 0;
  private readonly _notifications = signal<AppNotification[]>([]);
  public readonly notifications = this._notifications.asReadonly();

  public showSuccess(message: string): void {
    this.add('success', message);
  }

  public showError(message: string): void {
    this.add('error', message);
  }

  public showInfo(message: string): void {
    this.add('info', message);
  }

  public showWarning(message: string): void {
    this.add('warning', message);
  }

  public dismiss(id: number): void {
    this._notifications.update(notifications => notifications.filter(notification => notification.id !== id));
  }

  private add(kind: AppNotification['kind'], message: string): void {
    this._notifications.update(notifications => [
      ...notifications,
      { id: this.nextId++, kind, message }
    ]);
  }
}