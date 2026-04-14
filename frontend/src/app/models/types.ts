export enum TaskType {
  TODO = 'To Do',
  PLAN = 'Plan',
  IN_PROGRESS = 'In Progress',
  DONE = 'Done',
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskType;
  assignee?: string;
}
