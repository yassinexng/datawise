from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timedelta
import random, bcrypt


from app.db_config import get_database_connection
from app.models import User, EmailVerification
from .smtp import send_verification_email, send_password_reset_email

router = APIRouter()

class RegisterUser(BaseModel):
    email: str
    username: str
    password: str
    confirmPassword: str

class ConfirmEmail(BaseModel):
    email: str
    code: str

class LoginUser(BaseModel):
    username: str
    password: str

def hash_pw(p):     
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
def check_pw(p, h): 
    return bcrypt.checkpw(p.encode(), h.encode())
def make_code():    
    return str(random.randint(100000, 999999))
def now():          
    return datetime.utcnow()


@router.post("/register")
async def register(user: RegisterUser, db: AsyncSession = Depends(get_database_connection)):

    existing = (await db.execute(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )).scalar_one_or_none()

    if existing:
        if existing.is_verified:
            if existing.email == user.email:
                raise HTTPException(400, "Email already exists")
            raise HTTPException(400, "Username already taken")
        # This wipe unverified user so they can retry
        await db.execute(delete(EmailVerification).where(EmailVerification.username == existing.username))
        await db.execute(delete(User).where(User.username == existing.username))
        await db.commit()

    db.add(User(username=user.username, email=user.email, password_hash=hash_pw(user.password), is_verified=0))
    await db.flush()

    code = make_code()
    db.add(EmailVerification(username=user.username, code=code, expires_at=now() + timedelta(minutes=5)))
    await db.commit()

    print(f"Registered: {user.email} with: {code}", flush=True)
    send_verification_email(user.email, code)
    return {"message": "Check your email for the verification code."}


@router.post("/confirmemail")
async def confirm_email(data: ConfirmEmail, db: AsyncSession = Depends(get_database_connection)):
    user = (await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Email not found")

    v = (await db.execute(select(EmailVerification).where(EmailVerification.username == user.username))).scalar_one_or_none()
    if not v:
        raise HTTPException(404, "No verification code — please register first")
    if v.verified_at:
        raise HTTPException(400, "Already verified — please login")
    if now() > v.expires_at:
        raise HTTPException(400, "Code expired — please register again")

    submitted = data.code.strip()[:6]
    print(f"[CONFIRM] stored='{v.code}' received='{submitted}'", flush=True)

    if v.code != submitted:
        v.attempts += 1
        await db.commit()
        raise HTTPException(400, f"Wrong code — attempt {v.attempts}")

    v.verified_at = now()
    user.is_verified = 1
    await db.commit()
    return {"message": "Email verified successfully"}


@router.post("/login")
async def login(data: LoginUser, db: AsyncSession = Depends(get_database_connection)):
    user = (await db.execute(select(User).where(User.username == data.username))).scalar_one_or_none()

    if not user or not check_pw(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    if not user.is_verified:
        raise HTTPException(403, "Email not verified")

    return {"message": "Login successful", "username": user.username}

class Code(BaseModel):
    email:str | None = None
    code: str | None = None
    password: str | None = None

@router.post("/forgetpassword1")
async def forgetpassword1(data: Code, db: AsyncSession = Depends(get_database_connection)):
    user = (await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Email not found")
    code = make_code()
    user.code_verification = code
    await db.commit()
   
    send_password_reset_email(user.email, code)    
    print(f"code:'{code}'", flush=True)

    return {"message": "Check your email for the verification code."}

@router.post("/forgetpassword2")
async def forgetpassword2(data: Code, db: AsyncSession = Depends(get_database_connection)):
    if not data.code or not data.email:
        raise HTTPException(400, "Invalid code")
    user = (await db.execute(select(User).where((User.code_verification == data.code) & (User.email == data.email)))).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Invalid code or email")
    return {"message": "The code is true"}

@router.post("/forgetpassword3")
async def forgetpassword3(data: Code, db: AsyncSession = Depends(get_database_connection)):
    if not data.code:
        raise HTTPException(400, "Invalid code")
    user = (await db.execute(select(User).where((User.code_verification == data.code) & (User.email == data.email)))).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Invalid code or email")
    user.password_hash = hash_pw(data.password)
    user.code_verification = None
    db.add(user)
    await db.commit()

    
    return {"message": "The code is true"}