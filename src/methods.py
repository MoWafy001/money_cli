from datetime import datetime


class Methods:
    def __init__(self, current_user, session):
        self.current_user = current_user
        self.session = session


    def get_total(self):
        print('Total:', self.current_user.total)
        print('-'*16)
        for c in self.current_user.categories:
            print(c.category_name, ':', c.total)
    

    def get_history(self):
        for h in self.current_user.history:
            print(h.value, '\t', h.category_name, '\t', h.date)


    def set_total(self, new_total):
        self.current_user.total = int(new_total)
        self.session.commit()
        self.get_total()


    # can receive a category_name in the kargs
    def add_spend(self, value, **kargs):
        self.current_user.add_or_spend(value, datetime.now(), **kargs)
        self.session.commit()
        print(abs(value), 'added' if value >= 0 else 'spent')
        self.get_total()


    # can receive a category_name in the kargs
    def add(self, value, **kargs):
        value = int(value)
        self.add_spend(value, **kargs)


    # can receive a category_name in the kargs
    def spend(self, value, **kargs):
        value = int(value)
        self.add_spend(-value, **kargs)

    
    # can receive a value in the kargs as a flag
    def create_category(self, category_name, **kargs):
        pass


    def remove_category(self, category_name):
        pass


    def analyse(self):
        pass