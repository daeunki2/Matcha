import { Component, inject } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { NotificationService } from "./shared/services/notification.service";

@Component({
  imports: [RouterOutlet],
  selector: "app-root",
  styleUrl: "./app.scss",
  templateUrl: "./app.html",
})
export class App {
  protected readonly notificationService = inject(NotificationService);

  protected dismissNotification(id: number): void {
    this.notificationService.dismiss(id);
  }
}
