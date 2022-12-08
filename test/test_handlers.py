import requests
import math

from app.__main__ import get_cmd
from app.funcs import slice_on_4096

"""
def test_endpoint():
    d = {"message": {"text": "@pop cat /etc/os-release"}}
    response = requests.post(f"http://localhost:{config.port}/pop/{config.endpoint_termination}", json=d)
    data = response.json()
    assert "result" in data
"""


def test_get_cmd():
    update = {"message": {"text": "/r apt list --installed"}}
    assert get_cmd(update)

def test_slices():
    response = requests.get("https://baconipsum.com/api/?type=meat-and-filler&paras=15&format=text")
    text = response.text
    expected_slices = math.ceil(len(text)/4096)
    slices = slice_on_4096(text)
    assert len(slices) == expected_slices