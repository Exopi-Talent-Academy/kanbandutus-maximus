import { Component, inject, Input, OnInit } from '@angular/core';
import { Tasks } from '../../services/tasks';
import { Task } from '../../models/types';

@Component({
  selector: 'app-each-task',
  imports: [],
  templateUrl: './task.html',
  styleUrl: './task.css',
})
export class EachTask implements OnInit {
  @Input() task!: Task;
  @Input() boardId!: number;
  @Input() fromColumnId!: number;

  taskService = inject(Tasks);

  ngOnInit() {
    // console.log('Task in EachTask component:', this.task);
  }

  getAssignee() {
    return `${this.task.assignee?.split(' ')[0][0].toUpperCase()}${this.task.assignee?.split(' ')[1][0].toUpperCase()}`;
  }

  openTaskModal() {
    this.taskService.onEditTask({
      id: this.task.id,
      title: this.task.title,
      column_id: this.task.column_id,
      assignee: this.task.assignee,
      description: this.task.description,
      position: this.task.position,
    });
    this.taskService.onTaskMove(this.task, this.fromColumnId);
  }
  onDragStart() {
    this.taskService.onTaskMove(this.task, this.fromColumnId);
  }
}
