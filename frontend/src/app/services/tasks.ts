import { Injectable } from '@angular/core';
import { Task } from '../models/types';
import { Observable, Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';

// const BASE_URL = 'http://localhost:8000/api';
const BASE_URL = 'http://localhost:4201';

@Injectable({
  providedIn: 'root',
})
export class Tasks {
  constructor(private http: HttpClient) {}

  private tasks: Task[] = [];

  editTask = new Subject<Task | null>();

  onEditTask(task: Task): void {
    this.editTask.next(task);
  }
  cancelEditTask(): void {
    this.editTask.next(null);
  }

  addTask(task: Task): Observable<Task> {
    return this.http.post<Task>(`${BASE_URL}/tasks`, task);
  }

  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(`${BASE_URL}/tasks`);
  }

  updateTask(updatedTask: Task): Observable<Task> {
    return this.http.put<Task>(`${BASE_URL}/tasks/${updatedTask.id}`, updatedTask);
  }

  deleteTask(taskId: string): Observable<Task> {
    return this.http.delete<Task>(`${BASE_URL}/tasks/${taskId}`);
  }
}
