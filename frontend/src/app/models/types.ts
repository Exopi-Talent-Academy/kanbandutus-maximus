export enum TaskType {
  TODO = 'TO DO',
  PLAN = 'PLAN',
  IN_PROGRESS = 'IN PROGRESS',
  DONE = 'DONE',
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskType;
  assignee?: string;
  column_id?: number;
  position?: number;
}
