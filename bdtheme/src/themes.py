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
        :param css: Callable - function to parse css
        :param source: str{bd, vs} - website the theme is from
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.img_url = kwargs.get("img_url")
        self.url = kwargs.get("url")
        self.likes = kwargs.get("likes")
        self.views = kwargs.get("views")
        self.css = kwargs.get("css")
        self.source = kwargs.get("source")

    def __str__(self):
        return self.name


class Paginator:
    def __init__(self, retrieve_new: Callable, *, pagesize: int, name: str):
        self.retrieve_new = retrieve_new
        self.pagesize = pagesize

        self.page = 0
        self.parsepage = 1
        self._coll = self.retrieve_new(self.parsepage)

        self.pages_cache = {}

        self.name = name or "paginator"

    def next_page(self):
        if (cache := self.pages_cache.get(self.page + 1)):
            self.page += 1
            return cache

        result = []
        remaining = self.pagesize

        while remaining != 0:
            page_part = self._coll[:remaining]
            result += page_part
            self._coll = self._coll[remaining:]
            remaining -= len(page_part)

            if not self._coll:
                self.parsepage += 1
                self._coll = self.retrieve_new(self.parsepage)
            if not self._coll:
                if result:
                    break
                return result

        if result:
            self.pages_cache[self.page + 1] = result
            self.page += 1
        return result

    def previous_page(self):
        if (cache := self.pages_cache.get(self.page - 1)):
            self.page -= 1
            return cache


def get_themedir():
    return os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", ".themedir"))


def get_themes_dir():
    themedir_path = get_themedir()
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
    if not resp.ok:
        return []

    bs = BS(resp.text, 'lxml')

    theme_elements = bs.find_all("div", {"class": "infiniteBlock"})

    result = []
    for el in theme_elements:
        try:
            name = el.find_all("div")[2].find("a").text
        except IndexError:
            continue
        img_url = "https://vsthemes.org" + el.find("img").get("src")
        theme_url = el.find("a").get("href")
        views, _, likes = el.find("ul", {"class": "iOptions"}).find_all("span")
        views = int(views.text.replace(" ", ""))
        likes = int(likes.text.replace(" ", ""))

        result.append(Theme(name, img_url=img_url,
                      url=theme_url, likes=likes, views=views, css=parse_vsthemes_css, source="vs"))

    return result


def parse_vsthemes_css(url: str) -> Tuple[str, str]:
    resp = rq.get(url, headers=USER_AGENT)
    bs = BS(resp.text, 'lxml')

    css_text = bs.find("code", {"class": "php"})

    return css_text.text


def parse_better_list(page: int, pages: int = 10):
    abbrevs = {"k": 1000, "m": 1000000}
    base_url = "https://betterdiscord.app/Addon/GetApprovedAddons?type=theme&filter=&page={page}&pages={pages}&sort=popular&sortDirection=&tags=[]"

    resp = rq.get(base_url.format(page=page,
                  pages=pages), headers=USER_AGENT)
    if not resp.ok:
        return []

    bs = BS(resp.text, 'lxml')

    card_list = bs.find_all("a", {"class": "card-wrap"})
    result = []
    for el in card_list:
        name = el.find("h3", {"class": "card-title"}).text
        img_url = "https://betterdiscord.app" + el.find("img").get("src")
        theme_url = "https://betterdiscord.app" + el.get("href")
        views = el.find("div", {"id": "addon-downloads"}
                        ).text.strip().replace(",", '')
        likes = el.find("div", {"id": "addon-likes"}
                        ).text.strip().replace(",", "")

        views = int(views) if views.isdigit() else int(float(views[:-1]) * abbrevs[views[-1].lower()])

        likes = int(likes) if likes.isdigit() else int(float(likes[:-1]) * abbrevs[likes[-1].lower()])


        result.append(Theme(name, img_url=img_url,
                      url=theme_url, likes=likes, views=views, css=parse_better_css, source="bd"))

    return result


def parse_better_css(url: str) -> None:
    theme_resp = rq.get(url, headers=USER_AGENT)
    bs = BS(theme_resp.text, 'lxml')

    download_link = "https://betterdiscord.app" + \
        bs.find("a", {"class": "btn-primary"}).get("href")
    download_resp = rq.get(
        download_link, headers=USER_AGENT, allow_redirects=True)

    return download_resp.text


def save_theme(theme: Theme) -> None:
    themes_dir = get_themes_dir()
    theme_css = theme.css(theme.url)
    # with open(os.path.join(os.path.dirname(__file__), "fix.css"), "r") as f:
    #     fix_css = f.read()
    with open(os.path.join(themes_dir, f"{uuid.uuid4()}.css"), "a+", encoding="utf-8") as f:
        f.write(f"/* <{theme.name}> @ {theme.source} */\n")
        # f.write(fix_css)
        f.write("\n".join(list(filter(lambda i: not i.lower(
        ).startswith("//meta"), theme_css.split("\n")))))
