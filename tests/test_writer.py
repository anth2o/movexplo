import json
import os
from unittest import mock

import pytest
from bs4 import BeautifulSoup

from movexplo.constants import TOFIND
from movexplo.utils import md5, write_json
from movexplo.writer import (
    enrich_file, enrich_files, format_video_file_name, get_files_info, list_files_info_from_folder
)


@pytest.fixture
def folder(tmpdir):
    with open(os.path.join(tmpdir, "movie.mp4"), "x") as f:
        f.write("ab")  # md5 = "187ef4436122d1cc2f40dc2b92f0eba0"

    folder_path = os.path.join(tmpdir, "folder_1")
    os.mkdir(folder_path)
    with open(os.path.join(folder_path, "movie_2.mkv"), "x") as f:
        f.write("a")  # md5 = "0cc175b9c0f1b6a831c399e269772661"
    open(os.path.join(folder_path, ".avi"), "x")

    folder_path = os.path.join(tmpdir, "folder_2")
    os.mkdir(folder_path)
    with open(os.path.join(folder_path, "movie_3.mkv"), "x") as f:
        f.write("abc")  # md5 = "900150983cd24fb0d6963f7d28e17f72"

    open(os.path.join(folder_path, "movie_4.mkv"), "x")

    folder_path = os.path.join(tmpdir, "folder_3")
    os.mkdir(folder_path)
    folder_path = os.path.join(folder_path, "folder_4")
    os.mkdir(folder_path)
    with open(os.path.join(folder_path, "movie_5.mkv"), "x") as f:
        f.write("abcd")  # md5 = "e2fc714c4727ee9395f324cd2e7f331f"

    return tmpdir


def test_get_files_info_no_input_file(folder):
    files_info = get_files_info(None, str(folder))
    # yapf: disable
    expected_files_info = [
        {"name": "folder_1", "size": 1, "md5": "0cc175b9c0f1b6a831c399e269772661", "renamed": True},
        {"name": "folder_4", "size": 4, "md5": "e2fc714c4727ee9395f324cd2e7f331f"},
        {"name": "movie", "size": 2, "md5": "187ef4436122d1cc2f40dc2b92f0eba0"},
        {"name": "movie_3", "size": 3, "md5": "900150983cd24fb0d6963f7d28e17f72"},
        {"name": "movie_4", "size": 0, "md5": "d41d8cd98f00b204e9800998ecf8427e"},
    ]
    # yapf: enable
    assert sorted(files_info, key=lambda a: a["name"]) == expected_files_info


def test_get_files_info_no_input_folder(tmpdir):
    file_info_path = os.path.join(tmpdir, "file_info.json")
    expected_files_info = [{"toto": "tata"}]
    write_json(file_info_path, expected_files_info)
    files_info = get_files_info(file_info_path, None)
    assert files_info == expected_files_info


def test_get_files_info(folder, tmpdir):
    with pytest.raises(ValueError):
        get_files_info(None, None)

    file_info_path = os.path.join(tmpdir, "file_info.json")
    with pytest.raises(FileNotFoundError):
        get_files_info(file_info_path, None)
    files_info = [{"md5": "0cc175b9c0f1b6a831c399e269772661", "name": "toto", "tata": "tutu"}]
    write_json(file_info_path, files_info)

    files_info = get_files_info(file_info_path, folder)
    # yapf: disable
    expected_files_info = [
        {"name": "folder_4", "size": 4, "md5": "e2fc714c4727ee9395f324cd2e7f331f"},
        {"name": "movie", "size": 2, "md5": "187ef4436122d1cc2f40dc2b92f0eba0"},
        {"name": "movie_3", "size": 3, "md5": "900150983cd24fb0d6963f7d28e17f72"},
        {"name": "movie_4", "size": 0, "md5": "d41d8cd98f00b204e9800998ecf8427e"},
        {"name": "toto", "size": 1, "md5": "0cc175b9c0f1b6a831c399e269772661", "renamed": True, "tata": "tutu"},
    ]
    # yapf: enable
    assert sorted(files_info, key=lambda a: a["name"]) == expected_files_info


