import { Injectable } from '@angular/core';
import { Task } from '../models/types';
import { Observable, Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';

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
    return this.http.post<Task>('http://localhost:4201/tasks', task);
  }

  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>('http://localhost:4201/tasks');
  }

  updateTask(updatedTask: Task): Observable<Task> {
    return this.http.put<Task>(`http://localhost:4201/tasks/${updatedTask.id}`, updatedTask);
  }

  deleteTask(taskId: string): Observable<Task> {
    return this.http.delete<Task>(`http://localhost:4201/tasks/${taskId}`);
  }
}
