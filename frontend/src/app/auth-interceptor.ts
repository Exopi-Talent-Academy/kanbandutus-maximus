import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const userId = localStorage.getItem('userId');

    if (userId) {
      const authRequest = request.clone({
        setHeaders: {
          'X-Demo-Account-Id': userId,
        },
      });
      return next.handle(authRequest);
    }

    return next.handle(request);
  }
}
