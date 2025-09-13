from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MsgPayload(BaseModel):
    msg_id: Optional[int]
    msg_name: str


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)


class Login(Base):
    __tablename__ = "logins"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
