import os
from unittest import mock

from movexplo.app import app
from movexplo.utils import write_json


def test_app_get(tmpdir):
    data = [{
        "name": "toto",
        "image": "tutu",
        "link": "tata",
    }]
    static_folder = os.path.join(tmpdir, "static")
    os.makedirs(static_folder)
    data_path = os.path.join(static_folder, "data.json")
    write_json(data_path, data)

    with mock.patch("movexplo.app.DATA_PATH", data_path), app.test_client() as c:
        response = c.get("/")

    assert 'href="tata"' in response.data.decode("utf-8")


def test_app_post(tmpdir):
    data = [{
        "name": "toto",
        "image": "tutu",
        "link": "tata",
    }]
    static_folder = os.path.join(tmpdir, "static")
    os.makedirs(static_folder)
    data_path = os.path.join(static_folder, "data.json")
    write_json(data_path, data)

    with mock.patch("movexplo.app.DATA_PATH", data_path), app.test_client() as c:
        response = c.post("/", data={"title": "toto"})

    assert 'href="tata"' in response.data.decode("utf-8")

    with mock.patch("movexplo.app.DATA_PATH", data_path), app.test_client() as c:
        response = c.post("/", data={"title": "laiuebfzleb"})

    assert 'href="tata"' not in response.data.decode("utf-8")
