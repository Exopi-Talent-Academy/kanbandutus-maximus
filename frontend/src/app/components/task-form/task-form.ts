import { Component, inject, input, Input, OnInit, signal } from '@angular/core';
import { Container } from '../../shared/container/container';
import { FormsModule } from '@angular/forms';
import { Task } from '../../models/types';
import { Tasks } from '../../services/tasks';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faClose } from '@fortawesome/free-solid-svg-icons';
import { faEdit } from '@fortawesome/free-solid-svg-icons';
import { faAdd } from '@fortawesome/free-solid-svg-icons';
import { faTrash } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-task-form',
  imports: [Container, FormsModule, FontAwesomeModule],
  templateUrl: './task-form.html',
  styleUrl: './task-form.css',
})
export class TaskForm implements OnInit {
  faClose = faClose;
  faEdit = faEdit;
  faAdd = faAdd;
  faTrash = faTrash;
  @Input() currentTask!: Task;
  @Input() boardId!: number;
  @Input() position!: number;

  taskService = inject(Tasks);
  addTaskMode = false;

  ngOnInit() {
    console.log('dsjflkjdsflk', this.boardId, this.position);
    this.taskService.addTaskMode.subscribe((isAdd) => {
      this.addTaskMode = isAdd;
    });
  }
  deleteTask() {}

  saveTask() {
    if (this.addTaskMode) {
      this.taskService.addTask(this.currentTask, this.boardId, this.position).subscribe(() => {
        this.taskService.cancelEditTask();
        this.taskService.togggleAddTaskMode(false);
      });
    } else {
      this.taskService.updateTask(this.currentTask, this.boardId, this.position).subscribe(() => {
        this.taskService.cancelEditTask();
      });
    }
  }
}
