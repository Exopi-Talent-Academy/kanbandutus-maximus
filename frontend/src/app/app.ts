import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Container } from './shared/container/container';
import { Header } from './components/header/header';
import { NavBar } from './components/nav-bar/nav-bar';
import { Board } from './components/board/board';
import { Tasks } from './services/tasks';
import { Task } from './models/types';
import { TaskForm } from './components/task-form/task-form';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faClose } from '@fortawesome/free-solid-svg-icons';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  imports: [Container, Header, NavBar, Board, TaskForm, FontAwesomeModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  protected readonly title = signal('kanban');

  faClose = faClose;

  login = signal(false);
  username: string = '';
  password: string = '';

  task = signal<Task>({
    id: 0,
    title: '',
    column_id: 0,
    assignee: '',
    position: 0,
  });

  isEditable = signal(false);

  taskService = inject(Tasks);

  ngOnInit() {
    this.taskService.currentUser.subscribe((user) => {
      if (user.username) {
        this.login.set(true);
      } else {
        this.login.set(false);
      }
    });
    this.taskService.editTask.subscribe((task) => {
      console.log('Received task for editing:', task);
      if (task) {
        this.isEditable.set(true);
        this.task.set(task);
      } else {
        this.isEditable.set(false);
        this.task.set({
          id: 0,
          title: '',
          column_id: 0,
          assignee: '',
          position: 0,
        });
      }
    });
  }

  cancelEdit() {
    this.taskService.cancelEditTask();
    this.taskService.togggleAddTaskMode(false);
  }

  isAddTask() {
    return this.task().id === 0;
  }

  submitForm() {
    this.taskService.getUsers().subscribe((res) => {
      res.forEach((user) => {
        console.log(user.username, user.password_hash);
        if (user.username === this.username && this.password === user.password_hash) {
          const userId = user.id.toString();
          // Optional: persist to storage
          localStorage.setItem('userId', userId);
          console.log(localStorage.getItem('userId'));
          this.taskService.setUser(user);
          this.username = '';
          this.password = '';

          this.login.set(true);
        }
        console.log(this.login());
      });
    });
  }
}
