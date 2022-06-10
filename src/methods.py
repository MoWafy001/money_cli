from datetime import datetime


class Methods:
    def __init__(self, current_user, session):
        self.current_user = current_user
        self.session = session


    def get_total(self):
        print('Total:', self.current_user.total)


    def set_total(self, new_total):
        self.current_user.total = int(new_total)
        self.session.commit()
        self.get_total()


    def add_spend(self, value):
        self.current_user.add_or_spend(value, datetime.now())
        self.session.commit()
        print(value, 'added')
        self.get_total()


    def add(self, value):
        value = int(value)
        self.add_spend(value)


    def spend(self, value):
        value = int(value)
        self.add_spend(-value)