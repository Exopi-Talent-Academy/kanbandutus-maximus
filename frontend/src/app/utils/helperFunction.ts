import { BoardType, Task } from '../models/types';

export function updateBoard(
  newTask: Task,
  fromColumnId: number,
  board: BoardType,
  columnId: number,
) {
  board.columns = board.columns.map((column) => {
    if (column.id === fromColumnId) {
      const newTasks = column.tasks.filter((task) => {
        return task.id !== newTask.id;
      });

      return {
        ...column,
        tasks: newTasks,
      };
    } else if (column.id === columnId) {
      return {
        ...column,
        tasks: [...column.tasks, { ...newTask, column_id: column.id }],
      };
    } else {
      return column;
    }
  });
}
