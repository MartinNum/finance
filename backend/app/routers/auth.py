from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import verify_password, hash_password, create_access_token, get_current_user, get_public_key_pem, decrypt_password
from .. import models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/public-key")
def get_public_key():
    return {"public_key": get_public_key_pem()}


@router.post("/login", response_model=schemas.LoginResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    try:
        password = decrypt_password(data.password)
    except Exception:
        raise HTTPException(status_code=400, detail="密码解密失败，请刷新页面重试")
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已禁用")

    token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role,
            "park_id": user.park_id,
            "park_name": user.park.name if user.park else None,
            "can_edit": user.can_edit,
        },
    }


@router.get("/me", response_model=schemas.UserInfo)
def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "role": current_user.role,
        "park_id": current_user.park_id,
        "park_name": current_user.park.name if current_user.park else None,
        "can_edit": current_user.can_edit,
    }


@router.put("/password")
def change_password(
    data: schemas.PasswordChange,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        old_password = decrypt_password(data.old_password)
        new_password = decrypt_password(data.new_password)
    except Exception:
        raise HTTPException(status_code=400, detail="密码解密失败，请刷新页面重试")
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    current_user.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "密码修改成功"}
