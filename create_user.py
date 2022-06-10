from src.models import User, session
import sys


try:
    username = sys.argv[1]
except:
    print('username missing')
    exit(1)


res = None
try:
    res = sys.argv[2]
except:
    pass

if res != '--confirm':
    res = input(f"Are you sure you want to add {username}?(type 'Y' to confirm) ")
    if res != 'Y':
        exit()


try:
    total = sys.argv[3]
except:
    total = input(f"How much money does {username} have?(0) ").strip()
    if not total:
        total = 0


try:
    total = float(total)
except:
    print('Invlaid Number')
    exit()


try:
    user = User(username=username, total=total)
    session.add(user)
    session.commit()

    print(username, 'successfully created with total of', total)

except Exception as e:
    print('The user could not be added')
    print('maybe the user already exists')
    print(str(e))
finally:
    session.rollback()