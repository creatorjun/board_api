from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

security_scheme = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # 디버깅을 위해 토큰 생성 시 사용하는 SECRET_KEY 앞 5자리를 출력합니다.
    print(f"\n--- [토큰 생성 시점] 사용된 SECRET_KEY (앞 5자리): {settings.SECRET_KEY[:5]}... ---")
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> User:
    
    # 디버깅을 위해 토큰 검증 시 사용하는 SECRET_KEY 앞 5자리를 출력합니다.
    print(f"\n--- [토큰 검증 시점] 사용된 SECRET_KEY (앞 5자리): {settings.SECRET_KEY[:5]}... ---")
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_from_payload = payload.get("sub")
        if user_id_from_payload is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing user identifier")

    except JWTError as e:
        print(f"--- !!!오류!!!: JWT 디코딩 실패. 원인: {e} ---") # 실제 오류 원인 출력
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token signature is invalid or has expired")
    
    user_id = int(user_id_from_payload)
    user = await db.get(User, user_id)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"User with id {user_id} not found")
    
    return user