import { Component, Input, OnInit, inject } from '@angular/core';
import { Container } from '../../shared/container/container';
import { Task } from '../../models/types';
import { EachTask } from '../task/task';
import { AddNewTask } from '../add-new-task/add-new-task';
import { columnNames } from '../../models/types';
import { updateBoard } from '../../utils/helperFunction';
import { Tasks } from '../../services/tasks';

@Component({
  selector: 'app-each-row',
  imports: [Container, EachTask],
  templateUrl: './each-row.html',
  styleUrl: './each-row.css',
})
export class EachRow {
  @Input() task!: Task;
  @Input() boardId!: number;
  @Input() columnId!: number;

  taskService = inject(Tasks);

  onDragDrop(event: DragEvent) {
    event.preventDefault();

    const taskToMove = this.taskService.moveTask;

    this.taskService
      .updateTask(
        { ...taskToMove!, column_id: this.columnId, position: this.task?.position },
        taskToMove?.id!,
      )
      .subscribe((res: Task) => {
        this.taskService.onMoveTaskComplete();
        // this.taskService.showUpdateNotification();
      });
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    console.log(event);
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    console.log();
  }
}
