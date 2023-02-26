from sqlalchemy import *
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from .config import DATABASE_URI, DEFAULT_CATEGORY_NAME

# initialize
engine = create_engine(DATABASE_URI)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# models
class History(Base):
    __tablename__ = 'history'

    date = Column(DateTime, primary_key=True)
    value = Column(Float, nullable=False)
    desc = Column(String, nullable=True)
    except_from_budget = Column(Boolean, default=False, nullable=False)

    username = Column(String, ForeignKey('users.username'), nullable=False)
    category_name = Column(String, nullable=False)

    user = relationship('User', back_populates='history')

    def __lt__(self, other):
        return self.date < other.date


class Category(Base):
    __tablename__ = 'categories'

    category_name = Column(String, primary_key=True)
    username = Column(String, ForeignKey('users.username'), primary_key=True)
    total = Column(Float, default=0, nullable=False)
    hide_value = Column(Boolean, default=False, nullable=False)

    except_from_budget = Column(Boolean, default=False, nullable=False)
    allowed_to_spend = Column(Boolean, default=True, nullable=False)


class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    total = Column(Float, default=0, nullable=False)
    daily_budget = Column(Float, nullable=True)
    daily_budget_offset = Column(Float, default=0, nullable=False)
    budget_account_for_added_money = Column(Boolean, default=False, nullable=False)

    history = relationship('History', back_populates='user')
    categories = relationship('Category', backref='user')

    def choose_category(self):
        print('Choose a category:')
        print(f'{"_"*40}\n')
        for i, c in enumerate(self.categories):
            print(
                f'  {i}\t{c.total}\t{c.category_name}\t{"[Default]" if c.category_name == DEFAULT_CATEGORY_NAME else ""}'
            )

        print(f'{"_"*40}\n')
        choice = input('Choice Index(keep blank for default): ')

        if choice.strip() == '':
            return DEFAULT_CATEGORY_NAME
        else:
            try:
                choice = int(choice)
                return self.categories[choice].category_name
            except:
                raise Exception('Invalid choice')

    def add_or_spend(self, value, when, **kargs):
        category_name = kargs[
            'category_name'] if 'category_name' in kargs else self.choose_category(
        )

        cat = session.query(Category).get((category_name, self.username))
        if cat is None:
            raise Exception(f'Category {category_name} does not exist')
        if value < 0 and not cat.allowed_to_spend:
            raise Exception(f'{category_name} is locked')

        desc = kargs['desc'] if 'desc' in kargs else None

        if self.total is None:
            self.total = 0

        old_total = self.total

        try:
            except_from_budget = kargs['except_from_budget'] if 'except_from_budget' in kargs else cat.except_from_budget
            h = History(date=when,
                        value=value,
                        category_name=category_name,
                        desc=desc,
                        except_from_budget=except_from_budget,)
            self.history.append(h)
            self.total += value
        except Exception as e:
            self.total = old_total
            raise e

        # update category
        try:
            category = session.query(Category).get(
                (category_name, self.username))
            category.total += value
        except:
            raise Exception(
                f'Could not add to category ({category_name}). It may not exist'
            )

        if category.total < 0:
            raise Exception(f'{category_name} only has {category.total-value}')

        print(
            abs(value), f'added to {category_name}'
            if value >= 0 else f'spent from {category_name}')


# create all
Base.metadata.create_all(engine)


# events
@event.listens_for(Session, 'after_attach')
def receive_after_create(session, instance):
    if instance.__tablename__ != User.__tablename__:
        return

    default = Category(category_name=DEFAULT_CATEGORY_NAME,
                       username=instance.username,
                       total=instance.total)
    session.add(default)
    print(default.category_name, 'created')
