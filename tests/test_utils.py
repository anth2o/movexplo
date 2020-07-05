import os

import pytest

from movexplo.utils import (duration_to_int, md5, order_files, remove_special_characters, search_files)


@pytest.mark.parametrize(
    "input,expected_output", [
        ("perceval", "perceval"),
        ("comté", "comte"),
        ("perçeval", "perceval"),
        ("à", "a"),
    ]
)
def test_remove_special_characters(input, expected_output):
    output = remove_special_characters(input)
    assert output == expected_output


def test_md5(tmpdir):
    filename = os.path.join(tmpdir, "test")
    with open(filename, "w+") as f:
        f.write("omelette du fromage")
    output = md5(filename)
    expected_output = "538792eef9f1e7d22f772743457a67f0"
    assert output == expected_output


@pytest.mark.parametrize(
    "input,expected_output", [
        ("28 min", 28),
        ("2 h 08 min", 2 * 60 + 8),
        ("3 h", 3 * 60),
    ]
)
def test_duration_to_int(input, expected_output):
    output = duration_to_int(input)
    assert output == expected_output


def test_search_files():
    files = [
        {
            "name": "toto",
            "director": "tata",
            "genre": "tutu"
        },
        {
            "name": "tata",
            "director": "tutu",
            "duration": 20
        },
    ]

    assert search_files(files, "") == files
    assert search_files(files, "tutu") == [files[1]]
    assert search_files(files, "tata") == files
    assert search_files(files, "toto") == [files[0]]
    assert search_files(files, "titi") == []
    with pytest.raises(AttributeError):
        search_files(files, 20)


def test_order_files():
    files = [
        {
            "name": "toto",
            "director": "tata", # fourth element
            "genre": "tutu",
            "date": "2020-06-10"
        },
        {
            "name": "flute",
            "director": "tutu louis", # second element
            "duration": 30,
            "date": "2019-12-04"
        },
        {
            "name": "tata",
            "director": "tutu louis", # first element
            "duration": 20,
            "date": "2018-08-12"
        },
        {
            "name": "flute",
            "director": "tutu poulet", # third element
            "duration": 33,
            "date": "2018-11-07"
        },
        {
            "name": "trololo",
            "director": "tutu poulet", # ignored
            "duration": 33,
            "date": "2018-11-07",
            "ignore": True
        },
        {
            "name": "non", # last element
        },
    ]

    expected_output = [files[2], files[1], files[3], files[0], files[-1]]
    output = order_files(files)
    assert output == expected_output
