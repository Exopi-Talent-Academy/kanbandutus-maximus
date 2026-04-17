import { Component, inject, Input, OnInit } from '@angular/core';
import { Container } from '../../shared/container/container';
import { BoardType, Task } from '../../models/types';
import { EachTask } from '../task/task';
import { AddNewTask } from '../add-new-task/add-new-task';
import { Tasks } from '../../services/tasks';
import { columnNames } from '../../models/types';
import { updateBoard } from '../../utils/helperFunction';

@Component({
  selector: 'app-each-column',
  imports: [Container, EachTask, AddNewTask],
  templateUrl: './each-column.html',
  styleUrl: './each-column.css',
})
export class EachColumn implements OnInit {
  @Input() tasks: Task[] = [];
  @Input() columnName!: string;
  @Input() columnId!: number;
  @Input() boardId!: number;
  @Input() board!: BoardType;
  @Input() position!: number;

  taskService = inject(Tasks);

  ngOnInit() {}

  onDragDrop(event: DragEvent) {
    event.preventDefault();

    const taskToMove = this.taskService.moveTask;

    this.taskService
      .updateTask({ ...taskToMove!, column_id: this.columnId }, taskToMove?.id!)
      .subscribe((res: Task) => {
        console.log('successfully dragged and dropped....', res);
      });

    this.taskService.onMoveTaskComplete();
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }
}
