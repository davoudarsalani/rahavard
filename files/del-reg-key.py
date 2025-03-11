'''
Deletes a Windows registry key
and reboots if successful
'''


## Set-up guide:
##
## >> STEP 0: Install python
##    - Make sure python is installed
##
## >> STEP 1: Set up virtual environment
##    mkdir C:\del-reg-key
##    cd C:\del-reg-key
##    python -m venv venv
##    venv\Scripts\activate.bat
##    pip install winregistry
##
## >> STEP 2: Copy files
##    - Copy 'del-reg-key.bat' and 'del-reg-key.py'
##      into C:\del-reg-key directory
##
## >> STEP 3: Set up Task Scheduler
##    - Open Task Scheduler
##    - Click on Create Task
##    - Actions tab:
##      - Go to: New... > Browse
##      - Select C:\del-reg-key\del-reg-key.bat
##      - Press OK
##    - General tab:
##      - Set Name
##      - NOTE: Check 'Run with highest privileges'
##    - Triggers tab:
##      - Set as desired
##    - Press OK

## To execute manually (NOTE: Command Prompt needs to be run as administrator):
##   C:\del-reg-key\del-reg-key.bat

## Documentation for winregistry:
## https://pypi.org/project/winregistry/


from datetime import datetime
from getopt import getopt
from os import system as os_system
from pathlib import Path
from sys import argv
from time import sleep

import winreg
from winregistry import open_key  #WinRegistry


PARENT_DIR = Path(__file__).resolve().parent
LOG_FILE = f'{PARENT_DIR}/log'

REBOOT_DELAY = 5  ## seconds
MAX_LOOPS = 10


def display_help():
    print(r'''Help
>> NOTE: Use Double Quotes ONLY
-p|--path=  registry path, e.g. "SYSTEM\CurrentControlSet\Control\Terminal Server\RCM\GracePeriod"
-k|--key=   registry key, e.g. "L$RTMTIMEBOMB_1320153D-8DA3-4e8e-B27B-0D888223A588"''')
    exit()


def save_log(msg):
    ymdhms = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(msg)
    with open(LOG_FILE, 'a') as opened:
        opened.write(f'{ymdhms} {msg}\n')


def getopts():
    _REG_PATH = None
    _REG_KEY = None

    try:
        duos, duos_long = getopt(
            script_args,
            'hp:k:',
            ['help', 'path=', 'key=']
        )
        for opt, arg in duos:
            if   opt in ('-h', '--help'): display_help()
            elif opt in ('-p', '--path'): _REG_PATH = arg
            elif opt in ('-k', '--key'):  _REG_KEY  = arg
    except Exception as exc:
        save_log(f'Error: {exc!r}')
        display_help()

    return _REG_PATH, _REG_KEY


if __name__ == '__main__':
    loop = 0
    successful = False
    script_args = argv[1:]

    if not script_args:
        display_help()

    REG_PATH, REG_KEY = getopts()

    if not REG_PATH or not REG_KEY:
        display_help()

    save_log('Starting...')
    save_log(f'Path: {REG_PATH}')
    save_log(f'Key: {REG_KEY}')

    while not successful and loop < MAX_LOOPS:
        loop += 1
        save_log(f'  Loop #{loop}')

        try:
            with open_key(
                winreg.HKEY_LOCAL_MACHINE,
                sub_key=REG_PATH,
            ) as client:
                client.delete_key(REG_KEY)

            save_log('    Success')
            successful = True
        except FileNotFoundError as exc:
            save_log(f'    Failed: {exc!r}')
            break
        except Exception as exc:
            save_log(f'    Failed: {exc!r}')

        sleep(1)

    if successful:
        save_log(f'Rebooting in {REBOOT_DELAY} seconds...')
        save_log('------------------')
        os_system(f'shutdown -t {REBOOT_DELAY} -r -f')
    else:
        save_log(f'Failed after {loop} tries.')
        save_log('------------------')
