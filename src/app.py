from .models import User, session
from .config import CURRENT_USER
from .methods import Methods


current_user = session.query(User).get(CURRENT_USER)
methods = Methods(current_user, session)


commands = {
    'total': methods.get_total,
    'set-total': methods.set_total,
    'add': methods.add,
    'spend': methods.spend
}


def handel_command(command):
    try:
        if len(command) == 0:
            methods.get_total()
        elif len(command) > 1:
            commands[command[0]](command[1])
        else:
            commands[command[0]]()
    except Exception as e:
        print(str(e))
        print('Invalid command')
        #display_help()