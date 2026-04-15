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

@Component({
  selector: 'app-root',
  imports: [Container, Header, NavBar, Board, TaskForm, FontAwesomeModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  protected readonly title = signal('kanban');

  faClose = faClose;

  task = signal<Task>({
    id: '',
    title: '',
    column_id: 0,
    assignee: '',
  });

  isEditable = signal(false);

  taskService = inject(Tasks);

  ngOnInit() {
    this.taskService.editTask.subscribe((task) => {
      console.log('Received task for editing:', task);
      if (task) {
        this.isEditable.set(true);
        this.task.set(task);
      } else {
        this.isEditable.set(false);
        this.task.set({
          id: '',
          title: '',
          column_id: 0,
          assignee: '',
        });
      }
    });
  }

  cancelEdit() {
    this.taskService.cancelEditTask();
  }

  isAddTask() {
    return this.task().id === '';
  }
}
