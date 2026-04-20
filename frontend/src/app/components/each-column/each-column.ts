import { Component, inject, Input, OnChanges, OnInit, signal, SimpleChanges } from '@angular/core';
import { Container } from '../../shared/container/container';
import { BoardType, Task } from '../../models/types';

import { AddNewTask } from '../add-new-task/add-new-task';

import { EachRow } from '../each-row/each-row';
import { Tasks } from '../../services/tasks';

@Component({
  selector: 'app-each-column',
  imports: [Container, AddNewTask, EachRow],
  templateUrl: './each-column.html',
  styleUrl: './each-column.css',
})
export class EachColumn implements OnInit, OnChanges {
  @Input() tasks: Task[] = [];
  @Input() columnName!: string;
  @Input() columnId!: number;
  @Input() boardId!: number;
  @Input() board!: BoardType;
  @Input() position!: number;

  updatedTasks = signal<Task[]>([]);

  taskService = inject(Tasks);

  ngOnInit() {
    this.updateBoard();
    this.taskService.updateAvailable.subscribe((res) => {
      this.updateBoard();
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['tasks'] || changes['columnId']) {
      this.updateBoard();
    }
  }

  updateBoard() {
    const task: Task = {
      id: 0,
      title: '',
      position: 1111,
      description: '',
      assignee: '',
      column_id: this.columnId,
    };
    this.updatedTasks.set([...this.tasks, task]);
  }
}
