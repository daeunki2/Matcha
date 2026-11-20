import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { AuthService } from '../../../services/auth/auth.service';
import { NewPassword } from './new-password';

describe('NewPassword', () => {
  let component: NewPassword;
  let fixture: ComponentFixture<NewPassword>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewPassword],
      providers: [
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { queryParamMap: { get: () => 'reset-token' } } },
        },
        { provide: AuthService, useValue: { resetPassword: () => of({}) } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(NewPassword);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
