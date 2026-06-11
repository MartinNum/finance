from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_park_id, require_edit_permission
from .. import models, schemas

router = APIRouter()


@router.get("/cycles", response_model=List[schemas.CycleResponse])
def list_cycles(
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    return db.query(models.Cycle).filter(
        models.Cycle.park_id == park_id
    ).order_by(models.Cycle.start_date.desc()).all()


@router.post("/cycles", response_model=schemas.CycleResponse)
def create_cycle(
    cycle: schemas.CycleCreate,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    existing = db.query(models.Cycle).filter(
        models.Cycle.name == cycle.name,
        models.Cycle.park_id == park_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="周期名称已存在")

    is_first = db.query(models.Cycle).filter(models.Cycle.park_id == park_id).count() == 0
    db_cycle = models.Cycle(
        name=cycle.name,
        start_date=cycle.start_date,
        end_date=cycle.end_date,
        is_current=is_first,
        park_id=park_id,
    )
    db.add(db_cycle)
    db.commit()
    db.refresh(db_cycle)
    return db_cycle


@router.put("/cycles/{cycle_id}", response_model=schemas.CycleResponse)
def update_cycle(
    cycle_id: int,
    cycle: schemas.CycleUpdate,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    db_cycle = db.query(models.Cycle).filter(
        models.Cycle.id == cycle_id,
        models.Cycle.park_id == park_id,
    ).first()
    if not db_cycle:
        raise HTTPException(status_code=404, detail="Not found")

    for key, value in cycle.model_dump(exclude_unset=True).items():
        setattr(db_cycle, key, value)

    db.commit()
    db.refresh(db_cycle)
    return db_cycle


@router.delete("/cycles/{cycle_id}")
def delete_cycle(
    cycle_id: int,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    db_cycle = db.query(models.Cycle).filter(
        models.Cycle.id == cycle_id,
        models.Cycle.park_id == park_id,
    ).first()
    if not db_cycle:
        raise HTTPException(status_code=404, detail="Not found")
    if db_cycle.is_current:
        raise HTTPException(status_code=400, detail="不能删除当前活跃周期")

    db.delete(db_cycle)
    db.commit()
    return {"message": "Deleted successfully"}


@router.put("/cycles/{cycle_id}/activate", response_model=schemas.CycleResponse)
def activate_cycle(
    cycle_id: int,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    db_cycle = db.query(models.Cycle).filter(
        models.Cycle.id == cycle_id,
        models.Cycle.park_id == park_id,
    ).first()
    if not db_cycle:
        raise HTTPException(status_code=404, detail="Not found")

    db.query(models.Cycle).filter(
        models.Cycle.park_id == park_id
    ).update({models.Cycle.is_current: False})
    db_cycle.is_current = True
    db.commit()
    db.refresh(db_cycle)
    return db_cycle
