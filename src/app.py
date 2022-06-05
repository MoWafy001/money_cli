from .models import *
from .config import CURRENT_USER
from datetime import datetime


current_user = session.query(User).get(CURRENT_USER)


def get_total():
    print('Total:', current_user.total)


def set_total(new_total):
    current_user.total = int(new_total)
    session.commit()
    get_total()


def add(value):
    value = int(value)
    current_user.add_or_spend(value, datetime.now())
    session.commit()
    print(value, 'added')
    get_total()


def spend(value):
    value = int(value)
    current_user.add_or_spend(-value, datetime.now())
    session.commit()
    print(value, 'spent')
    get_total()


commands = {
    'total': get_total,
    'set-total': set_total,
    'add': add,
    'spend': spend
}


def handel_command(command):
    try:
        if len(command) == 0:
            get_total()
        elif len(command) > 1:
            commands[command[0]](command[1])
        else:
            commands[command[0]]()
    except Exception as e:
        print(str(e))
        print('Invalid command')
        #display_help()