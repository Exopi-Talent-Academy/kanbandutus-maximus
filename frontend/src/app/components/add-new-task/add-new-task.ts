import { Component, inject, Input } from '@angular/core';
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
  @Input() columnId!: number;
  faAdd = faAdd;
  taskService = inject(Tasks);

  addNewTask() {
    this.taskService.onEditTask({
      id: 0,
      title: '',
      column_id: this.columnId,
      assignee: '',
      description: '',
      position: 1110,
    });
    this.taskService.togggleAddTaskMode(true);
  }
}
