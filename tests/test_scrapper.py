from unittest import mock

import pytest
from bs4 import BeautifulSoup

from movexplo.constants import TOFIND
from movexplo.scrapper import (
    get_date_from_soup, get_director_from_soup, get_duration_from_soup, get_genres_from_soup,
    get_image_from_soup, get_link_from_file, get_link_from_soup, get_soup_from_url
)


def mock_requests_get(*args, **kwargs):
    result = mock.Mock()
    result.text = "<div>TEST</div>"
    return result


@mock.patch("movexplo.scrapper.requests.get", side_effect=mock_requests_get)
def test_soup_from_url(mockingbird):
    soup = get_soup_from_url("toto")
    expected_soup = BeautifulSoup("<div>TEST</div>", 'html.parser')
    assert soup == expected_soup


def mock_get_soup_from_url(url, *args, **kwargs):
    name = url.split("search?q=")[1].split("&categories")[0]
    if name == "toto":
        html = "<div class='ProductListItem__TextContainer-sc-1ci68b-8 kKuZab'><a href='https://www.senscritique.com/morceau/Poulet/13259275'></div>"
    else:
        html = ""
    return BeautifulSoup(html, "html.parser")


@mock.patch("movexplo.scrapper.get_soup_from_url", side_effect=mock_get_soup_from_url)
@pytest.mark.parametrize("name", ["toto", "tata"])
def test_get_link_from_file(mockingbird, name):
    file_info = {"name": name}
    link = get_link_from_file(file_info)
    expected_link = "https://www.senscritique.com/morceau/Poulet/13259275" if name == "toto" else TOFIND
    assert link == expected_link


def test_get_link_from_soup():
    html = "<div class='ProductListItem__TextContainer-sc-1ci68b-8 kKuZab'><a href='https://www.senscritique.com/morceau/Poulet/13259275'></div>"
    soup = BeautifulSoup(html, "html.parser")
    link = get_link_from_soup(soup)
    assert link == "https://www.senscritique.com/morceau/Poulet/13259275"


def test_get_image_from_soup():
    html = "<img class='pvi-hero-poster' src='poulet'>"
    soup = BeautifulSoup(html, "html.parser")
    image = get_image_from_soup(soup)
    assert image == "poulet"


def test_get_director_from_soup():
    html = "<span itemprop='name'>jacquouille</span>"
    soup = BeautifulSoup(html, "html.parser")
    director = get_director_from_soup(soup)
    assert director == "jacquouille"


def test_get_date_from_soup():
    html = "<li class='pvi-productDetails-item nowrap'><time datetime='1991-11-15' >15 novembre 1991</time></li>"
    soup = BeautifulSoup(html, "html.parser")
    date = get_date_from_soup(soup)
    assert date == "1991-11-15"


def test_get_genres_from_soup():
    html = "<span itemprop='genre'>Thriller</span><span itemprop='genre'>Drame</span>"
    soup = BeautifulSoup(html, "html.parser")
    genres = get_genres_from_soup(soup)
    assert genres == ["Thriller", "Drame"]


def test_get_duration_from_soup():
    html = "<li class='pvi-productDetails-item'><meta itemprop='duration' content='PT7680S'>2 h 08 min</li>"
    soup = BeautifulSoup(html, "html.parser")
    duration = get_duration_from_soup(soup)
    assert duration == 2 * 60 + 8
