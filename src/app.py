from .models import User, session
from .config import CURRENT_USER
from .methods import Methods


current_user = session.query(User).get(CURRENT_USER)
methods = Methods(current_user, session)


commands = {
    'total': methods.get_total,
    'history': methods.get_history,
    'set-total': methods.set_total,
    'add': methods.add,
    'spend': methods.spend,
    #'create-category': methods.create_category,
    #'remove-category': methods.remove_category,
    #'analyse': methods.analyse,
}


def handel_command(command):
    flags = {f[2:].replace('-','_'):command[i+1] for i, f in enumerate(command[:-1]) if f[:2] == '--'}
    action = command[0] if len(command) > 0 else None
    value = command[1] if len(command) > 1 else None

    if value is not None and value[:2] == '--': # if flag
        value = None

    try:
        if action is None:
            methods.get_total()
            methods.get_history()
        elif value is None:
            commands[action](**flags)
        else:
            commands[action](value, **flags)
    except Exception as e:
        print(str(e))
        print('Invalid command')
        #display_help()