from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from .config import DATABASE_URI 


# initialize
engine = create_engine(DATABASE_URI, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# models
class History(Base):
  __tablename__ = 'history'

  date = Column(DateTime, primary_key=True)
  value = Column(Float, nullable=False)

  users = relationship('User', secondary='user_history', back_populates='history')


class User(Base):
  __tablename__ = 'users'

  username = Column(String, primary_key=True)
  total = Column(Integer, default=0, nullable=False)

  history = relationship('History', secondary='user_history', back_populates='users')


  def add_or_spend(self, value, when):
    old_total = self.total

    try:
      h = History(date=when, value=value)
      self.history.append(h)

      if self.total is None:
        self.total = 0
        
      self.total += value
    except Exception as e:
      self.total = old_total
      raise e


class UserHistory(Base):
  __tablename__ = 'user_history'

  username = Column(String, ForeignKey('users.username'), primary_key=True)
  date = Column(DateTime, ForeignKey('history.date'), primary_key=True)


Base.metadata.create_all(engine)