import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 프로젝트 루트 경로 추가

from utils import verify_password
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_verify_password():
    print("[DEBUG] test_verify_password 실행")
    raw = "password123"
    hashed = pwd_context.hash(raw)
    assert verify_password(raw, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_user_model_fields():
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpw"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashedpw"