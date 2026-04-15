import { Component, inject, input, Input, OnInit, signal } from '@angular/core';
import { Container } from '../../shared/container/container';
import { FormsModule } from '@angular/forms';
import { Task } from '../../models/types';
import { Tasks } from '../../services/tasks';

@Component({
  selector: 'app-task-form',
  imports: [Container, FormsModule],
  templateUrl: './task-form.html',
  styleUrl: './task-form.css',
})
export class TaskForm implements OnInit {
  @Input() currentTask!: Task;

  taskService = inject(Tasks);
  addTaskMode = false;

  ngOnInit() {
    this.taskService.addTaskMode.subscribe((isAdd) => {
      this.addTaskMode = isAdd;
    });
  }
  deleteTask() {
    this.taskService.deleteTask(this.currentTask.id).subscribe(() => {
      this.taskService.cancelEditTask();
    });
  }

  saveTask() {
    if (this.addTaskMode) {
      this.taskService.addTask(this.currentTask).subscribe(() => {
        this.taskService.cancelEditTask();
        this.taskService.togggleAddTaskMode(false);
      });
    } else {
      this.taskService.updateTask(this.currentTask).subscribe(() => {
        this.taskService.cancelEditTask();
      });
    }
  }
}
