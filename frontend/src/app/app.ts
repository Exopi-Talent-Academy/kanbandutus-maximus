import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Container } from './shared/container/container';
import { Header } from './components/header/header';
import { NavBar } from './components/nav-bar/nav-bar';
import { Board } from './components/board/board';
import { Tasks } from './services/tasks';

@Component({
  selector: 'app-root',
  imports: [Container, Header, NavBar, Board],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  protected readonly title = signal('kanban');

  isEditable = signal(false);

  taskService = inject(Tasks);

  ngOnInit() {
    this.taskService.editTask.subscribe((task) => {
      if (task) {
        this.isEditable.set(true);
      } else {
        this.isEditable.set(false);
      }
    });
  }

  cancelEdit() {
    this.taskService.cancelEditTask();
  }
}
