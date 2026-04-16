import { Component, inject, Input, OnInit } from '@angular/core';
import { Container } from '../../shared/container/container';
import { BoardType, Task } from '../../models/types';
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
  @Input() position!: number;
  @Input() boardId!: number;
  @Input() board!: BoardType;

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

    this.taskService.moveTask.subscribe((movedTask) => {
      if (movedTask) {
        this.updateBoard(movedTask);
      }
    });

    this.taskService.deleteBoard(this.boardId).subscribe(() => {
      console.log('Board deleted successfully after drag and drop');
      this.taskService.addBoard(this.board).subscribe(() => {
        console.log('Board updated successfully after drag and drop');
      });
    });

    this.taskService.onMoveTaskComplete();
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }

  updateBoard(newTask: Task) {
    this.board.columns = this.board.columns.map((column) => {
      if (column.position === this.position && column.name === this.columnName) {
        const newTasks = column.tasks.map((task) => {
          if (task.id === newTask.id) {
            return newTask;
          } else {
            return task;
          }
        });

        return {
          ...column,
          tasks: newTasks,
        };
      } else {
        return column;
      }
    });
  }
}
