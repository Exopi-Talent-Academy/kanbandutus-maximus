import { Component, inject, input, Input, OnInit, signal } from '@angular/core';
import { Container } from '../../shared/container/container';
import { FormsModule } from '@angular/forms';
import { BoardType, ColumnType, Task } from '../../models/types';
import { Tasks } from '../../services/tasks';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faClose } from '@fortawesome/free-solid-svg-icons';
import { faEdit } from '@fortawesome/free-solid-svg-icons';
import { faAdd } from '@fortawesome/free-solid-svg-icons';
import { faTrash } from '@fortawesome/free-solid-svg-icons';
import { Board } from '../board/board';

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
    this.taskService.addTaskMode.subscribe((isAdd) => {
      this.addTaskMode = isAdd;
    });
    console.log('position', this.currentTask.column_id);
  }
  deleteTask() {
    this.taskService.deleteTask(this.currentTask.id).subscribe((res: Task) => {
      console.log('successfully deleted a task....', res);
      this.taskService.cancelEditTask();
    });
  }

  saveTask() {
    this.taskService.updateTask(this.currentTask, this.currentTask.id).subscribe((res: Task) => {
      console.log('successfully dragged and dropped....', res);
    });

    this.taskService.cancelEditTask();
  }
  addTask() {
    this.taskService.createTask(this.currentTask).subscribe((res: Task) => {
      console.log('successfully dragged and dropped....', res);
    });

    this.taskService.cancelEditTask();
    this.taskService.togggleAddTaskMode(false);
  }
}
