# import requests

from app.__main__ import get_cmd

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
