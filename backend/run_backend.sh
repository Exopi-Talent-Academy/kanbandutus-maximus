#!/usr/bin/bash
if [ ! -d "virtual-environment-kanban" ]; then
    python3 -m venv virtual-environment-kanban
fi
source virtual-environment-kanban/bin/activate
pip install -e ".[dev]"
uvicorn src.kanban.main:app --reload
