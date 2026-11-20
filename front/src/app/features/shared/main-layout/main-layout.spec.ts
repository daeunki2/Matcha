import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { AuthService } from '../../../services/auth/auth.service';
import { NotificationService } from '../../../shared/services/notification.service';
import { MainLayout } from './main-layout';

describe('MainLayout', () => {
  let component: MainLayout;
  let fixture: ComponentFixture<MainLayout>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MainLayout],
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: {
            user: () => ({ username: 'matcha-user' }),
            logout: () => of(undefined),
          },
        },
        { provide: NotificationService, useValue: { showError: () => {} } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MainLayout);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('renders the app navigation, account action, and legal footer', () => {
    const element: HTMLElement = fixture.nativeElement;

    expect(element.querySelector('a[href="/dashboard"]')?.textContent?.trim()).toBe('Matcha');
    expect(element.querySelector('a[href="/complete_profile"]')?.textContent?.trim()).toBe('matcha-user');
    expect(element.querySelector('button')?.textContent?.trim()).toBe('Log out');
    expect(element.querySelector('footer')?.textContent).toContain('Legal information');
  });
});
