# Overview of Features

## Combined with User Stories and API Endpoints

| User Story | Feature | API Endpoint |
| :---- | :---- | :---- |
| *“As a product owner, I need to view the board, in order to see the state of the project.” “As a project manager, I need to review a task, in order to track it.”* | View the board | GET: api/boards |
| *“As a manager, I need to add a task, in order to delegate.” “As a user, I need an add task button, in order to add the task.”* | Add a task | POST: api/tasks |
| *“As a developer, I need to add a name to a task, in order to take responsibility for it.” “As a manager, I need to edit the task, in order to change the assignment.”* | Edit task contents (Set assignee on task) | PUT: api/tasks/\[id\] |
| *“As a developer, I need to move a task, in order to update the progress.”* | Move a task (Drag and drop on UI) | PUT: api/tasks/\[id\] |
| *“As a developer, I need to delete a task, in order to clean up the board.”* | Delete a task | DELETE: api/tasks/\[id\] |
| *“As a user, I need to sign into my account.”* | Find and select account to login as | GET: api/accounts |

# Nice to haves

| User Story | Feature | API Endpoint |
| :---- | :---- | :---- |
| *“As a manager, I need to adjust the number of columns.”* | Add a column <br> Delete a column | POST: api/columns <br> DELETE: api/columns/\[id\] |
| *“As a manager, I need to name the columns, in order to define the progression points.”* | Edit a column | PUT: api/columns/\[id\] |
| *“As a manager, I need to reorder the columns, in order to define the progression points.”* | Move a column (Drag and drop on UI) | PUT: api/columns/\[id\] |
| *“As a product owner, I need to add a new board, in order to start a new project.”* | Add a new board | POST: api/boards |
| *“As a manager, I need to switch to a different board, in order to handle different subteams.”* | Load a specific board | GET: api/boards/\[id\] |

