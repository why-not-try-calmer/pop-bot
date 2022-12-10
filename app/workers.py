import subprocess
from concurrent.futures import CancelledError, ThreadPoolExecutor
from functools import reduce
from queue import Queue

from app import logging
from app.funcs import reply, to_error
from app.types import Cmd, Query

allowed_0 = [
    "apt",
    "cat",
    "ls",
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
    "whoami",
    "whereis",
    "which",
]

allowed_apt_1 = ["info", "list", "search", "show"]

allowed_flatpak_1 = ["search"]


def validate_or_err(cmd: str) -> list[list[str]] | str:
    un_piped = cmd.split("|")
    un_piped_args = []

    for args in un_piped:
        split_args = args.strip().split(" ")

        if not split_args[0] in allowed_0:
            return to_error(split_args[0], "bash", allowed_0)

        if split_args[0] == "apt":
            if not split_args[1] in allowed_apt_1:
                return to_error(split_args[1], "apt", allowed_apt_1)

        if split_args[0] == "flatpak":
            if not split_args[1] in allowed_flatpak_1:
                return to_error(split_args[1], "flatpak", allowed_flatpak_1)

        un_piped_args.append(split_args)

    return un_piped_args


def run_in_sub(pipes: list[list[str]]) -> str:
    def wait_kill(p, drain=False, timeout=5) -> None | str:
        try:
            if p.wait(timeout) != 0:
                p.kill()
        except Exception:
            p.kill()
        finally:
            return p.stdout.read() if drain else None

    def reducer(prev_proc: subprocess.Popen, args: list[str]):
        proc = subprocess.Popen(
            args,
            stdin=prev_proc.stdout,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        )
        wait_kill(prev_proc)
        return proc

    start = subprocess.Popen(
        pipes[0],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    finale = reduce(reducer, pipes[1:], start)
    return wait_kill(finale, drain=True)  # type: ignore


proc_queue: Queue[Query] = Queue(maxsize=50)
cons_queue: Queue[Query] = Queue(maxsize=50)


def process_q(proc_q: Queue, res_q: Queue):
    with ThreadPoolExecutor() as pool:

        while True:
            query = proc_q.get()
            logging.info(
                f"Dequeuing process_q: {query}. Remaining on queue: {proc_q.qsize()}"
            )
            try:
                match query.cmd_type:

                    case Cmd.RUN:
                        piped_args_or_error = validate_or_err(query.input)

                        if isinstance(piped_args_or_error, str):
                            query.error = piped_args_or_error

                        else:
                            query.future = pool.submit(run_in_sub, piped_args_or_error)

                    case Cmd.HELP:
                        query.result = "Use '/run' (or '/r') <command> <arguments> to issue commands just as you would in a Pop!_OS terminal."

                res_q.put(query)
            except (TimeoutError, CancelledError):
                query.error = f"This command timed out or was cancelled. {query.input}"
                res_q.put(query)
            finally:
                proc_q.task_done()
                logging.info(f"Done process_q: {query}")


def consume_q(res_q: Queue):
    while True:
        query = res_q.get()
        logging.info(
            f"Dequeuing consume_q: {query}. Remaining on queue: {res_q.qsize()}"
        )
        try:
            if "error" in query:
                if "future" in query and query.future.running():
                    query.future.cancel()

            elif "future" in query:
                query.result = query.future.result(timeout=5)

            reply(query)
        except Exception as error:
            query.error = str(error)
            reply(query)
            logging.error(
                f"(consume_q) Ran into an exception after unwrapping query: {str(error)}. Traceback: {error.with_traceback}"
            )
        finally:
            res_q.task_done()
            logging.info(f"Done consume_q: {query}")
