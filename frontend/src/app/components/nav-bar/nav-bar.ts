import { Component, inject, OnInit, signal } from '@angular/core';
import { Container } from '../../shared/container/container';
import { Tasks } from '../../services/tasks';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faSignOut } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-nav-bar',
  imports: [Container, FontAwesomeModule],
  templateUrl: './nav-bar.html',
  styleUrl: './nav-bar.css',
})
export class NavBar implements OnInit {
  faSignOut = faSignOut;
  taskService = inject(Tasks);
  userName = signal('');
  ngOnInit(): void {
    this.taskService.currentUser.subscribe((user) => this.userName.set(user.username));
  }

  logoutUser() {
    this.taskService.setUser({
      id: '',
      username: '',
      password_hash: '',
    });
    localStorage.removeItem('userId');
  }
}
