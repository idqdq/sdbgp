from typing import Optional
from datetime import datetime, timedelta
from fastapi import Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from models import UserBase, UserInDB
from config import Settings


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
settings = Settings()


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)


async def authenticate(request: Request, user: str, password: str) -> Optional[UserInDB]:
    if (obj_user := await request.app.db.user.find_one({"user": user})) is not None:       
        if not _verify_password(password, obj_user["hashed_password"]):  
            return None
    return obj_user


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = dict(user=data["user"],hashed_password=data["hashed_password"])

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> UserBase:    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        username: str = payload.get("user")
        #token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=400, detail="wrong token")

    user = await request.app.db.user.find_one({"user": username})
    if user is None:
        raise HTTPException(status_code=400, detail="token and user doesn't match")        
    
    return UserBase(user=user["user"], is_superuser=user["is_superuser"])
    