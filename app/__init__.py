from typing import NamedTuple
from os import environ
from requests import Session


class Config(NamedTuple):
    token: str
    port: int
    bot_name: str
    endpoint_termination: str
    session: Session


token = environ.get("TOKEN", "")

config = Config(
    token,
    int(environ.get("PORT", "8000")),
    environ.get("BOT_USERNAME", "pop"),
    f"bot{token}",
    Session(),
)
