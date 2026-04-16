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

  addTask(task: Task): Observable<Task> {
    this.updateAvailable.next(true);
    return this.http.post<Task>(`${BASE_URL}/tasks`, task);
  }

  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(`${BASE_URL}/tasks`);
  }

  getBoards(): Observable<any> {
    return this.http.get(`${BASE_URL}/boards`);
  }

  updateTask(updatedTask: Task): Observable<Task> {
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
