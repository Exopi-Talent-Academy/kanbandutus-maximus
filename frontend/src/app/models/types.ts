export interface Task {
  id: number;
  title: string;
  description?: string;
  assignee?: string;
  column_id?: number;
  position?: number;
}

export interface ColumnType {
  id: number;
  name: string;
  position: number;
  board_id: number;
  tasks: Task[];
}

export interface BoardType {
  id: number;
  name: string;
  columns: ColumnType[];
}

export const columnNames = {
  0: 'To Do',
  1: 'Plan',
  2: 'In Progress',
  3: 'Done',
};
