![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)
![PyPi version](https://img.shields.io/pypi/v/bdtheme)
![Topmost language](https://img.shields.io/github/languages/top/TheAmmiR/bdtheme)
![Total lines](https://img.shields.io/tokei/lines/github/TheAmmiR/bdtheme)



## BeautifulDiscord theme manager
Console script for downloading & managing Discord .css themes via [BeautifulDiscord](https://github.com/leovoel/BeautifulDiscord).
## Setup
Simply run
```python
# Linux/MacOS
pip3 install bdtheme
# Windows
pip install bdtheme
```
## Usage
You have access to `bdtheme` command now in your `bash`/`cmd`.
* `bdtheme init [path/to/folder]` - initialize BeautifulDiscord and set the `directory` as themes folder. No worries, you probably won't need the files, so you can omit all the arguments. **Requires Discord to be launched**
* `bdtheme download` - themes browser. Navigate with WASD/arrows, "q" to exit, choose whatever you like and hit enter.
* `bdtheme set [filename]` - if no `filename` specified, opens browser you're familliar with so you can apply chosen theme. Changes should be visible after no time, otherwise it could happen something's wrong.
* `bdtheme revert` - cleans Discord files up a little, so there's no more BeautifulDiscord and .css hot-reload.
