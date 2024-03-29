import argparse
import os
from .curses_app import download_app, browse_app
from .themes import get_themes_dir, set_theme, get_themedir


def scmd_init(args):
    themes_dir = None
    themes_dir = args.dir or os.path.join(os.path.dirname(__file__), "..", "themes")

    themes_dir = os.path.normpath(themes_dir)
    with open(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", '.themedir')), 'w') as f:
        f.write(themes_dir)
    path = os.path.join(themes_dir, "__current.css")
    path = os.path.normcase(path)
    print(f"Initializing BeautifulDiscord at {path}")

    os.makedirs(themes_dir, exist_ok=True)

    os.system(f'beaudis --css "{path}"')


def scmd_browse(_):
    download_app()


def scmd_set(args):
    if args.file:
        print(f"Installing {args.file} theme.")
        set_theme(args.file)
    else:
        browse_app()


def scmd_clear(_):
    open(os.path.join(get_themes_dir(), "__current.css"), "w")


def scmd_revert(_):
    scmd_clear([])
    os.remove(get_themedir())
    os.system("beaudis --revert")


def scmd_cat(_):
    try:
        with open(os.path.join(get_themes_dir(), "__current.css"), 'r') as f:
            print(f.read())
    except FileNotFoundError:
        print('Execute "bdtheme init" first.')


def cmd_bdtheme():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    p_init = subparsers.add_parser(
        "init", help="Initialize BeautifulDiscord. Requires Discord running.")
    p_init.add_argument(
        "dir", metavar="themes_dir", nargs="?", default="", help="Custom themes location.")
    p_init.set_defaults(func=scmd_init)

    p_browse = subparsers.add_parser(
        "download", help="Download Discord themes. Requires internet connection.")
    p_browse.set_defaults(func=scmd_browse)

    p_set = subparsers.add_parser(
        "set", help="Choose a theme from installation folder.")
    p_set.add_argument("file", nargs="?", default=None,
                       help="Theme .css file location.")
    p_set.set_defaults(func=scmd_set)

    p_clear = subparsers.add_parser(
        "clear", help="Set Discord theme to default.")
    p_clear.set_defaults(func=scmd_clear)

    p_revert = subparsers.add_parser(
        "revert", help="Remove BeautifulDiscord .css hot-reload.")
    p_revert.set_defaults(func=scmd_revert)

    p_cat = subparsers.add_parser("cat", help="Print out current .css theme.")
    p_cat.set_defaults(func=scmd_cat)

    args = parser.parse_args()
    args.func(args)
