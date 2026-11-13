import { Routes } from "@angular/router";

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
  // {
  //   path: "dashboard",
  //   loadComponent: () =>
  //     import("./features/dashboard/dashboard").then((m) => m.Dashboard),
  // },
];
