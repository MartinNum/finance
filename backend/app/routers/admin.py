from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..auth import require_admin, hash_password, decrypt_password
from ..services.seed import create_park_seed_data
from .. import models, schemas

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/parks", response_model=List[schemas.ParkResponse])
def list_parks(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(models.Park).order_by(models.Park.id).all()


@router.post("/parks", response_model=schemas.ParkResponse)
def create_park(
    park: schemas.ParkCreate,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if db.query(models.Park).filter(models.Park.name == park.name).first():
        raise HTTPException(status_code=400, detail="园区名称已存在")
    db_park = models.Park(name=park.name)
    db.add(db_park)
    db.flush()
    create_park_seed_data(db, db_park.id)
    db.commit()
    db.refresh(db_park)
    return db_park


@router.put("/parks/{park_id}", response_model=schemas.ParkResponse)
def update_park(
    park_id: int,
    park: schemas.ParkUpdate,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_park = db.query(models.Park).filter(models.Park.id == park_id).first()
    if not db_park:
        raise HTTPException(status_code=404, detail="园区不存在")
    for key, value in park.model_dump(exclude_unset=True).items():
        setattr(db_park, key, value)
    db.commit()
    db.refresh(db_park)
    return db_park


@router.delete("/parks/{park_id}")
def delete_park(
    park_id: int,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_park = db.query(models.Park).filter(models.Park.id == park_id).first()
    if not db_park:
        raise HTTPException(status_code=404, detail="园区不存在")
    db_park.is_active = False
    db.commit()
    return {"message": "园区已停用"}


@router.get("/users", response_model=List[schemas.UserResponse])
def list_users(
    park_id: Optional[int] = None,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.User)
    if park_id is not None:
        query = query.filter(models.User.park_id == park_id)
    return query.order_by(models.User.id).all()


@router.post("/users", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if user.park_id:
        park = db.query(models.Park).filter(models.Park.id == user.park_id).first()
        if not park:
            raise HTTPException(status_code=400, detail="园区不存在")
    try:
        plain_password = decrypt_password(user.password)
    except Exception:
        raise HTTPException(status_code=400, detail="密码解密失败，请刷新页面重试")
    db_user = models.User(
        username=user.username,
        hashed_password=hash_password(plain_password),
        display_name=user.display_name,
        role=user.role,
        park_id=user.park_id,
        can_edit=user.can_edit,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/users/{user_id}/reset-password")
def reset_password(
    user_id: int,
    data: schemas.PasswordReset,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    try:
        new_password = decrypt_password(data.new_password)
    except Exception:
        raise HTTPException(status_code=400, detail="密码解密失败，请刷新页面重试")
    db_user.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "密码重置成功"}
