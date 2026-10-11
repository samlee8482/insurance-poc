import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# JWT 서명 설정
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)


# JWT 토큰 발급
def create_token(username: str, role: str):
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY 환경변수가 설정되지 않았습니다.")

    now = datetime.now(timezone.utc)

    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=30)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# JWT 토큰 검증
def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="인증 토큰이 없습니다.")

    if not SECRET_KEY:
        raise HTTPException(status_code=500, detail="JWT 서버 설정 오류")

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "role", "iat", "exp"]}
        )
        return payload

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")


# RBAC 권한 검사
def require_role(allowed_roles: list[str]):
    def check_role(payload: dict = Depends(verify_token)):
        if payload.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        return payload

    return check_role