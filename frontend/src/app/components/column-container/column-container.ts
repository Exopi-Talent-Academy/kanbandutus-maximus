import { Component, inject, Input } from '@angular/core';
import { Container } from '../../shared/container/container';
import { Tasks } from '../../services/tasks';

@Component({
  selector: 'app-column-container',
  imports: [Container],
  templateUrl: './column-container.html',
  styleUrl: './column-container.css',
})
export class ColumnContainer {
  @Input() position!: number;
  @Input() columnName!: string;

  taskService = inject(Tasks);

  onDragDrop(event: DragEvent) {
    // event.preventDefault();
    const { name, position } = this.taskService.movingColumn;
    this.taskService
      .updateColumn({ name: name, position: this.position }, position)
      .subscribe((res) => console.log(res));
  }
  onDragOver(event: DragEvent) {
    event.preventDefault();
  }
}
