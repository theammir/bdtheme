import requests as rq
import os
import shutil
import uuid
from typing import Tuple, List, Callable
from bs4 import BeautifulSoup as BS

USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"}


class Theme:
    """
        :param img_url: str - theme screenshot url
        :param url: str - theme page url
        :param likes: int - likes count
        :param views: int - views count
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.img_url = kwargs.get("img_url")
        self.url = kwargs.get("url")
        self.likes = kwargs.get("likes")
        self.views = kwargs.get("views")

    def __str__(self):
        return self.name


class Paginator:
    VSTHEMES_PAGESIZE = 25

    def __init__(self, retrieve_new: Callable, *, pagesize: int):
        self.retrieve_new = retrieve_new
        self.pagesize = pagesize

        self.page = 0
        self.vspage = 0
        self._coll = self.retrieve_new(self.page)

        self.pages_cache = {}

    def next_page(self):
        if (cache := self.pages_cache.get(self.page + 1)):
            self.page += 1
            return cache

        result = []
        remaining = self.pagesize

        while not remaining == 0:
            self.vspage += 1
            self._coll = self.retrieve_new(self.vspage)
            if not self._coll:
                if result:
                    self.page += 1
                return result

            page_part = self._coll[:remaining]
            result += page_part
            remaining -= len(page_part)
            self._coll = self._coll[remaining:]

        if result:
            self.pages_cache[self.page + 1] = result
            self.page += 1
        return result

    def previous_page(self):
        if (cache := self.pages_cache.get(self.page - 1)):
            self.page -= 1
            return cache


def get_themes_dir():
    themedir_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", ".themedir"))
    if os.path.exists(themedir_path):
        with open(themedir_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    else:
        return os.path.normpath(os.path.join(
            os.path.dirname(__file__), "..", "themes"))


def set_theme(file: str):
    shutil.copyfile(file, os.path.join(get_themes_dir(), "__current.css"))


def parse_vsthemes_list(page: int = 1) -> List[Theme]:
    base_url = 'https://vsthemes.org/en/skins/discord/page/{page}/'

    resp = rq.get(base_url.format(page=page), headers=USER_AGENT)
    bs = BS(resp.text, 'lxml')

    theme_elements = bs.find_all("div", {"class": "infiniteBlock"})

    result = []
    for el in theme_elements:
        name = el.find_all("a")[1].text
        img_url = "https://vsthemes.org" + el.find("img").get("src")
        theme_url = el.find("a").get("href")
        views, _, likes = el.find("ul", {"class": "iOptions"}).find_all("span")
        views = int(views.text.replace(" ", ""))
        likes = int(likes.text.replace(" ", ""))

        result.append(Theme(name, img_url=img_url,
                      url=theme_url, likes=likes, views=views))

    return result


def parse_vsthemes_css(url: str) -> Tuple[str, str]:
    resp = rq.get(url, headers=USER_AGENT)
    bs = BS(resp.text, 'lxml')

    css_text = bs.find("code", {"class": "php"})

    return css_text.text


def save_theme(theme: Theme) -> None:
    themes_dir = get_themes_dir()
    theme_css = parse_vsthemes_css(theme.url)
    with open(os.path.join(themes_dir, f"{uuid.uuid4()}.css"), "a+", encoding="utf-8") as f:
        f.write(f"/* <{theme.name}> */\n")
        f.write("\n".join(list(filter(lambda i: not i.lower(
        ).startswith("//meta"), theme_css.split("\n")))))
