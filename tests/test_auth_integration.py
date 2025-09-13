import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db, SQLALCHEMY_DATABASE_URL
from models import User
import sqlalchemy


@pytest.fixture(autouse=True)
def cleanup_users_table():
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("DELETE FROM logins"))
        conn.execute(sqlalchemy.text("DELETE FROM users"))
        conn.commit()
    yield


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_signup_success(client):
    print("[DEBUG] test_signup_success 실행")
    # 테스트 시작 전 DB에서 동일한 username/email 삭제
    db = next(get_db())
    db.query(User).filter(User.username == "testuser").delete()
    db.query(User).filter(User.email == "testuser@example.com").delete()
    db.commit()
    # /signup 엔드포인트 정상 동작 및 DB 저장
    response = client.post(
        "/signup",
        json={
            "username": "testuser",
            "password": "password123",
            "email": "testuser@example.com",
        },
    )
    assert response.status_code == 201


def test_signup_duplicate_username(client):
    # 중복 아이디 입력 시 제약조건 위반 에러 반환
    client.post(
        "/signup",
        json={
            "username": "dupuser",
            "password": "password123",
            "email": "dupuser@example.com",
        },
    )
    response = client.post(
        "/signup",
        json={
            "username": "dupuser",
            "password": "password123",
            "email": "dupuser@example.com",
        },
    )
    assert response.status_code == 400


def test_signup_invalid_input(client):
    # 잘못된 입력(짧은 비밀번호, 잘못된 이메일) 422 반환
    response = client.post(
        "/signup",
        json={
            "username": "baduser",
            "password": "pw",
            "email": "not-an-email"
        }
    )
    assert response.status_code == 422


def test_login_success_and_token(client):
    # /login 정상 플로우: DB 조회, 비밀번호 검증, 토큰 발급
    client.post(
        "/signup",
        json={
            "username": "loginuser",
            "password": "password123",
            "email": "loginuser@example.com",
        },
    )
    response = client.post(
        "/login",
        json={
            "username": "loginuser",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    # 잘못된 비밀번호 401 반환
    client.post(
        "/signup",
        json={
            "username": "wrongpwuser",
            "password": "password123",
            "email": "wrongpwuser@example.com",
        },
    )
    response = client.post(
        "/login", json={"username": "wrongpwuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_user_not_found(client):
    # 없는 아이디 404 반환
    response = client.post(
        "/login", json={"username": "nouser", "password": "password123"}
    )
    assert response.status_code == 404


def test_protected_api_with_token(client):
    # 로그인 후 토큰으로 보호된 API 접근
    client.post(
        "/signup",
        json={
            "username": "profileuser",
            "password": "password123",
            "email": "profileuser@example.com",
        },
    )
    login = client.post(
        "/login", json={"username": "profileuser", "password": "password123"}
    )
    token = login.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/profile", headers=headers)
    assert response.status_code == 200


def test_logout_and_block_access(client):
    # 로그아웃 후 토큰 무효화 및 접근 차단
    client.post(
        "/signup",
        json={
            "username": "logoutuser",
            "password": "password123",
            "email": "logoutuser@example.com",
        },
    )
    login = client.post(
        "/login", json={"username": "logoutuser", "password": "password123"}
    )
    token = login.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    logout = client.post("/logout", headers=headers)
    assert logout.status_code == 200
    response = client.get("/profile", headers=headers)
    assert response.status_code == 401
