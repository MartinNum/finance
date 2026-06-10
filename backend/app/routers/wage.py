from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..auth import get_current_park_id
from ..deps import validate_cycle_ownership
from .. import models, schemas

router = APIRouter()


@router.get("/wages", response_model=List[schemas.WageResponse])
def list_wages(
    cycle_id: int = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    job_type_id: Optional[int] = Query(None),
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(cycle_id, park_id, db)
    query = db.query(models.Wage).options(joinedload(models.Wage.job_type))

    filters = [models.Wage.cycle_id == cycle_id]
    if start_date:
        filters.append(models.Wage.expense_date >= start_date)
    if end_date:
        filters.append(models.Wage.expense_date <= end_date)
    if job_type_id:
        filters.append(models.Wage.job_type_id == job_type_id)

    query = query.filter(and_(*filters))
    return query.order_by(models.Wage.expense_date.desc()).all()


@router.post("/wages", response_model=schemas.WageResponse)
def create_wage(
    wage: schemas.WageCreate,
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(wage.cycle_id, park_id, db)
    amount = wage.unit_price * wage.headcount * wage.days

    db_wage = models.Wage(
        cycle_id=wage.cycle_id,
        job_type_id=wage.job_type_id,
        unit_price=wage.unit_price,
        headcount=wage.headcount,
        days=wage.days,
        amount=amount,
        expense_date=wage.expense_date,
        remark=wage.remark,
    )
    db.add(db_wage)
    db.commit()
    db.refresh(db_wage)
    return db_wage


@router.put("/wages/{wage_id}", response_model=schemas.WageResponse)
def update_wage(
    wage_id: int,
    wage: schemas.WageUpdate,
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    db_wage = db.query(models.Wage).filter(models.Wage.id == wage_id).first()
    if not db_wage:
        raise HTTPException(status_code=404, detail="Wage record not found")
    validate_cycle_ownership(db_wage.cycle_id, park_id, db)

    update_data = wage.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_wage, key, value)

    db_wage.amount = db_wage.unit_price * db_wage.headcount * db_wage.days
    db.commit()
    db.refresh(db_wage)
    return db_wage


@router.delete("/wages/{wage_id}")
def delete_wage(
    wage_id: int,
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    db_wage = db.query(models.Wage).filter(models.Wage.id == wage_id).first()
    if not db_wage:
        raise HTTPException(status_code=404, detail="Wage record not found")
    validate_cycle_ownership(db_wage.cycle_id, park_id, db)

    db.delete(db_wage)
    db.commit()
    return {"message": "Wage record deleted successfully"}
