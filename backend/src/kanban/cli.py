import argparse

from .config import get_data_file, get_database_url
from .storage import JsonStorage, SqlAlchemyStorage


def reimport_json_to_sqlite() -> tuple[int, int, int]:
    json_storage = JsonStorage(get_data_file())
    sqlite_storage = SqlAlchemyStorage()

    data = json_storage.load()
    sqlite_storage.save(data)

    loaded = sqlite_storage.load()
    return len(loaded.boards), len(loaded.columns), len(loaded.tasks)


def reimport_json_to_sqlite_cli() -> None:
    boards, columns, tasks = reimport_json_to_sqlite()
    print(
        f"Re-import complete into {get_database_url()}: "
        f"{boards} boards, {columns} columns, {tasks} tasks"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Kanban CLI utilities")
    parser.add_argument(
        "command",
        nargs="?",
        default="reimport-json-to-sqlite",
        choices=["reimport-json-to-sqlite"],
        help="Utility command to run",
    )
    args = parser.parse_args()

    if args.command == "reimport-json-to-sqlite":
        reimport_json_to_sqlite_cli()


if __name__ == "__main__":
    main()
