import subprocess
from collections import UserDict
from queue import Queue
from time import sleep

from app.funcs import raise_error, reply

allowed_0 = [
    "apt",
    "cat",
    "cd",
    "ls",
    "echo",
    "find",
    "flatpak",
    "grep",
    "head",
    "history",
    "info",
    "less",
    "locate",
    "man",
    "more",
    "tail",
    "wc",
    "whereis",
    "which",
]

allowed_apt_1 = ["info", "list", "search", "show"]

allowed_flatpak_1 = ["search"]


def parse_validate(cmd: str) -> list[str]:
    args = cmd.split(" ")

    if not args[0] in allowed_0:
        raise_error(args[0], "bash", allowed_0)

    if args[0] == "apt":
        if not args[1] in allowed_apt_1:
            raise_error(args[1], "apt", allowed_apt_1)

    if args[0] == "flatpak":
        if not args[1] in allowed_flatpak_1:
            raise_error(args[1], "flatpak", allowed_flatpak_1)

    return args


def run_in_sub(cmd: str, args: list[str]) -> str:
    try:
        res = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            universal_newlines=True,
        )
        if res.returncode != 0:
            raise Exception(f"Failed! Errors: {res.stderr}")
        else:
            return res.stdout
    except TimeoutError:
        return f"Timed out: {cmd}"


class Query(UserDict):
    cmd: str
    chat_id: int
    result: str | None
    error: str | None


queue: Queue[Query] = Queue(maxsize=10)


def consume(q: Queue):
    while True:
        if query := q.get():
            try:
                cmd = query["cmd"]
                args = parse_validate(cmd)
                res = run_in_sub(cmd, args)
                query["result"] = res
                reply(query)
            except Exception as error:
                query["error"] = error
                reply(query)
        sleep(0.01)
