from datetime import datetime
from .models import User, session, Category, History, DEFAULT_CATEGORY_NAME


class Methods:
    def __init__(self, current_user, session):
        self.current_user = current_user
        self.session = session

    def get_total(self, **kargs):
        show_hidden = 'show_hidden' in kargs and kargs['show_hidden'] == 'true'

        print('Total:', self.current_user.total)
        print('-' * 16)
        for c in self.current_user.categories:
            print(f'{c.category_name}: ', end='')

            if c.hide_value:
                print('\033[90m', end='')
                if show_hidden:
                    print(c.total, end=' ')
                else:
                    print('--hidden--', end=' ')
                print('\033[0m', end='')
            else:
                print(c.total, end=' ')

            print(f'{"[L]" if not c.allowed_to_spend else ""}')

    def get_history(self, **kargs):

        if 'category' in kargs:
            category_name = kargs['category']
            history = self.session.query(History).filter_by(
                username=self.current_user.username,
                category_name=category_name).all()
            history = sorted(history, key=lambda x: x.date, reverse=True)
        else:
            history = sorted(self.current_user.history, reverse=True)

        if 'n' in kargs:
            history = history[:int(kargs['n'])]

        for h in history:
            print("{:<8} {:<20} {:<10} {:<10}".format(h.value, h.category_name + ('!' if h.except_from_budget else ""),
                                                      str(h.date), h.desc
                                                      or ''))

    # can receive a category_name in the kargs
    def add_spend(self, value, **kargs):
        try:
            exceptFromBudget = kargs[
                'except_from_budget'] if 'except_from_budget' in kargs else False
            
            if 'from' in kargs and value > 0:
                exceptFromBudget = True
                self.spend(
                    value, category_name=kargs['from'], desc="transfer", except_from_budget=True)

            self.current_user.add_or_spend(value, datetime.now(), except_from_budget=exceptFromBudget, **kargs)

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

        if value <= 0:
            raise Exception('Value must be greater than 0')

        self.add_spend(value, **kargs)

    # can receive a category_name in the kargs
    def spend(self, value, **kargs):
        value = float(value)

        if value <= 0:
            raise Exception('Value must be greater than 0')

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
            self.show_budget(**kargs)

    def show_budget(self, **kargs):
        if self.current_user.daily_budget is None:
            print('No daily budget set')
            return

        max_days = datetime.now().max.day

        print('Daily budget:', self.current_user.daily_budget)

        monthly_budget = self.current_user.daily_budget * max_days
        print('Monthly budget:', monthly_budget)

        budget_total_month_spending = - self.get_budget_total_month_spending(
            printHistory=kargs['history'] == 'true' if 'history' in kargs else False
        )

        remaining_for_this_month = monthly_budget - budget_total_month_spending

        remaining_for_this_month = round(remaining_for_this_month, 2)

        allowed_to_spend_today = (self.current_user.daily_budget * datetime.now().day -
                                  budget_total_month_spending)
        allowed_to_spend_today = round(
            allowed_to_spend_today, 2)

        # turn red if negative
        if remaining_for_this_month <= 0:
            print('\033[91m', end='')
        print('Remaining money for this month:', remaining_for_this_month)
        print('\033[0m', end='')

        # turn red if negative
        if allowed_to_spend_today <= 0:
            print('\033[91m', end='')
        print('Allowed to spend today:',
              allowed_to_spend_today)
        print('\033[0m', end='')

        print("Exceptions from budget:")
        for c in self.current_user.categories:
            if c.except_from_budget:
                print("*", c.category_name)

    def get_budget_total_month_spending(self, printHistory=False):

        def f(h):
            category = self.session.query(Category).get(
                (h.category_name, self.current_user.username))

            if category is None:
                return False

            if h.date.month != datetime.now().month:
                return False

            if h.except_from_budget:
                return False

            return True

        history = list(filter(f, self.current_user.history))

        if printHistory:
            print("{:<10} {:<20} {:<20} {:<20}".format(
                'Value', 'Category', 'Description', 'Date'))
            for h in sorted(history, key=lambda h: h.date, reverse=True):
                print("{:<10} {:<20} {:<20} {:<20}".format(
                    h.value, h.category_name, h.desc or "", str(h.date)))

        total = sum([h.value for h in history])

        return total

    def lock(self, category_name):
        category = self.session.query(Category).get(
            (category_name, self.current_user.username))
        category.allowed_to_spend = False
        self.session.commit()
        print(f'--> {category_name} locked')

    def unlock(self, category_name):
        category = self.session.query(Category).get(
            (category_name, self.current_user.username))
        category.allowed_to_spend = True
        self.session.commit()
        print(f'--> {category_name} unlocked')

    def hide(self, category_name):
        category = self.session.query(Category).get(
            (category_name, self.current_user.username))
        category.hide_value = True
        self.session.commit()
        print(f'--> {category_name} hidden')

    def unhide(self, category_name):
        category = self.session.query(Category).get(
            (category_name, self.current_user.username))
        category.hide_value = False
        self.session.commit()
        print(f'--> {category_name} unhidden')

    def analyse(self):
        pass
