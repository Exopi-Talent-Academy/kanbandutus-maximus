import { Component, inject, Input, OnInit } from '@angular/core';
import { Container } from '../../shared/container/container';
import { Task } from '../../models/types';
import { EachTask } from '../task/task';
import { AddNewTask } from '../add-new-task/add-new-task';
import { Tasks } from '../../services/tasks';
import { columnNames } from '../../models/types';

@Component({
  selector: 'app-each-column',
  imports: [Container, EachTask, AddNewTask],
  templateUrl: './each-column.html',
  styleUrl: './each-column.css',
})
export class EachColumn implements OnInit {
  @Input() tasks: Task[] = [];
  @Input() columnName!: string;

  taskService = inject(Tasks);

  ngOnInit() {
    console.log('Column Name:', this.columnName);
    for (const task of this.tasks) {
      console.log(
        'Task in EachColumn component:',
        task.position,
        'with column name:',
        this.columnName,
      );
    }
  }

  onDragDrop(event: DragEvent) {
    event.preventDefault();

    console.log('Drag dropped on column:', this.columnName);
    this.taskService.moveTask.subscribe((movedTask) => {
      if (movedTask) {
        this.taskService
          .updateTask({
            ...movedTask,
            position: this.columnName as unknown as number,
          })
          .subscribe(() => {
            this.taskService.onMoveTaskComplete();
            console.log('Task moved successfully:', movedTask);
          });
      }
    });

    this.taskService.onMoveTaskComplete();
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }
}
