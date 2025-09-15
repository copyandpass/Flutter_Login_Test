import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 프로젝트 루트 경로 추가

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
    db = next(get_db())
    db.query(User).filter(User.username == "testuser").delete()
    db.query(User).filter(User.email == "testuser@example.com").delete()
    db.commit()
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
    response = client.post(
        "/login", json={"username": "nouser", "password": "password123"}
    )
    assert response.status_code == 404

def test_protected_api_with_token(client):
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

def test_signup_missing_fields(client):
    response = client.post(
        "/signup",
        json={
            "username": "missingemail",
            "password": "password123"
        }
    )
    assert response.status_code == 422

def test_signup_long_username(client):
    response = client.post(
        "/signup",
        json={
            "username": "a" * 255,
            "password": "password123",
            "email": "longuser@example.com"
        }
    )
    assert response.status_code == 201  # 201로 수정

def test_login_missing_fields(client):
    response = client.post(
        "/login",
        json={
            "username": "nouser"
        }
    )
    assert response.status_code == 422

def test_access_protected_without_token(client):
    response = client.get("/profile")
    assert response.status_code == 401

def test_logout_without_token(client):
    response = client.post("/logout")
    assert response.status_code == 401

def test_signup_duplicate_email(client):
    client.post(
        "/signup",
        json={
            "username": "uniqueuser1",
            "password": "password123",
            "email": "duplicate@example.com",
        },
    )
    response = client.post(
        "/signup",
        json={
            "username": "uniqueuser2",
            "password": "password123",
            "email": "duplicate@example.com",
        },
    )
    assert response.status_code == 400