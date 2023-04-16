import subprocess
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from time import sleep

from app import logging
from app.funcs import reply, to_error
from app.types import Cmd

logger = logging.getLogger(__name__)

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


def run_cmd(cmd: str, timeout: int) -> str:
    result = subprocess.run(
        cmd,
        shell=True,
        timeout=timeout,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stderr if result.returncode != 0 else result.stdout


def run_task(_input: str, timeout=6) -> str:
    return run_cmd(_input, timeout).strip()


def process(proc_q: Queue, res_q: Queue):
    with ThreadPoolExecutor() as pool:
        while True:
            query = proc_q.get()
            logger.info(
                f"Dequeuing process_q: {query.input}. Remaining on queue: {proc_q.qsize()}"
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
            except Exception as error:
                query.error = f"This command failed. {query.input}. Error: {error}"
                if "future" in query and query.future.running():
                    query.future.cancel()
            finally:
                res_q.put(query)
                proc_q.task_done()
                logger.info(f"Done process_q: {query.input}")
                sleep(0.01)


def consume(res_q: Queue):
    while True:
        query = res_q.get()
        logger.info(
            f"Dequeuing consume_q: {query.input}. Remaining on queue: {res_q.qsize()}"
        )
        try:
            if "future" in query:
                query.result = query.future.result()
        except Exception as error:
            query.error = str(error)
            logger.error(
                f"(consume_q) Ran into an exception after unwrapping query: {str(error)}. Traceback: {error.with_traceback}"
            )
        finally:
            if "future" in query and query.future.running():
                query.future.cancel()
            reply(query)
            res_q.task_done()
            logger.info(f"Done consume_q: {query.input}")
            sleep(0.01)
