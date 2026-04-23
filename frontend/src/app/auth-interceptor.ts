import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Get userId from localStorage, sessionStorage, or your auth service
    // Option 1: From localStorage
    const userId = localStorage.getItem('userId');

    // Option 3: From an Auth Service (better)
    // const userId = this.authService.getUserId();

    if (userId) {
      // Clone the request and add the userId header
      const authRequest = request.clone({
        setHeaders: {
          userId: userId,
        },
      });
      return next.handle(authRequest);
    }

    // If no userId, proceed with original request
    return next.handle(request);
  }
}
