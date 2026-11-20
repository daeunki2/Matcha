import { Routes } from "@angular/router";
import { authGuard } from "./services/auth/auth.guard";

export const routes: Routes = [
  {
    path: "",
    redirectTo: "login",
    pathMatch: "full",
  },
  {
    path: "login",
    loadComponent: () =>
      import("./features/auth/login/login").then((m) => m.Login),
  },
  {
    path: "signup",
    loadComponent: () =>
      import("./features/auth/signup/signup").then((m) => m.Signup),
  },
  {
    path: 'verify-email',
    loadComponent: () =>
      import('./features/auth/email-check/email-check').then(m => m.EmailCheck)
  },
  {
    path: "forgot-password",
    loadComponent: () =>
      import("./features/auth/forgot-password/forgot-password").then((m) => m.ForgotPassword),
  },
  {
    path: 'reset-password',
    loadComponent: () =>
      import('./features/auth/new-password/new-password').then(m => m.NewPassword)
  },
  {
    path: "legal",
    loadComponent: () =>
      import("./features/shared/legal-information/legal-information").then((m) => m.LegalInformation),
  },
  {
    path: "",
    canActivate: [authGuard],
    loadComponent: () =>
      import("./features/shared/main-layout/main-layout").then((m) => m.MainLayout),
    children: [
      {
        path: "dashboard",
        loadComponent: () =>
          import("./features/dashboard/dashboard").then((m) => m.Dashboard),
      },
      {
        path: "complete_profile",
        loadComponent: () =>
          import("./features/profile/complete-profile/complete-profile").then((m) => m.CompleteProfile),
      },
    ],
  },
  {
    path: "**",
    redirectTo: "login",
  },
];
