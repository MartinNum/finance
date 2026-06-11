from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_park_id, require_edit_permission
from .. import models, schemas

router = APIRouter()


@router.get("/grape-grades", response_model=List[schemas.GrapeGradeResponse])
def list_grape_grades(
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    return db.query(models.GrapeGrade).filter(
        models.GrapeGrade.park_id == park_id
    ).order_by(models.GrapeGrade.id).all()


@router.post("/grape-grades", response_model=schemas.GrapeGradeResponse)
def create_grape_grade(
    item: schemas.GrapeGradeCreate,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    if db.query(models.GrapeGrade).filter(
        models.GrapeGrade.name == item.name,
        models.GrapeGrade.park_id == park_id,
    ).first():
        raise HTTPException(status_code=400, detail="等级名称已存在")
    db_item = models.GrapeGrade(
        name=item.name,
        default_price=item.default_price,
        is_active=item.is_active,
        park_id=park_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/grape-grades/{item_id}", response_model=schemas.GrapeGradeResponse)
def update_grape_grade(
    item_id: int,
    item: schemas.GrapeGradeUpdate,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    db_item = db.query(models.GrapeGrade).filter(
        models.GrapeGrade.id == item_id,
        models.GrapeGrade.park_id == park_id,
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/grape-grades/{item_id}")
def delete_grape_grade(
    item_id: int,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    db_item = db.query(models.GrapeGrade).filter(
        models.GrapeGrade.id == item_id,
        models.GrapeGrade.park_id == park_id,
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted successfully"}
