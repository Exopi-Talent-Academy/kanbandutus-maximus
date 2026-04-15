import { Component, inject } from '@angular/core';
import { Container } from '../../shared/container/container';
import { Tasks } from '../../services/tasks';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faAdd } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-add-new-task',
  imports: [Container, FontAwesomeModule],
  templateUrl: './add-new-task.html',
  styleUrl: './add-new-task.css',
})
export class AddNewTask {
  faAdd = faAdd;
  taskService = inject(Tasks);

  addNewTask() {
    this.taskService.onEditTask({
      id: '',
      title: '',
      column_id: 0,
      assignee: '',
      description: '',
      position: 0,
    });
    this.taskService.togggleAddTaskMode(true);
  }
}
