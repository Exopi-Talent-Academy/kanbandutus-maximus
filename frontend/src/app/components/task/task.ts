import { Component, inject, Input, OnInit } from '@angular/core';
import { Tasks } from '../../services/tasks';
import { Task } from '../../models/types';
import { NgClass } from '@angular/common';

@Component({
  selector: 'app-each-task',
  imports: [NgClass],
  templateUrl: './task.html',
  styleUrl: './task.css',
})
export class EachTask implements OnInit {
  @Input() task!: Task;
  @Input() boardId!: number;
  @Input() columnId!: number;

  taskService = inject(Tasks);

  ngOnInit() {
    // console.log('Task in EachTask component:', this.task);
    // this.userId = localStorage.getItem('userId');
  }

  getAssignee() {
    return 'S';
    //return this.task.assignee?.split('')[0].toUpperCase();
    // return `${this.task.assignee?.split(' ')[0][0].toUpperCase()}${this.task.assignee?.split(' ')[1][0].toUpperCase()}`;
  }

  openTaskModal() {
    if (this.getUserId() === '4') {
      return;
    } else {
      this.taskService.onEditTask({
        id: this.task.id,
        title: this.task.title,
        column_id: this.task.column_id,
        assignee: this.task.assignee,
        description: this.task.description,
        position: this.task.position,
      });
      this.taskService.onTaskMove(this.task, this.columnId);
    }
  }
  onDragStart() {
    this.taskService.onTaskMove(this.task, this.columnId);
  }
  getUserId() {
    return localStorage.getItem('userId');
  }
}
