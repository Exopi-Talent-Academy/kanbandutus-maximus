import { Component, inject } from '@angular/core';
import { Container } from '../../shared/container/container';
import { Tasks } from '../../services/tasks';

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
      column_id: 0,
      assignee: '',
      description: '',
    });
    this.taskService.togggleAddTaskMode(true);
  }
}
