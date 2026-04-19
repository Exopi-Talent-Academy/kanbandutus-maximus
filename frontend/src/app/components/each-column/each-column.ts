import { Component, inject, Input, OnInit } from '@angular/core';
import { Container } from '../../shared/container/container';
import { BoardType, Task } from '../../models/types';

import { AddNewTask } from '../add-new-task/add-new-task';

import { EachRow } from '../each-row/each-row';

@Component({
  selector: 'app-each-column',
  imports: [Container, AddNewTask, EachRow],
  templateUrl: './each-column.html',
  styleUrl: './each-column.css',
})
export class EachColumn implements OnInit {
  @Input() tasks: Task[] = [];
  @Input() columnName!: string;
  @Input() columnId!: number;
  @Input() boardId!: number;
  @Input() board!: BoardType;
  @Input() position!: number;

  ngOnInit() {}
}