def test_list_files_info_from_folder(folder):
    files_info = list_files_info_from_folder(str(folder))
    # yapf: disable
    expected_files_info = [
        {"name": "folder_1", "size": 1, "md5": "0cc175b9c0f1b6a831c399e269772661", "renamed": True},
        {"name": "folder_4", "size": 4, "md5": "e2fc714c4727ee9395f324cd2e7f331f"},
        {"name": "movie", "size": 2, "md5": "187ef4436122d1cc2f40dc2b92f0eba0"},
        {"name": "movie_3", "size": 3, "md5": "900150983cd24fb0d6963f7d28e17f72"},
        {"name": "movie_4", "size": 0, "md5": "d41d8cd98f00b204e9800998ecf8427e"},
    ]
    # yapf: enable
    assert sorted(files_info, key=lambda a: a["name"]) == expected_files_info


@pytest.mark.parametrize(
    "video_file_name, expected_video_file_name", [
        ("toto.mp4", "toto"),
        ("tata", "tata"),
        ("toto.mp4_tata.mp4", "toto.mp4_tata"),
        ("toto.avi_tata.mp4", "toto.avi_tata"),
    ]
)
def test_format_video_file_name(video_file_name, expected_video_file_name):
    assert format_video_file_name(video_file_name) == expected_video_file_name


def mock_enrich_file(file_info, *args, **kwargs):
    file_info["mock_enriched"] = True
    return file_info


@pytest.mark.parametrize("force_enrich", [True, False])
@mock.patch("movexplo.writer.enrich_file", side_effect=mock_enrich_file)
def test_enrich_files(mockingbird, force_enrich):
    files_info = [
        {
            "a": "b",
            "enriched": True,
            "name": "a"
        },
        {
            "c": "d",
            "enriched": False,
            "name": "c"
        },
        {
            "e": "f",
            "name": "e"
        },
    ]
    if force_enrich:
        expected_files_info = [
            {
                "a": "b",
                "enriched": True,
                "mock_enriched": True,
                "name": "a"
            },
            {
                "c": "d",
                "enriched": False,
                "mock_enriched": True,
                "name": "c"
            },
            {
                "e": "f",
                "mock_enriched": True,
                "name": "e"
            },
        ]
    else:
        expected_files_info = [
            {
                "a": "b",
                "enriched": True,
                "name": "a"
            },
            {
                "c": "d",
                "enriched": False,
                "mock_enriched": True,
                "name": "c"
            },
            {
                "e": "f",
                "mock_enriched": True,
                "name": "e"
            },
        ]
    files_info = enrich_files(files_info, force_enrich)
    assert files_info == expected_files_info


def mock_get_link_from_file(file_info, *args, **kwargs):
    return f"www.a-dumb-link.com/{file_info['name']}"


def mock_get_soup_from_url(url, *args, **kwargs):
    if url.endswith("toto"):
        return BeautifulSoup("<div>TUTU</div>", "html.parser")
    return BeautifulSoup("<a>TUTU</a>", "html.parser")


field_to_method = {"title": lambda soup: soup.find("div").text}


@mock.patch("movexplo.writer.get_link_from_file", side_effect=mock_get_link_from_file)
@mock.patch("movexplo.writer.get_soup_from_url", side_effect=mock_get_soup_from_url)
@mock.patch("movexplo.writer.FIELD_TO_METHOD", field_to_method)
@pytest.mark.parametrize("name", ["toto", "tata"])
def test_enrich_file(mockingbird, mocker, name):
    file_info = {"name": name}
    file_info = enrich_file(file_info)
    expected_file_info = {
        "name": name,
        "enriched": True,
        "title": "TUTU" if name == "toto" else TOFIND,
        "link": f"www.a-dumb-link.com/{name}"
    }
    assert file_info == expected_file_info
