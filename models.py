from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(55), unique=True, index=True)
    username = Column(String(55), unique=True, index=True)
    firstName = Column(String(55))
    hashed_password = Column(String(55))
    isActive = Column(Boolean, default=True)
    todos = relationship("Todos", back_populates="owner")


class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(55))
    description = Column(String(55))
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("Users", back_populates="todos")
