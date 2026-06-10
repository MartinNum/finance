from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..database import get_db
from ..auth import get_current_park_id
from ..deps import validate_cycle_ownership
from .. import models, schemas

router = APIRouter()


@router.get("/investments", response_model=List[schemas.InvestmentResponse])
def list_investments(
    cycle_id: int = Query(...),
    investor_name: Optional[str] = Query(None),
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(cycle_id, park_id, db)
    query = db.query(models.Investment).filter(models.Investment.cycle_id == cycle_id)
    if investor_name:
        query = query.filter(models.Investment.investor_name == investor_name)
    return query.order_by(models.Investment.invest_date.desc()).all()


@router.post("/investments", response_model=schemas.InvestmentResponse)
def create_investment(
    item: schemas.InvestmentCreate,
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(item.cycle_id, park_id, db)
    db_item = models.Investment(
        cycle_id=item.cycle_id,
        investor_name=item.investor_name,
        amount=item.amount,
        invest_date=item.invest_date,
        remark=item.remark,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/investments/{item_id}")
def delete_investment(
    item_id: int,
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    db_item = db.query(models.Investment).filter(models.Investment.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")
    validate_cycle_ownership(db_item.cycle_id, park_id, db)
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted successfully"}


@router.get("/investments/balance", response_model=schemas.BalanceSummary)
def get_balance(
    cycle_id: int = Query(...),
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(cycle_id, park_id, db)

    total_investment = db.query(func.sum(models.Investment.amount)).filter(
        models.Investment.cycle_id == cycle_id
    ).scalar() or 0

    total_wages = db.query(func.sum(models.Wage.amount)).filter(
        models.Wage.cycle_id == cycle_id
    ).scalar() or 0

    total_expenses = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.cycle_id == cycle_id
    ).scalar() or 0

    total_expense = total_wages + total_expenses

    return schemas.BalanceSummary(
        total_investment=total_investment,
        total_expense=total_expense,
        balance=total_investment - total_expense,
    )
