from datetime import datetime
from .models import User, session, Category, History, DEFAULT_CATEGORY_NAME


class Methods:
    def __init__(self, current_user, session):
        self.current_user = current_user
        self.session = session

    def get_total(self):
        print('Total:', self.current_user.total)
        print('-' * 16)
        for c in self.current_user.categories:
            print(c.category_name, ':', c.total)

    def get_history(self, **kargs):

        if 'category' in kargs:
            category_name = kargs['category']
            history = self.session.query(History).filter_by(
                username=self.current_user.username,
                category_name=category_name).all()
            history = sorted(history, key=lambda x: x.date, reverse=True)
        else:
            history = self.current_user.history

        if 'n' in kargs:
            history = history[::-1][:int(kargs['n'])]

        for h in history:
            print("{:<8} {:<10} {:<10} {:<10}".format(h.value, h.category_name,
                                                      str(h.date), h.desc
                                                      or ''))

    # can receive a category_name in the kargs
    def add_spend(self, value, **kargs):
        try:
            if 'from' in kargs and value > 0:
                self.spend(value, category_name=kargs['from'])

            self.current_user.add_or_spend(value, datetime.now(), **kargs)

            self.session.commit()
            self.get_total()
        except Exception as e:
            self.session.rollback()
            print('\nError')
            print(str(e))
            exit(1)

    # can receive a category_name in the kargs
    def add(self, value, **kargs):
        value = float(value)
        self.add_spend(value, **kargs)

    # can receive a category_name in the kargs
    def spend(self, value, **kargs):
        value = float(value)
        self.add_spend(-value, **kargs)

    # can receive a value in the kargs as a flag
    def create_category(self, category_name, **kargs):
        new_category = Category(category_name=category_name,
                                username=self.current_user.username)
        self.session.add(new_category)
        self.session.commit()

    def remove_category(self, category_name):

        if category_name == DEFAULT_CATEGORY_NAME:
            raise Exception(
                'The default category is not allowed to be removed')

        category_to_remove = self.session.query(Category).get(
            (category_name, self.current_user.username))
        default_cat = self.session.query(Category).get(
            (DEFAULT_CATEGORY_NAME, self.current_user.username))
        print(
            f'--> {category_to_remove.total} moved to {DEFAULT_CATEGORY_NAME}')

        default_cat.total += category_to_remove.total

        self.session.delete(category_to_remove)
        self.session.commit()
        print(f'--> {category_name} removed')

    def budget(self, **kargs):
        if 'set_daily' in kargs:
            self.current_user.daily_budget = float(kargs['set_daily'])
            self.session.commit()
            print('Daily budget set to', self.current_user.daily_budget)

        elif 'add_exception' in kargs:
            category = self.session.query(Category).get(
                (kargs['add_exception'], self.current_user.username))
            category.except_from_budget = True
            self.session.commit()
            print('Added exception', kargs['add_exception'])

        elif 'remove_exception' in kargs:
            category = self.session.query(Category).get(
                (kargs['remove_exception'], self.current_user.username))
            category.except_from_budget = False
            self.session.commit()
            print('Removed exception', kargs['remove_exception'])

        else:
            self.show_budget()

    def show_budget(self):
        if self.current_user.daily_budget is None:
            print('No daily budget set')
            return

        print('Daily budget:', self.current_user.daily_budget)
        monthly_budget = self.current_user.daily_budget * 30
        print('Monthly budget:', monthly_budget)

        remaining_for_this_month = monthly_budget - \
            self.get_budget_total_month_spending()
        remaining_for_this_month = round(
            remaining_for_this_month, 2)

        minimum_allowed_daily_spending = (remaining_for_this_month /
                                          (30 - datetime.now().day)) if datetime.now().day < 30 else 0
        minimum_allowed_daily_spending = round(
            minimum_allowed_daily_spending, 2)

        # turn red if negative
        if remaining_for_this_month <= 0:
            print('\033[91m', end='')
        print('Remaining money for this month:', remaining_for_this_month)
        print('\033[0m', end='')

        # turn red if negative
        if minimum_allowed_daily_spending <= 0:
            print('\033[91m', end='')
        print('Minimum allowed daily spending:',
              minimum_allowed_daily_spending)
        print('\033[0m', end='')

    def get_budget_total_month_spending(self):
        history = list(
            filter(
                lambda h: h.date.month == datetime.now().month and h.value < 0 and not self.session.query(
                    Category).get((h.category_name, self.current_user.username)).except_from_budget,
                self.current_user.history))
        total = abs(sum([h.value for h in history]))

        return total

    def analyse(self):
        pass
