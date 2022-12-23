from .config import CURRENT_USER
from .methods import Methods, User, session

current_user = session.query(User).get(CURRENT_USER)

if current_user is None:
    print(f'User ({CURRENT_USER}) was not found\n')
    print(f'run the following script to create {CURRENT_USER}\n')
    print("=" * 40)
    print(f'= python create_user.py {CURRENT_USER}')
    print("=" * 40)
    exit(1)

methods = Methods(current_user, session)

commands = {
    'total': methods.get_total,
    'history': methods.get_history,
    'add': methods.add,
    'spend': methods.spend,
    'create-category': methods.create_category,
    'remove-category': methods.remove_category,
    'budget': methods.budget,
    # 'analyse': methods.analyse,
}


def handel_command(command):
    flags = {
        (
            f[2:].replace('-', '_')
            if f.startswith('--')
            else f[1:].replace('-', '_')
        ): command[i + 1]
        for i, f in enumerate(command[:-1]) if f.startswith('-')
    }

    action = command[0] if len(command) > 0 else None
    value = command[1] if len(command) > 1 else None

    if value is not None and value[:1] == '-':  # if flag
        value = None

    try:
        if action is None:
            methods.get_total()
            print("-" * 16)
            methods.show_budget()
            print("-" * 16)
            methods.get_history(n=10)
        elif value is None:
            commands[action](**flags)
        else:
            commands[action](value, **flags)
    except Exception as e:
        print(str(e))
        print('Invalid command')
        # display_help()
