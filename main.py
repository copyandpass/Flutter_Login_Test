from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models import MsgPayload, User, Base
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from database import engine
from fastapi.middleware.cors import CORSMiddleware  # ← CORS 미들웨어 import 추가

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 또는 ["*"]로 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messages_list: dict[int, MsgPayload] = {}
users_db = {}
invalid_tokens = set()


@app.get("/")
def root() -> dict[str, str]:
    print("[DEBUG] root endpoint called")
    return {"message": "Hello"}


# About page route
@app.get("/about")
def about() -> dict[str, str]:
    return {"message": "This is the about page."}


# Route to add a message
@app.post("/messages/{msg_name}/")
def add_msg(msg_name: str) -> dict[str, MsgPayload]:
    # Generate an ID for the item based on the highest ID in the messages_list
    msg_id = max(messages_list.keys()) + 1 if messages_list else 0
    messages_list[msg_id] = MsgPayload(msg_id=msg_id, msg_name=msg_name)

    return {"message": messages_list[msg_id]}


# Route to list all messages
@app.get("/messages")
def message_items() -> dict[str, dict[int, MsgPayload]]:
    return {"messages:": messages_list}


class SignupRequest(BaseModel):
    username: str
    password: str
    email: EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/signup", status_code=201)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    # 중복 아이디/이메일 체크
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Duplicate username")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Duplicate email")
    # 비밀번호 해시
    hashed_pw = pwd_context.hash(req.password)
    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hashed_pw
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Signup successful"}


@app.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong password")
    # 실제 서비스에서는 JWT 토큰을 발급해야 함
    return {"access_token": "dummy-token"}


@app.get("/profile")
def profile(request: Request):
    auth = request.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        return JSONResponse(
            content={"message": "Unauthorized"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    token = auth.split(" ")[1]
    if token != "dummy-token" or token in invalid_tokens:
        return JSONResponse(
            content={"message": "Unauthorized"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return JSONResponse(
        content={"message": "Profile info"},
        status_code=status.HTTP_200_OK
    )


@app.post("/logout")
def logout(request: Request):
    auth = request.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        return JSONResponse(
            content={"message": "Unauthorized"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    token = auth.split(" ")[1]
    invalid_tokens.add(token)
    return JSONResponse(
        content={"message": "Logout successful"},
        status_code=status.HTTP_200_OK
    )


# 테스트/앱 시작 시 테이블 자동 생성
Base.metadata.create_all(bind=engine)
