# Activity-Monitor

## How to set-up

Clone the repository and in the parent directory, run the following commands.

### Install python virtual environment

Windows\
`pip install virtualenv`

### Create new environment called 'venv'

`virtualenv venv`


### Activate the venv

Windows\
`venv\Scripts\activate`
    
On Windows, it may be required to set the execution policy for the user.
You can do this by issuing the following PowerShell command:
PS C:> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser


### Install modules

`pip install -r requirements.txt`

### Run Activity Monitor
Ensure that the requirements are installed, and the virtual environment is activated. Then run the following\

Windows\
`python app.py`


## Compiling fow Windows
To compile Activity Monitor to an executable (.exe), run either of the following commands in the root directory of the project using [pyinstaller](https://www.pyinstaller.org/)

For .exe with console use `pyinstaller -F -c --icon=favicon.ico ./app.py`

For .exe without console use `pyinstaller -F -w --icon=favicon.ico ./app.py`

## Browser Extension

Install the [extension](https://github.com/thisuraseniya/Activity-Monitor-Extension) to collect URL 




