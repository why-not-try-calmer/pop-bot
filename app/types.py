from __future__ import annotations

from concurrent.futures import Future
from enum import Enum, auto
from typing import Any


class Cmd(Enum):
    RUN = auto()
    HELP = auto()


class GettAble(dict):
    def __getattribute__(self, k: str) -> Any:
        return super().__getitem__(k)

    def __setattr__(self, k, v):
        super().__setitem__(k, v)


class Query(GettAble):
    input: str
    started: float
    chat_id: int
    cmd: Cmd | None
    future: Future[str] | None
    result: str | None
    error: str | None
    test: bool | None


class Payload(GettAble):
    chat_id: int
    parse_mode: str
    text: str
