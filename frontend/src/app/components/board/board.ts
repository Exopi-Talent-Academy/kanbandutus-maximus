import { Component, inject, OnInit, signal } from '@angular/core';
import { EachColumn } from '../each-column/each-column';
import { Container } from '../../shared/container/container';
import { CommonModule } from '@angular/common';
import { Task } from '../../models/types';
import { Tasks } from '../../services/tasks';

@Component({
  selector: 'app-board',
  imports: [EachColumn, Container, CommonModule],
  templateUrl: './board.html',
  styleUrl: './board.css',
})
export class Board implements OnInit {
  board = ['To Do', 'Plan', 'In Progress', 'Done'];
  tasks = signal<Task[]>([]);
  taskService = inject(Tasks);

  ngOnInit() {
    this.taskService.getTasks().subscribe((tasks) => {
      console.log('Fetched tasks:', tasks);
      this.tasks.set(tasks);
    });
  }
}
