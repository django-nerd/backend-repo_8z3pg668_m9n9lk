import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

from database import db, create_document, get_documents
from schemas import User, Article, Indicator, Message, LibraryItem, CalendarEvent, Earning, SupportTicket

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginInput(BaseModel):
    username: str
    password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc).timestamp() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.get("/")
async def root():
    return {"message": "Trading Community API running"}


@app.get("/schema")
async def read_schema():
    # Provide schemas info to viewer tools if needed
    return {
        "collections": [
            "user", "article", "indicator", "message", "libraryitem", "calendarevent", "earning", "supportticket"
        ]
    }


@app.post("/auth/register", response_model=Token)
async def register(body: LoginInput):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    existing = db["user"].find_one({"username": body.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=body.username, password_hash=get_password_hash(body.password))
    create_document("user", user)
    token = create_access_token({"sub": body.username, "role": "member"})
    return Token(access_token=token)


@app.post("/auth/login", response_model=Token)
async def login(body: LoginInput):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    doc = db["user"].find_one({"username": body.username})
    if not doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(body.password, doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": body.username, "role": doc.get("role", "member")})
    return Token(access_token=token)


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response
