import os
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives import serialization
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_db
from . import models

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "finance-system-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


def get_current_park_id(
    current_user: models.User = Depends(get_current_user),
    x_park_id: Optional[int] = Header(None),
) -> int:
    if current_user.role == "admin":
        if x_park_id is None:
            raise HTTPException(status_code=400, detail="管理员需要指定园区（X-Park-Id）")
        return x_park_id
    return current_user.park_id


def require_edit_permission(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role == "admin":
        return current_user
    if not current_user.can_edit:
        raise HTTPException(status_code=403, detail="没有编辑权限")
    return current_user


# ---- RSA 非对称加密：前端用公钥加密密码，后端用私钥解密 ----

_KEYS_DIR = Path(__file__).resolve().parent.parent / "keys"
_PRIVATE_KEY_PATH = _KEYS_DIR / "private.pem"
_PUBLIC_KEY_PATH = _KEYS_DIR / "public.pem"


def _load_or_create_keys():
    _KEYS_DIR.mkdir(exist_ok=True)
    if _PRIVATE_KEY_PATH.exists() and _PUBLIC_KEY_PATH.exists():
        private_pem = _PRIVATE_KEY_PATH.read_bytes()
        public_pem = _PUBLIC_KEY_PATH.read_bytes()
    else:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        _PRIVATE_KEY_PATH.write_bytes(private_pem)
        _PUBLIC_KEY_PATH.write_bytes(public_pem)
        try:
            os.chmod(_PRIVATE_KEY_PATH, 0o600)
        except OSError:
            pass
    return private_pem, public_pem


_PRIVATE_PEM, PUBLIC_PEM = _load_or_create_keys()
_PRIVATE_KEY: RSAPrivateKey = serialization.load_pem_private_key(_PRIVATE_PEM, password=None)


def get_public_key_pem() -> str:
    return PUBLIC_PEM.decode("utf-8")


def decrypt_password(cipher_b64: str) -> str:
    cipher = base64.b64decode(cipher_b64)
    plain = _PRIVATE_KEY.decrypt(cipher, padding.PKCS1v15())
    return plain.decode("utf-8")
