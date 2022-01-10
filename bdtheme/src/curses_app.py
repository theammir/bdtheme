import curses
import shutil
import re
import os
from .themes import parse_vsthemes_list, save_theme, get_themes_dir, set_theme, Paginator
from curses import wrapper


def init_app(stdscr, retrieve_new, on_choice):
    curses.init_pair(1, curses.COLOR_RED,
                     curses.COLOR_WHITE)  # cursor position
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.curs_set(False)
    wx, wy = shutil.get_terminal_size()
    cursor = [5, 5]

    paginator = Paginator(retrieve_new, pagesize=wy - 5 - 5)
    theme_list = paginator.next_page()

    mainloop = True
    while mainloop:
        stdscr.clear()
        for y in range(wy):
            for x in range(wx):
                if (x == 0 or y == 0):
                    stdscr.addch(y, x, "#")

        stdscr.addstr(3, 3, 'Press "q" to exit.')
        stdscr.addstr(wy - 2, 3, '"WASD" or arrows to navigate.')
        if not os.path.isdir(get_themes_dir()):
            stdscr.addstr(
                wy - 1, 10, 'Execute "bdtheme init" first!', curses.color_pair(2))

        for y in range(min(wy - 5 - 5, len(theme_list))):
            try:
                stdscr.addstr(y+5, 5, str((y + 1) + (paginator.pagesize * (paginator.page - 1))) + ". "
                              + str(theme_list[y]))
            except IndexError:
                break

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
        elif key in [curses.KEY_RIGHT, ord("d"), ord("D"), ord("в"), ord("В")]:
            old_list = theme_list.copy()
            theme_list = paginator.next_page()
            if not theme_list:
                theme_list = old_list
        elif key in [curses.KEY_LEFT, ord("a"), ord("A"), ord("ф"), ord("Ф")]:
            old_list = theme_list.copy()
            theme_list = paginator.previous_page()
            if not theme_list:
                theme_list = old_list


def download_app():
    def on_choice(theme):
        print("Downloading " + theme.name)
        save_theme(theme)
    wrapper(init_app, parse_vsthemes_list, on_choice)


def browse_app():
    name_re = r'/\* <(.+)> \*/'

    files = []
    try:
        files = os.listdir(get_themes_dir())
    except FileNotFoundError:
        pass

    themes_list = []
    themes_dict = {}
    for file in files:
        filename = os.path.join(get_themes_dir(), file)
        if file == "__current.css":
            continue
        with open(filename, 'r', encoding="utf-8") as f:
            theme_name = re.match(name_re, f.read().split('\n')[0]).group(1)
            themes_list.append(theme_name)
            themes_dict[theme_name] = filename

    def on_choice(theme_name):
        filename = themes_dict[theme_name]
        set_theme(filename)

    def retrieve_new(page):
        if page == 1:
            return themes_list
        else:
            return

    wrapper(init_app, retrieve_new, on_choice)
