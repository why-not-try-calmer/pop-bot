from os import environ
from typing import NamedTuple


class Config(NamedTuple):
    token: str
    port: int
    bot_name: str
    endpoint_termination: str


config = Config(
    environ["TOKEN"],
    int(environ.get("PORT", "8000")),
    environ.get("BOT_USERNAME", "pop"),
    f"bot{environ['TOKEN']}"
)
