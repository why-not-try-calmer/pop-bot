import subprocess
from collections import UserDict, deque
from concurrent.futures import Future, ThreadPoolExecutor
from functools import reduce
from queue import Queue
from typing import Deque, NamedTuple

from app.funcs import raise_error, reply

allowed_0 = {
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
    "uptime",
    "wc",
    "whereis",
    "which",
}

allowed_apt_1 = {"info", "list", "search", "show"}

allowed_flatpak_1 = {"search"}


def parse_validate(cmd: str) -> list[list[str]]:
    un_piped = cmd.split("|")
    un_piped_args = []

    for args in un_piped:
        split_args = args.strip().split(" ")

        if not split_args[0] in allowed_0:
            raise_error(split_args[0], "bash", list(allowed_0))

        if split_args[0] == "apt":
            if not split_args[1] in allowed_apt_1:
                raise_error(split_args[1], "apt", list(allowed_apt_1))

        if split_args[0] == "flatpak":
            if not split_args[1] in allowed_flatpak_1:
                raise_error(split_args[1], "flatpak", list(allowed_flatpak_1))

        un_piped_args.append(split_args)

    return un_piped_args


def run_in_sub(pipes: list[list[str]]) -> str:
    def reducer(prev_proc: subprocess.Popen, args: list[str]):
        proc = subprocess.Popen(
            args,
            stdin=prev_proc.stdout,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        )
        print("WAITING!!!")
        prev_proc.wait(timeout=5)
        return proc

    start = subprocess.Popen(
        pipes[0],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    finale = reduce(reducer, pipes[1:], start)
    output = finale.stdout.read()  # type:ignore
    finale.terminate()
    return output


class Query(UserDict):
    cmd: str
    chat_id: int
    result: str | None
    error: str | None


class Job(NamedTuple):
    query: Query
    future: Future[None]


queue: Queue[Query] = Queue(maxsize=10)


def process(query: Query, result=None):
    try:
        if result:
            query["result"] = result
        else:
            args = parse_validate(query["cmd"])
            query["result"] = run_in_sub(args)
        reply(query)
    except Exception as error:
        query["error"] = error
        reply(query)


def consume(q: Queue):

    with ThreadPoolExecutor() as pool:
        submitted: Deque[Job] = deque()
        while True:
            if query := q.get():
                try:
                    future = pool.submit(process, query)
                    next_job = Job(query, future)
                    submitted.append(next_job)

                    if submitted:
                        prev_job: Job = submitted.popleft()
                        prev_job.future.result(timeout=10)

                    q.task_done()
                except TimeoutError:
                    query["error"] = f"This command timeout! {query.cmd}"
                    reply(query)
