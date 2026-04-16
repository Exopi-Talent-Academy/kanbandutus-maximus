import { Injectable } from '@angular/core';
import { BoardType, Task } from '../models/types';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';

// const BASE_URL = 'http://localhost:8000/api';
const BASE_URL = 'http://localhost:4201';

@Injectable({
  providedIn: 'root',
})
export class Tasks {
  constructor(private http: HttpClient) {}

  updateAvailable = new Subject<boolean>();

  moveTask = new Subject<Task | null>();

  editTask = new Subject<Task | null>();
  addTaskMode = new BehaviorSubject<boolean>(false);

  onTaskMove(task: Task): void {
    this.moveTask.next(task);
  }

  onMoveTaskComplete(): void {
    this.moveTask.next(null);
  }

  private tasks: Task[] = [];

  togggleAddTaskMode(isAdd: boolean): void {
    this.addTaskMode.next(isAdd);
  }

  onEditTask(task: Task): void {
    this.editTask.next(task);
  }
  cancelEditTask(): void {
    this.editTask.next(null);
  }

  addTask(task: Task, board_id: number, position: number): Observable<Task> {
    this.updateAvailable.next(true);
    // Fetch the board
    return new Observable<Task>((observer) => {
      this.getBoard(board_id).subscribe(
        (board: BoardType) => {
          // Find the column by position
          const column = board.columns.find((col) => col.position === position);
          if (!column) {
            observer.error('Column not found');
            return;
          }
          // Insert the task at the end of the column's tasks
          const newTask = { ...task, column_id: column.id, position: column.tasks.length };
          column.tasks.push(newTask);
          // Update the board
          this.http
            .patch<BoardType>(`${BASE_URL}/boards/${board_id}`, { columns: board.columns })
            .subscribe({
              next: () => {
                observer.next(newTask);
                observer.complete();
              },
              error: (err) => observer.error(err),
            });
        },
        (err) => observer.error(err),
      );
    });
  }

  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(`${BASE_URL}/tasks`);
  }

  getBoards(): Observable<any> {
    return this.http.get(`${BASE_URL}/boards`);
  }

  getBoard(boardId: number): Observable<any> {
    return this.http.get(`${BASE_URL}/boards/${boardId}`);
  }

  updateTask(updatedTask: Task, boardId: number, position: number): Observable<Task> {
    this.updateAvailable.next(true);
    return this.http.put<Task>(`${BASE_URL}/tasks/${updatedTask.id}`, updatedTask);
  }

  deleteTask(taskId: string): Observable<Task> {
    this.updateAvailable.next(true);
    return this.http.delete<Task>(`${BASE_URL}/tasks/${taskId}`);
  }

  updateTaskPosition(boardId: number, newPosition: number, name: string): Observable<BoardType> {
    this.updateAvailable.next(true);
    return this.http.patch<BoardType>(`${BASE_URL}/boards/${boardId}`, {
      columns: [
        {
          name,
          position: newPosition,
        },
      ],
    });
  }

  showUpdateNotification() {
    this.updateAvailable.next(true);
    setTimeout(() => {
      this.updateAvailable.next(false);
    }, 3000);
  }
}
