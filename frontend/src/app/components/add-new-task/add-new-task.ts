import { Component, inject } from '@angular/core';
import { Container } from '../../shared/container/container';
import { Tasks } from '../../services/tasks';
import { TaskType } from '../../models/types';

@Component({
  selector: 'app-add-new-task',
  imports: [Container],
  templateUrl: './add-new-task.html',
  styleUrl: './add-new-task.css',
})
export class AddNewTask {
  taskService = inject(Tasks);

  addNewTask() {
    this.taskService.onEditTask({
      id: '',
      title: '',
      status: TaskType.TODO,
      assignee: '',
      description: '',
    });
    this.taskService.togggleAddTaskMode(true);
  }
}
