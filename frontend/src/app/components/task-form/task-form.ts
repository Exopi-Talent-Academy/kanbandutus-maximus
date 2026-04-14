import { Component, inject, input, Input, OnInit, signal } from '@angular/core';
import { Container } from '../../shared/container/container';
import { FormsModule } from '@angular/forms';
import { Task, TaskType } from '../../models/types';
import { Tasks } from '../../services/tasks';

@Component({
  selector: 'app-task-form',
  imports: [Container, FormsModule],
  templateUrl: './task-form.html',
  styleUrl: './task-form.css',
})
export class TaskForm implements OnInit {
  @Input() currentTask!: Task;
  @Input() addTask: boolean = false;

  taskService = inject(Tasks);

  ngOnInit() {
    console.log('Task received in TaskForm component:', this.currentTask);
  }
  deleteTask() {
    this.taskService.deleteTask(this.currentTask.id).subscribe(() => {
      this.taskService.cancelEditTask();
    });
  }

  saveTask() {
    if (this.addTask) {
      this.taskService.addTask(this.currentTask).subscribe(() => {
        this.taskService.cancelEditTask();
      });
    } else {
      this.taskService.updateTask(this.currentTask).subscribe(() => {
        this.taskService.cancelEditTask();
      });
    }
  }
}
