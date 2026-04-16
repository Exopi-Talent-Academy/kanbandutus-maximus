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
    const fromColumnId = this.taskService.fromColumnId;

    console.log('Drag dropped on column:', this.columnId, 'from column:', fromColumnId);
    console.log('Task to move:', taskToMove);

    updateBoard(taskToMove!, fromColumnId, this.board, this.columnId);

    this.taskService.updateBoard(this.boardId.toString(), this.board).subscribe(() => {
      console.log('Board updated successfully after drag and drop');
    });

    this.taskService.onMoveTaskComplete();
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }
}
