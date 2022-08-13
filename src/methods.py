from datetime import datetime
from .models import User, session, Category, DEFAULT_CATEGORY_NAME


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
        for h in self.current_user.history[::-1][:10]:
            print(h.value, '\t', h.category_name, '\t', h.date)


    # can receive a category_name in the kargs
    def add_spend(self, value, **kargs):
        try:
            if 'from' in kargs and value > 0:
                self.spend(value, category_name = kargs['from'])

            self.current_user.add_or_spend(value, datetime.now(), **kargs)

            self.session.commit()
            self.get_total()
        except Exception as e:
            self.session.rollback()
            print('\nError')
            print(str(e))
            


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
        new_category = Category(category_name = category_name,
                                username = self.current_user.username)
        self.session.add(new_category)
        self.session.commit()


    def remove_category(self, category_name):

        if category_name == DEFAULT_CATEGORY_NAME:
            raise Exception('The default category is not allowed to be removed')

        category_to_remove = self.session.query(Category).get((category_name, self.current_user.username))
        default_cat = self.session.query(Category).get((DEFAULT_CATEGORY_NAME, self.current_user.username))
        print(f'--> {category_to_remove.total} moved to {DEFAULT_CATEGORY_NAME}')

        default_cat.total += category_to_remove.total
        
        self.session.delete(category_to_remove)
        self.session.commit()
        print(f'--> {category_name} removed')


    def analyse(self):
        pass
