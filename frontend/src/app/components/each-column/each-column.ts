import { Component, Input, OnInit } from '@angular/core';
import { Container } from '../../shared/container/container';
import { Task } from '../../models/types';
import { EachTask } from '../task/task';
import { AddNewTask } from '../add-new-task/add-new-task';

@Component({
  selector: 'app-each-column',
  imports: [Container, EachTask, AddNewTask],
  templateUrl: './each-column.html',
  styleUrl: './each-column.css',
})
export class EachColumn implements OnInit {
  @Input() tasks: Task[] = [];
  @Input() columnName!: string;

  ngOnInit() {
    console.log('Column Name:', this.columnName);
    for (const task of this.tasks) {
      console.log(
        'Task in EachColumn component:',
        task.status,
        'with column name:',
        this.columnName,
      );
    }
  }
}
