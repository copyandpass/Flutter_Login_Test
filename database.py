from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 사용자명과 비밀번호를 실제 값으로 변경하세요.
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://root:1111@{DB_HOST}:3306/my_login_db"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    print("[DEBUG] get_db() called")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
