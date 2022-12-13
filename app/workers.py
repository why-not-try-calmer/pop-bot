import subprocess
from concurrent.futures import CancelledError, ThreadPoolExecutor
from re import compile
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


def try_to_invalidate(cmd: str) -> str | None:
    split_args = cmd.strip().split(" ")

    if not split_args[0] in allowed_0:
        return to_error(split_args[0], "bash", allowed_0)

    if split_args[0] == "apt":
        if not split_args[1] in allowed_apt_1:
            return to_error(split_args[1], "apt", allowed_apt_1)

    if split_args[0] == "flatpak":
        if not split_args[1] in allowed_flatpak_1:
            return to_error(split_args[1], "flatpak", allowed_flatpak_1)


exp = compile("[A-Z]{3,}")


def run_cmd(cmd: str) -> list[str]:
    with subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    ) as proc:
        return proc.stdout.readlines()  # type: ignore


def post_proc(lines: list[str]) -> str:
    pred = lambda l: l != "\n" and not exp.findall(l)
    acceptable = filter(pred, lines)
    last = "\n".join(acceptable)
    return last.strip()


def run_task(_input: str) -> str:
    _output = run_cmd(_input)
    return post_proc(_output)


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

                        if err := try_to_invalidate(query.input):
                            query.error = err

                        else:
                            query.future = pool.submit(run_task, query.input)

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

            if "future" in query and query.future.running():
                query.future.cancel()

            query.error = str(error)
            reply(query)
            
            logging.error(
                f"(consume_q) Ran into an exception after unwrapping query: {str(error)}. Traceback: {error.with_traceback}"
            )

        finally:
            res_q.task_done()
            logging.info(f"Done consume_q: {query}")
