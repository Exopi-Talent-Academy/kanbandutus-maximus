export interface Task {
  id: string;
  title: string;
  description?: string;
  assignee?: string;
  column_id?: number;
  position?: number;
}

export const columnNames = {
  0: 'To Do',
  1: 'Plan',
  2: 'In Progress',
  3: 'Done',
};
