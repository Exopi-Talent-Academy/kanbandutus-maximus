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
  }
  deleteTask() {
    let board = this.taskService.currentBoard;
    const columnId = this.taskService.fromColumnId;

    // let column = board?.columns.find((column) => column.id === columnId);
    // const tasks = column?.tasks.filter((task) => task.id !== this.currentTask.id) ?? [];

    // if (column) {
    //   column = { ...column, tasks: tasks };
    // }

    board?.columns.map((col) => {
      if (col.id === columnId) {
        let tasks = col.tasks.filter((task) => task.id !== this.currentTask.id);
        col.tasks = tasks;
        return col;
      } else {
        return col;
      }
    });

    this.taskService.updateBoard('2', board as BoardType).subscribe(() => {
      console.log('Board deleted successfully after saving task');
    });
    this.taskService.cancelEditTask();
  }

  saveTask() {
    const board = this.taskService.currentBoard;
    const columnId = this.taskService.fromColumnId;
    console.log('Saving task:', this.currentTask, 'to board:', board, 'in column:', columnId);

    const myTask = board?.columns
      .filter((col) => col.id === columnId)[0]
      .tasks.filter((t) => t.id === this.currentTask.id)[0];
    if (myTask) {
      myTask.title = this.currentTask.title;
      myTask.description = this.currentTask.description;
      myTask.assignee = this.currentTask.assignee;
    }
    this.taskService.updateBoard('2', board as BoardType).subscribe(() => {
      console.log('Board updated successfully after saving task');
    });
    this.taskService.cancelEditTask();
  }
}
