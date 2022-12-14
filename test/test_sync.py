import math
from time import sleep

import requests

from app import cons_queue, proc_queue
from app.__main__ import parse_query, start_workers
from app.funcs import parse_query, slice_on_n
from app.types import Cmd, Query
from app.workers import run_task, try_to_invalidate


def test_get_cmd():
    update = {"message": {"text": "/r apt list --installed", "chat": {"id": 1234}}}
    assert parse_query(update)


def test_get_chat_id():
    update = {"message": {"text": "/r apt list --installed", "chat": {"id": 1234}}}
    assert parse_query(update)


def test_get_help():
    update = {"message": {"text": "/help", "chat": {"id": 1234}}}
    query = parse_query(update)


def test_slices():
    response = requests.get(
        "https://baconipsum.com/api/?type=meat-and-filler&paras=15&format=text"
    )
    text = response.text
    expected_slices = math.ceil(len(text) / 4096)
    slices = slice_on_n(text, 4096)
    assert len(slices) == expected_slices


def test_sub():
    cmd = "apt list --installed"
    if not try_to_invalidate(cmd):
        result = run_task(cmd)
        assert len(result.split("\n")) > 250


def test_get_parse_validate_run():
    update = {
        "message": {
            "text": "/r apt list --installed | wc -l | wc -c",
            "chat": {"id": 1234},
        }
    }
    if query := parse_query(update):
        if not try_to_invalidate(query.input):
            assert run_task(query.input)


""" REQUIRES FLATPAK TO BE SET
def test_flatpak_search():
    update = {
        "message": {
            "text": "/r flatpak search qgis",
            "chat": {"id": 1234},
        }
    }
    cmd = get_cmd(update)
    if not cmd:
        raise AssertionError
    args = parse_validate(cmd)
    result = run_in_sub(args)
    assert len(result.split("\n")) >= 2
"""


def test_worker():
    start_workers()

    input1 = "apt list --installed | wc -l | wc -c"
    input2 = "echo 123"
    query1 = Query(input=input1, chat_id=1234, test=True, started=0, cmd_type=Cmd.RUN)
    query2 = Query(input=input2, chat_id=1234, test=True, started=0, cmd_type=Cmd.RUN)
    proc_queue.put_nowait(query1)
    proc_queue.put_nowait(query2)
    sleep(5)
    assert proc_queue.qsize() == 0
    assert cons_queue.qsize() == 0
