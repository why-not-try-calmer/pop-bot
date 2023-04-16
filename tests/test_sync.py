from __future__ import annotations

import math
from logging import getLogger
from time import sleep

import requests

from app import config, cons_queue, proc_queue
from app.__main__ import parse_query, start_workers
from app.funcs import parse_query, slice_on_n
from app.types import Cmd, Query
from app.workers import run_task, try_to_invalidate

logger = getLogger(__name__)


def test_config():
    assert config.port == 8000
    assert not config.is_production


def test_get_cmd():
    update = {"message": {"text": "/r apt list --installed", "chat": {"id": 1234}}}
    assert parse_query(update)


def test_get_chat_id():
    update = {"message": {"text": "/r apt list --installed", "chat": {"id": 1234}}}
    assert parse_query(update)


def test_get_help():
    update = {"message": {"text": "/help", "chat": {"id": 1234}}}
    parse_query(update)


def test_slices():
    response = requests.get(
        "https://baconipsum.com/api/?type=meat-and-filler&paras=15&format=text",
    )
    text = response.text
    expected_slices = math.ceil(len(text) / 4096)
    slices = slice_on_n(text, 4096)
    assert len(slices) == expected_slices


def test_sub():
    cmd = "apt list --installed"
    assert try_to_invalidate(cmd) is None
    result = run_task(cmd)
    assert len(result.split("\n")) > 250


def test_get_parse_validate_run():
    update = {
        "message": {
            "text": "/r apt list --installed | wc -l | wc -c",
            "chat": {"id": 1234},
        },
    }
    query = parse_query(update)
    assert query
    assert run_task(query.input)


def test_flatpak_search():
    update = {
        "message": {
            "text": "/r flatpak search qgis",
            "chat": {"id": 1234},
        },
    }
    query = parse_query(update)
    assert query
    result = run_task(query.input, timeout=12)
    logger.info(result)
    assert len(result.split("\n")) >= 2


def test_long_command():
    input1 = "apt list --installed | wc -l"
    update = {
        "message": {
            "text": f"/r {input1}",
            "chat": {"id": 1234},
        },
    }
    query = parse_query(update)
    assert query
    result = run_task(query.input)
    final_result = result.split("\n")[-1]
    assert int(final_result) > 1000


def test_worker():
    start_workers()
    input1 = "apt list --installed | wc -l | wc -c"
    input2 = "echo 123"
    query1 = Query(input=input1, chat_id=1234, test=True, started=0, cmd_type=Cmd.RUN)
    query2 = Query(input=input2, chat_id=1234, test=True, started=0, cmd_type=Cmd.RUN)
    proc_queue.put(query1)
    proc_queue.put(query2)
    sleep(3)
    assert proc_queue.qsize() == 0
    assert cons_queue.qsize() == 0
