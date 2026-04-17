import { Injectable } from '@angular/core';
import { BoardType, Task } from '../models/types';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';

const BASE_URL = 'http://localhost:8000/api';
//const BASE_URL = 'http://localhost:4201';

@Injectable({
  providedIn: 'root',
})
export class Tasks {
  constructor(private http: HttpClient) {}

  updateAvailable = new Subject<boolean>();

  moveTask: Task | null = null;
  fromColumnId = 0;

  editTask = new Subject<Task | null>();
  addTaskMode = new BehaviorSubject<boolean>(false);

  currentBoard: BoardType | null = null;

  setCurrentBoard(board: BoardType | null): void {
    this.currentBoard = board;
  }

  onTaskMove(task: Task, beginColumnId: number): void {
    this.moveTask = task;
    this.fromColumnId = beginColumnId;
  }

  onMoveTaskComplete(): void {
    this.moveTask = null;
    this.fromColumnId = 0;
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

  getBoards(): Observable<any> {
    return this.http.get(`${BASE_URL}/boards`);
  }

  getBoard(name: string): Observable<any> {
    return this.http.get(`${BASE_URL}/boards/${name}`);
  }

  deleteBoard(boardId: number): Observable<any> {
    return this.http.delete(`${BASE_URL}/boards/${boardId}`);
  }

  addBoard(board: BoardType): Observable<any> {
    return this.http.post(`${BASE_URL}/boards`, board);
  }

  updateBoard(boardId: string, board: BoardType): Observable<any> {
    return this.http.put(`${BASE_URL}/boards/${boardId}`, board);
  }

  updateTask(task: Task, task_id: number): Observable<Task> {
    this.updateAvailable.next(true);
    return this.http.put<Task>(`${BASE_URL}/tasks/${task_id}`, task);
  }

  createTask(task: Task) {
    this.updateAvailable.next(true);
    return this.http.post<Task>(`${BASE_URL}/tasks`, task);
  }

  showUpdateNotification() {
    this.updateAvailable.next(true);
    setTimeout(() => {
      this.updateAvailable.next(false);
    }, 3000);
  }
}
