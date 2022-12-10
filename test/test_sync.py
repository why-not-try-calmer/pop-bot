import requests
import math

from app.__main__ import get_cmd
from app.worker import run_in_sub, parse_validate
from app.funcs import get_chatid, slice_on_n


def test_get_cmd():
    update = {"message": {"text": "/r apt list --installed"}}
    assert get_cmd(update)


def test_get_chat_id():
    update = {"message": {"text": "/r apt list --installed", "chat": {"id": 1234}}}
    assert get_chatid(update)


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
    args = parse_validate(cmd)
    result = run_in_sub(args)
    assert len(result.split("\n")) > 250


def test_get_parse_validate_run():
    update = {
        "message": {
            "text": "/r apt list --installed | wc -l | wc -c",
            "chat": {"id": 1234},
        }
    }
    cmd = get_cmd(update)
    if not cmd:
        raise AssertionError
    args = parse_validate(cmd)
    result = run_in_sub(args)
    assert result.strip() == "5"
