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

  users = relationship('User', secondary='user_history', back_populates='history')


class Category(Base):
  __tablename__ = 'categories'

  category_name = Column(String, primary_key=True)
  username = Column(String, ForeignKey('users.username'), primary_key=True)
  total = Column(Float, default=0, nullable=False)


class User(Base):
  __tablename__ = 'users'

  username = Column(String, primary_key=True)
  total = Column(Float, default=0, nullable=False)

  history = relationship('History', secondary='user_history', back_populates='users')
  categories = relationship('Category', backref='user')


  def choose_category(self):
    print('Choose a category:')
    print('________________________\n')
    for i, c in enumerate(self.categories):
      print(f'{i}\t{c.category_name}\t{"[Default]" if c.category_name == DEFAULT_CATEGORY_NAME else ""}')
    
    print('________________________\n')
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
    category_name = kargs['category_name'] if 'category_name' in kargs else self.choose_category()

    if self.total is None:
      self.total = 0

    old_total = self.total

    try:
      h = History(date=when, value=value)
      self.history.append(h)
      self.total += value
    except Exception as e:
      self.total = old_total
      raise e

    # update category
    try:
      category = session.query(Category).get((category_name, self.username))
      category.total += value
    except:
      raise Exception(f'Could not add to category ({category_name}). It may not exist')


class UserHistory(Base):
  __tablename__ = 'user_history'

  username = Column(String, ForeignKey('users.username'), primary_key=True)
  date = Column(DateTime, ForeignKey('history.date'), primary_key=True)


# create all
Base.metadata.create_all(engine)


# events
@event.listens_for(Session, 'after_attach')
def receive_after_create(session, instance):
  if instance.__tablename__ != User.__tablename__:
    return
  
  default = Category(category_name=DEFAULT_CATEGORY_NAME, username=instance.username, total=instance.total)
  session.add(default)
  print(default.category_name, 'created')