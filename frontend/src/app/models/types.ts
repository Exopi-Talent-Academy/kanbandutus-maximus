export interface Task {
  id: string;
  title: string;
  description?: string;
  assignee?: string;
  column_id?: number;
  position?: number;
}

export interface BoardType {
  id: number;
  name: string;
  columns: {
    id: number;
    name: string;
    tasks: Task[];
  }[];
}

export interface ColumnType {
  id: number;
  name: string;
  position: number;
  board_id: number;
  tasks: Task[];
}

export const columnNames = {
  0: 'To Do',
  1: 'Plan',
  2: 'In Progress',
  3: 'Done',
};
