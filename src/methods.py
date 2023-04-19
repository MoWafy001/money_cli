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
            if 'from' in kargs and value > 0:
                kargs['except_from_budget'] = True
                exceptFromBudget = True
                self.spend(
                    value, category_name=kargs['from'], desc="transfer", except_from_budget=True)

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
        max_days = datetime.now().max.day

        if 'set_daily' in kargs:
            self.current_user.daily_budget = float(kargs['set_daily'])
            self.session.commit()
            print('Daily budget set to', self.current_user.daily_budget)

        elif 'set_monthly' in kargs:
            monthly_budget = float(kargs['set_monthly'])
            self.current_user.daily_budget = monthly_budget / max_days
            self.session.commit()
            print('Daily budget set to', self.current_user.daily_budget)

        elif 'set_daily_offset' in kargs:
            offset = float(kargs['set_daily_offset'])
            if offset > 0:
                raise Exception('Offset cannot be greater than 0')

            self.current_user.daily_budget_offset = offset
            self.session.commit()
            print('Daily budget offset set to',
                  self.current_user.daily_budget_offset)

        elif 'set_monthly_offset' in kargs:
            offset = float(kargs['set_monthly_offset'])

            self.current_user.daily_budget_offset = offset / max_days
            self.session.commit()
            print('Daily budget offset set to',
                  self.current_user.daily_budget_offset)

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

        elif 'account_for_added_money' in kargs:
            inp = kargs['account_for_added_money'].lower()
            if inp not in ('true', 'false'):
                raise Exception("Invalid Input: this function only takes (true) or (false)")
            inp = True if inp == 'true' else False
            self.current_user.budget_account_for_added_money = inp
            print("budget_account_for_added_money is set to", inp)
            self.session.commit()

        else:
            self.show_budget(**kargs)

    def show_budget(self, **kargs):
        if self.current_user.daily_budget is None:
            print('No daily budget set')
            return

        max_days = datetime.now().max.day

        daily_budget = self.current_user.daily_budget
        print('Daily budget:', round(daily_budget, 2))

        daily_budget_offset = self.current_user.daily_budget_offset or 0
        if daily_budget_offset is not None and daily_budget_offset != 0:
            print('Daily budget offset:', round(daily_budget_offset, 2))
            print("Montly budget offset:", round(daily_budget_offset * max_days, 2))
            print('Daily budget after offset:', round(daily_budget + daily_budget_offset, 2))

        daily_budget += daily_budget_offset

        monthly_budget = daily_budget * max_days
        print('Monthly budget:', round(monthly_budget, 2))

        totalSpend, totalAdded = self.get_budget_total_month_spending(
            printHistory=kargs['history'] == 'true' if 'history' in kargs else False
        )
        totalAddedCopy = totalAdded if self.current_user.budget_account_for_added_money else 0

        print("Total added:", totalAdded)
        print("Total spent:", totalSpend)

        final_monthly_budget = monthly_budget + totalAddedCopy
        print("Final monthly budget:", round(final_monthly_budget, 2))

        remaining_for_this_month = final_monthly_budget + totalSpend

        remaining_for_this_month = round(remaining_for_this_month, 2)

        daily_step = final_monthly_budget/max_days
        print("Daily step:", round(daily_step, 2))

        allowed_to_spend_today = daily_step * datetime.now().day + totalSpend

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

        totalSpend = sum([h.value for h in history if h.value < 0])
        totalAdded = sum([h.value for h in history if h.value > 0])

        return totalSpend, totalAdded

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
