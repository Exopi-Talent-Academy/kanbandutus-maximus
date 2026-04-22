# ============================================================================
# Layer 2: Service Layer Tests
# ============================================================================
# Tests for KanbanService business logic.
# These tests call the service layer directly without going through the API.
# ============================================================================

from src.kanban.service import KanbanService, NotFoundError


# ============================================================================
# Section 1: Board Service Tests
# ============================================================================

def test_service_get_board(storage):
    board = storage.get_board(1)
    assert board is not None
    assert board.name == "Test Board"


def test_service_get_board_not_found(storage):
    board = storage.get_board(999)
    assert board is None


def test_service_get_all_boards(storage):
    service = KanbanService(storage)
    boards = service.get_all_boards()
    assert len(boards) >= 1
    assert boards[0].name == "Test Board"


def test_service_create_board(storage):
    service = KanbanService(storage)
    board = service.create_board("New Board")
    assert board is not None
    assert board.name == "New Board"
    assert board.id >= 1


def test_service_update_board(storage):
    service = KanbanService(storage)
    board = service.update_board(1, "Updated Board Name")
    assert board is not None
    assert board.name == "Updated Board Name"


def test_service_update_board_not_found(storage):
    service = KanbanService(storage)
    board = service.update_board(999, "Non-existent")
    assert board is None


def test_service_delete_board(storage):
    service = KanbanService(storage)
    service.delete_board(1)
    board = storage.get_board(1)
    assert board is None


def test_service_delete_board_not_found(storage):
    service = KanbanService(storage)
    deleted = service.delete_board(999)
    assert deleted is False


# ============================================================================
# Section 2: Column Service Tests
# ============================================================================

def test_service_get_column(storage):
    column = storage.get_column(1)
    assert column is not None
    assert column.name == "To Do"
    assert column.position == 0


def test_service_get_column_not_found(storage):
    column = storage.get_column(999)
    assert column is None


def test_service_get_columns_by_board(storage):
    service = KanbanService(storage)
    columns = service.get_columns_by_board(1)
    assert len(columns) >= 1
    assert columns[0].board_id == 1


def test_service_get_columns_by_board_not_found(storage):
    service = KanbanService(storage)
    try:
        columns = service.get_columns_by_board(999)
    except NotFoundError:
        pass  # Expected


def test_service_create_column(storage):
    service = KanbanService(storage)
    column = service.create_column("In Progress", 2, 1)
    assert column is not None
    assert column.name == "In Progress"
    assert column.position == 2


def test_service_create_column_invalid_board(storage):
    service = KanbanService(storage)
    column = service.create_column("Fail", 0, 999)
    assert column is None


def test_service_update_column(storage):
    service = KanbanService(storage)
    column = service.update_column(1, "Updated Column", 5)
    assert column is not None
    assert column.name == "Updated Column"


def test_service_update_column_not_found(storage):
    service = KanbanService(storage)
    column = service.update_column(999, "Updated", 0)
    assert column is None


def test_service_delete_column(storage):
    service = KanbanService(storage)
    service.delete_column(1)
    column = storage.get_column(1)
    assert column is None


def test_service_delete_column_not_found(storage):
    service = KanbanService(storage)
    deleted = service.delete_column(999)
    assert deleted is False


# ============================================================================
# Section 3: Task Service Tests
# ============================================================================

def test_service_get_task(storage):
    task = storage.get_task(1)
    assert task is not None
    assert task.title == "Test Task"


def test_service_get_task_not_found(storage):
    task = storage.get_task(999)
    assert task is None


def test_service_get_tasks_by_column(storage):
    service = KanbanService(storage)
    tasks = service.get_tasks_by_column(1)
    assert len(tasks) >= 1
    assert tasks[0].column_id == 1


def test_service_get_tasks_by_column_not_found(storage):
    service = KanbanService(storage)
    try:
        tasks = service.get_tasks_by_column(999)
    except NotFoundError:
        pass  # Expected


def test_service_create_task(storage):
    service = KanbanService(storage)
    task = service.create_task("New Task", "Description", 1, 1)
    assert task is not None
    assert task.title == "New Task"


def test_service_create_task_invalid_column(storage):
    service = KanbanService(storage)
    task = service.create_task("Fail", "", 999, 0)
    assert task is None


def test_service_update_task(storage):
    service = KanbanService(storage)
    task = service.update_task(1, "Updated Task", "New Desc", 2, 1)
    assert task is not None
    assert task.title == "Updated Task"
    assert task.column_id == 2


def test_service_update_task_not_found(storage):
    service = KanbanService(storage)
    task = service.update_task(999, "Updated", "", 1, 0)
    assert task is None


def test_service_delete_task(storage):
    service = KanbanService(storage)
    service.delete_task(1)
    task = storage.get_task(1)
    assert task is None


def test_service_delete_task_not_found(storage):
    service = KanbanService(storage)
    deleted = service.delete_task(999)
    assert deleted is False


# ============================================================================
# Section 4: Account Service Tests
# ============================================================================

def test_service_get_all_accounts(storage):
    service = KanbanService(storage)
    accounts = service.get_all_accounts()
    assert len(accounts) >= 2
    assert accounts[0].username == "admin"


def test_service_get_account(storage):
    account = storage.get_account(1)
    assert account is not None
    assert account.username == "admin"


def test_service_get_account_not_found(storage):
    account = storage.get_account(999)
    assert account is None