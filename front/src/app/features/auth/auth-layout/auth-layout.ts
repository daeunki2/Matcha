import { Component, input, InputSignal } from '@angular/core';

@Component({
  imports: [],
  selector: 'app-auth-layout',
  styleUrl: './auth-layout.scss',
  templateUrl: './auth-layout.html',
})
export class AuthLayout {
  public readonly title: InputSignal<string> = input.required<string>();
  public readonly subtitle: InputSignal<string | undefined> = input<string | undefined>();
}
