import os
from unittest import mock

from movexplo.app import app
from movexplo.utils import write_json


def test_app_get_template(tmpdir):
    """Tests that the template is used and that is correctly displayed."""
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

    html = response.data.decode("utf-8")
    assert 'href="tata"' in html
    assert 'src="tutu"' in html

def test_app_get_data():
    """Test that data.json is found by the app."""
    with app.test_client() as c:
        response = c.get("/")

    assert response.status_code == 200

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

    html = response.data.decode("utf-8")
    assert 'href="tata"' in html
    assert 'src="tutu"' in html

    with mock.patch("movexplo.app.DATA_PATH", data_path), app.test_client() as c:
        response = c.post("/", data={"title": "laiuebfzleb"})

    html = response.data.decode("utf-8")
    assert 'href="tata"' not in html
    assert 'src="tutu"' not in html
