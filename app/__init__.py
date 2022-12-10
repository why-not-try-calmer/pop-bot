from typing import NamedTuple
from os import environ
from requests import Session

import logging


class SubConfig(NamedTuple):
    timeout: int


class Config(NamedTuple):
    token: str
    port: int
    bot_name: str
    endpoint_termination: str
    session: Session
    subprocesses: SubConfig


token = environ.get("TOKEN", "")

config = Config(
    token,
    int(environ.get("PORT", "8000")),
    environ.get("BOT_USERNAME", "pop"),
    f"bot{token}",
    Session(),
    SubConfig(int(environ.get("SUBPROC_TIMEOUT", "15"))),
)


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
