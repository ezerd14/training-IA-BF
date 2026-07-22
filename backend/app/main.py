from datetime import datetime, timedelta, timezone
import os

import jwt
from fastapi import FastAPI, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Backend App", version="1.0.0")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 300
REFRESH_TOKEN_EXPIRE_SECONDS = 3600
ADMIN_USERNAME = "admin"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ADMIN_PASSWORD_HASH = password_context.hash("admin123")


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(alias="usuario")
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS


def create_token(subject: str, token_type: str, expires_in: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {"sub": subject, "type": token_type, "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def issue_tokens(subject: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_token(subject, "access", ACCESS_TOKEN_EXPIRE_SECONDS),
        refresh_token=create_token(subject, "refresh", REFRESH_TOKEN_EXPIRE_SECONDS),
    )


def decode_token(token: str, expected_type: str) -> dict[str, str]:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        ) from exc

    if payload.get("type") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token inválido",
        )

    return payload


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/token", response_model=TokenResponse)
def login(credentials: LoginRequest) -> TokenResponse:
    if credentials.username != ADMIN_USERNAME or not password_context.verify(
        credentials.password, ADMIN_PASSWORD_HASH
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    return issue_tokens(credentials.username)


@app.post("/auth/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest) -> TokenResponse:
    token_payload = decode_token(payload.refresh_token, "refresh")
    return issue_tokens(token_payload["sub"])
