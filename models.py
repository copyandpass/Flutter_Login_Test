from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MsgPayload(BaseModel):
    msg_id: Optional[int]
    msg_name: str

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, nullable=True)

class Login(Base):
    __tablename__ = "logins"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    login_time = Column(TIMESTAMP, nullable=True)
    ip_address = Column(String(45), nullable=True)
    is_success = Column(Boolean, nullable=False)