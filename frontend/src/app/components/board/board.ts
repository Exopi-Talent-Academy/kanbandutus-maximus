import { Component, inject, OnInit, signal } from '@angular/core';
import { EachColumn } from '../each-column/each-column';
import { Container } from '../../shared/container/container';
import { CommonModule } from '@angular/common';
import { Task, BoardType } from '../../models/types';
import { Tasks } from '../../services/tasks';
import { map } from 'rxjs';

@Component({
  selector: 'app-board',
  imports: [EachColumn, Container, CommonModule],
  templateUrl: './board.html',
  styleUrl: './board.css',
})
export class Board implements OnInit {
  board = [0, 1, 2, 3];
  tasks = signal<Task[]>([]);
  taskService = inject(Tasks);
  boards = signal<BoardType[]>([]);
  currentBoard = signal<BoardType | null>(null);

  ngOnInit() {
    this.loadBoards();
    // this.loadTasks();
    this.taskService.updateAvailable.subscribe(() => {
      this.tasks.set([]); // Clear current tasks before reloading
      console.log('Update available, reloading tasks...');
      setTimeout(() => {
        this.loadBoards();
        // this.loadTasks();
      }, 100); // Add a slight delay to ensure the backend has processed the update
    });
  }

  loadBoards() {
    this.taskService.getBoards().subscribe((boards) => {
      this.boards.set([...boards]);
      this.currentBoard.set(boards[1] || null); // Set the current board to the first one, or null if no boards are available
      console.log('Board loaded:', boards[1]);
      this.taskService.setCurrentBoard(boards[1] || null); // Update the current board in the service as well
    });
  }

  loadTasks() {
    this.taskService.getBoard('Musique').subscribe((board) => {
      this.currentBoard.set(board);
      console.log('Tasks loaded for board:', board);
    });
  }
}
