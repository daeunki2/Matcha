import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { AuthService } from '../../../services/auth/auth.service';
import { EmailCheck } from './email-check';

describe('EmailCheck', () => {
  let component: EmailCheck;
  let fixture: ComponentFixture<EmailCheck>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EmailCheck],
      providers: [
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { queryParamMap: { get: () => 'verification-token' } } },
        },
        { provide: AuthService, useValue: { verifyEmail: () => of({}) } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(EmailCheck);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
