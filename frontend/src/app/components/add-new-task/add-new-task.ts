import { Component } from '@angular/core';
import { Container } from '../../shared/container/container';

@Component({
  selector: 'app-add-new-task',
  imports: [Container],
  templateUrl: './add-new-task.html',
  styleUrl: './add-new-task.css',
})
export class AddNewTask {
  addNewTask() {
    console.log('Add New Task clicked');
  }
}
