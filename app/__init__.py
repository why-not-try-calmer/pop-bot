import logging
from os import environ
from queue import Queue
from typing import NamedTuple

from requests import Session


class SubConfig(NamedTuple):
    timeout: int


class Config(NamedTuple):
    token: str
    port: int
    bot_name: str
    endpoint_termination: str
    session: Session
    subprocesses: SubConfig
    is_production: bool


token = environ.get("TOKEN", "")

config = Config(
    token,
    int(environ.get("PORT", "8000")),
    environ.get("BOT_USERNAME", "pop"),
    f"bot{token}",
    Session(),
    SubConfig(int(environ.get("SUBPROC_TIMEOUT", "15"))),
    int(environ.get("PROD", 1)) == 1
)

proc_queue = Queue(maxsize=50)
cons_queue = Queue(maxsize=50)

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
