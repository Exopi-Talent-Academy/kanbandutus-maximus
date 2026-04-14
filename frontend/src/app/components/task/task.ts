import { Component, inject, Input, OnInit } from '@angular/core';
import { Container } from '../../shared/container/container';
import { Tasks } from '../../services/tasks';
import { TaskType } from '../../models/types';
import { Task } from '../../models/types';

@Component({
  selector: 'app-each-task',
  imports: [],
  templateUrl: './task.html',
  styleUrl: './task.css',
})
export class EachTask implements OnInit {
  @Input() task!: Task;

  taskService = inject(Tasks);

  ngOnInit() {
    // console.log('Task in EachTask component:', this.task);
  }

  getAssignee() {
    return `${this.task.assignee?.split(' ')[0][0].toUpperCase()}${this.task.assignee?.split(' ')[1][0].toUpperCase()}`;
  }

  openTaskModal() {
    this.taskService.onEditTask({
      id: '',
      title: this.task.title,
      status: TaskType.TODO,
      assignee: this.task.assignee,
      description: '',
    });
  }
}
