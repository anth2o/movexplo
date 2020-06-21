from bs4 import BeautifulSoup

from scrapper import get_link_from_soup, get_image_from_soup, get_director_from_soup, get_date_from_soup, get_genres_from_soup, get_duration_from_soup


def test_get_item_link():
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


def test_get_genre():
    html = "<span itemprop='genre'>Thriller</span><span itemprop='genre'>Drame</span>"
    soup = BeautifulSoup(html, "html.parser")
    genres = get_genres_from_soup(soup)
    assert genres == ["Thriller", "Drame"]


def test_get_duration():
    html = "<li class='pvi-productDetails-item'><meta itemprop='duration' content='PT7680S'>2 h 08 min</li>"
    soup = BeautifulSoup(html, "html.parser")
    duration = get_duration_from_soup(soup)
    assert duration == 2 * 60 + 8
