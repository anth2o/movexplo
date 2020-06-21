import requests
from bs4 import BeautifulSoup

from movexplo.constants import TOFIND, URL
from movexplo.utils import (duration_to_int, get_logger, remove_special_characters)

logger = get_logger("scrapper")


def get_soup_from_url(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    return soup


def get_link_from_file(file_info):
    url = URL.format(remove_special_characters(file_info["name"].replace(" ", "%20").lower()))
    logger.info("Searching {}".format(url))
    soup = get_soup_from_url(url)
    try:
        return get_link_from_soup(soup)
    except (IndexError, AttributeError) as e:
        logger.warning("Search failed for {} at url {}".format(file_info["name"], url))
        return TOFIND


def get_link_from_soup(soup):
    item = soup.find("div", "ProductListItem__TextContainer-sc-1ci68b-8 kKuZab")
    links = item.find_all("a", href=True)
    for link in links:
        if link["href"] is not None:
            return link["href"]
    return None


def get_image_from_soup(soup):
    item = soup.find("img", "pvi-hero-poster")
    return item["src"]


def get_director_from_soup(soup):
    item = soup.find("span", itemprop="name")
    return item.text


def get_date_from_soup(soup):
    item = soup.find("time")
    return item["datetime"]


def get_genres_from_soup(soup):
    items = soup.find_all("span", itemprop="genre")
    return [item.text for item in items]


def get_duration_from_soup(soup):
    items = soup.find_all("li", "pvi-productDetails-item")
    for item in items:
        if item.find("meta", itemprop="duration"):
            return duration_to_int(item.text.replace("\n", "").replace("\t", ""))
    raise IndexError


FIELD_TO_METHOD = {
    "image": get_image_from_soup,
    "director": get_director_from_soup,
    "date": get_date_from_soup,
    "genres": get_genres_from_soup,
    "duration": get_duration_from_soup
}
