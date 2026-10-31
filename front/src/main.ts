import { Component, signal } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';

@Component({
  selector: 'app-root',
  standalone: true,
  template: `
    <header><strong>Matcha</strong></header>
    <main>
      <h1>Welcome to Matcha</h1>
      <p>Your next connection starts here.</p>
      <p role="status">{{ status() }}</p>
    </main>
    <footer>Matcha · 42 project</footer>
  `,
})
class App {
  readonly status = signal('Connecting…');

  constructor() {
    void this.checkConnection();
  }

  private async checkConnection(): Promise<void> {
    try {
      const response = await fetch('/api/health');
      const result = await response.json();
      if (!response.ok || result.status !== 'ok' || result.database !== 'ok') {
        throw new Error('Service unavailable');
      }
      this.status.set('Ready to get started.');
    } catch {
      this.status.set('Unable to connect. Please try again later.');
    }
  }
}

bootstrapApplication(App).catch(console.error);
