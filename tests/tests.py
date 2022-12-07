import requests

from app import config

def test_endpoint():
    d = {"message": {"text": "@pop cat /etc/os-release"}}
    response = requests.post(f"http://localhost:{config.port}/pop/{config.endpoint_termination}", json=d)
    data = response.json()
    assert "result" in data