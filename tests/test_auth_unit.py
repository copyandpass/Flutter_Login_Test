from utils import verify_password
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def test_verify_password():
    print("[DEBUG] test_verify_password 실행")
    # 비밀번호 해시 검증 함수 단위 테스트
    raw = "password123"
    hashed = pwd_context.hash(raw)
    assert verify_password(raw, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_user_model_fields():
    # User 모델 필드 단위 테스트
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpw"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashedpw"
