#!/bin/bash

python3 -m venv virtual-environment-kanban
source virtual-environment-kanban/bin/activate
pip install -e ".[dev]"
uvicorn src.kanban.main:app --reload
