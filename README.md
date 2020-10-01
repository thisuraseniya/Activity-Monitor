# Activity-Monitor

Run app.py to start Activity Monitor in development

To compile Activity Monitor to an executable (.exe), run either of the following commands in the root directory of the project using [pyinstaller](https://www.pyinstaller.org/)

For .exe with console use `pyinstaller -F -c --icon=favicon.ico ./app.py`

For .exe without console use `pyinstaller -F -w --icon=favicon.ico ./app.py`

Install the [extension](https://github.com/thisuraseniya/Activity-Monitor-Extension) to collect URL data

Activity Monitor is built with ❤ using Flask, SQLite, jQuery, HTML and Bootstrap.
