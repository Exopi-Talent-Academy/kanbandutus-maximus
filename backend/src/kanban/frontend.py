from abc import ABC, abstractmethod
from typing import Any, Optional


class FrontendInterface(ABC):
    @abstractmethod
    def call(self, method: str, path: str, body: Optional[dict] = None) -> dict:
        pass


class AngularMock(FrontendInterface):
    def __init__(self):
        self.responses = {}

    def call(self, method: str, path: str, body: Optional[dict] = None) -> dict:
        key = f"{method}:{path}"
        if key in self.responses:
            return self.responses[key]
        return {"error": "Not found in mock", "path": path, "method": method}

    def set_response(self, method: str, path: str, response: dict) -> None:
        key = f"{method}:{path}"
        self.responses[key] = response

    def clear_responses(self) -> None:
        self.responses = {}