import curses
import shutil
import re
import os
from .themes import parse_vsthemes_list, parse_better_list
from .themes import Paginator, save_theme, get_themes_dir, set_theme, get_themedir
from curses import wrapper


def init_app(stdscr, paginator_data, on_choice):
    curses.init_pair(1, curses.COLOR_RED,
                     curses.COLOR_WHITE)  # cursor position
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.curs_set(False)
    wx, wy = shutil.get_terminal_size()
    cursor = [5, 5]

    paginators = []
    theme_cache = []
    pag_index = 0
    if isinstance(paginator_data, dict):
        for k, v in paginator_data.items():
            p = Paginator(v, pagesize=wy - 5 - 5, name=k)
            paginators.append(p)
            theme_cache.append(p.next_page())
    elif isinstance(paginator_data, list):
        for i, v in enumerate(paginator_data):
            p = Paginator(v, pagesize=wy - 5 - 5, name=str(i + 1))
            paginators.append(p)
            theme_cache.append(p.next_page())
    else:
        p = Paginator(paginator_data, pagesize=wy - 5 - 5, name="main")
        paginators.append(p)
        theme_cache.append(p.next_page())

    mainloop = True
    while mainloop:
        paginator = paginators[pag_index]
        theme_list = theme_cache[pag_index]

        stdscr.clear()
        # Slashes
        for y in range(wy):
            for x in range(wx):
                if (x == 0 or y == 0):
                    stdscr.addch(y, x, "#")

        # Notes text
        stdscr.addstr(3, 3, 'Press "q" to exit.')
        stdscr.addstr(wy - 3, 3, '"WasD" or arrows to navigate.')
        stdscr.addstr(wy - 2, 3, 'Capital "AS" to switch tabs.')
        # No-init warning text
        if not os.path.exists(get_themedir()):
            stdscr.addstr(
                wy - 1, 10, 'Execute "bdtheme init" first!', curses.color_pair(2))
        # Themes text
        for y in range(min(wy - 5 - 5, len(theme_list))):
            try:
                stdscr.addstr(y+5, 5, str((y + 1) + (paginator.pagesize * (paginator.page - 1))) + ". "
                              + str(theme_list[y]))
            except IndexError:
                break

        # Current paginators
        tabs_text = []
        for p in paginators:
            tabs_text.append(f"[ {p.name} ]")
        overall_len = sum([len(i) for i in tabs_text])
        start_x = (wx // 2) - (overall_len // 2)
        offset = 0
        for tab in tabs_text:
            if tab == f"[ {paginator.name} ]":
                stdscr.addstr(2, start_x + offset, tab, curses.A_BOLD)
            else:
                stdscr.addstr(2, start_x + offset, tab)
            offset += len(tab)

        # Cursor position
        stdscr.addch(*cursor, stdscr.inch(*cursor), curses.color_pair(1))

        stdscr.refresh()

        key = stdscr.getch()
        if key in [ord("q"), ord("Q"), ord("й"), ord("Й")]:
            mainloop = False
        elif key in [curses.KEY_DOWN, ord("s"), ord("S"), ord("ы"), ord("Ы")]:
            if cursor[0] + 1 in range(5, min(wy, len(theme_list)) + 5):
                cursor[0] += 1
        elif key in [curses.KEY_UP, ord("w"), ord("W"), ord("ц"), ord("Ц")]:
            if cursor[0] - 1 in range(5, min(wy, len(theme_list)) + 5):
                cursor[0] -= 1
        elif key in [curses.KEY_ENTER, 10]:
            chosen_theme = theme_list[cursor[0] - 5]
            on_choice(chosen_theme)
            mainloop = False
        elif key in [curses.KEY_RIGHT, ord("d"), ord("в")]:
            next_page = paginator.next_page()
            if next_page:
                theme_cache[pag_index] = next_page
        elif key in [curses.KEY_LEFT, ord("a"), ord("ф")]:
            prev_page = paginator.previous_page()
            if prev_page:
                theme_cache[pag_index] = prev_page
        elif key in [ord("A"), ord("Ф")]:
            pag_index -= 1
            if pag_index < 0:
                pag_index = len(paginators) - 1
        elif key in [ord("D"), ord("В")]:
            pag_index += 1
            if pag_index > (len(paginators) - 1):
                pag_index = 0


def download_app():
    def on_choice(theme):
        print("Downloading " + theme.name)
        save_theme(theme)

    wrapper(init_app, {"betterdis": parse_better_list,
            "vsthemes": parse_vsthemes_list}, on_choice)


def browse_app():
    name_re = r'/\* <(.+)> @ (.+) \*/'

    files = []
    try:
        files = os.listdir(get_themes_dir())
    except FileNotFoundError:
        pass

    all_themes_list = []
    vs_themes_list = []
    bd_themes_list = []
    themes_dict = {}
    for file in files:
        filename = os.path.join(get_themes_dir(), file)
        if file == "__current.css":
            continue
        with open(filename, 'r', encoding="utf-8") as f:
            match = re.match(name_re, f.read().split('\n')[0])
            theme_name, theme_src = match.group(1), match.group(2)

            all_themes_list.append(theme_name)
            if theme_src == "vs":
                vs_themes_list.append(theme_name)
            elif theme_src == "bd":
                bd_themes_list.append(theme_name)
            themes_dict[theme_name] = filename

    def on_choice(theme_name):
        filename = themes_dict[theme_name]
        set_theme(filename)

    def retrieve_all(page):
        if page == 1:
            return all_themes_list
        else:
            return []

    def retrieve_bd(page):
        if page == 1:
            return bd_themes_list
        else:
            return []

    def retrieve_vs(page):
        if page == 1:
            return vs_themes_list
        else:
            return []

    wrapper(init_app, {"overall": retrieve_all,
            "betterdis": retrieve_bd, "vsthemes": retrieve_vs}, on_choice)
