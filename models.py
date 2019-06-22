##from sqlalchemy import Column, Integer, String
##from sqlalchemy.ext.declarative import declarative_base
##
##Base = declarative_base()
##
##class SomeClass(Base):
##    __tablename__ = 'some_table'
##    id = Column(Integer, primary_key=True)
##    name =  Column(String(50))

from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)

class Userfile(Base):
    __tablename__ = 'userfiles'
    id = Column(Integer, primary_key=True)
    filename = Column(String(50), unique=True)
    fileid = Column(String(10), unique=True)
