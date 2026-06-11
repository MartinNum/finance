from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..auth import get_current_park_id, require_edit_permission
from ..deps import validate_cycle_ownership
from .. import models, schemas

router = APIRouter()


@router.get("/expenses", response_model=List[schemas.ExpenseResponse])
def list_expenses(
    cycle_id: int = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None),
    sub_category: Optional[str] = Query(None),
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(cycle_id, park_id, db)
    query = db.query(models.Expense)

    filters = [models.Expense.cycle_id == cycle_id]
    if start_date:
        filters.append(models.Expense.expense_date >= start_date)
    if end_date:
        filters.append(models.Expense.expense_date <= end_date)
    if category:
        filters.append(models.Expense.category == category)
    if sub_category:
        filters.append(models.Expense.sub_category == sub_category)

    query = query.filter(and_(*filters))
    return query.order_by(models.Expense.expense_date.desc()).all()


@router.post("/expenses", response_model=schemas.ExpenseResponse)
def create_expense(
    expense: schemas.ExpenseCreate,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(expense.cycle_id, park_id, db)
    db_expense = models.Expense(
        cycle_id=expense.cycle_id,
        category=expense.category,
        sub_category=expense.sub_category,
        amount=expense.amount,
        expense_date=expense.expense_date,
        remark=expense.remark,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.put("/expenses/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(
    expense_id: int,
    expense: schemas.ExpenseUpdate,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense record not found")
    validate_cycle_ownership(db_expense.cycle_id, park_id, db)

    update_data = expense.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_expense, key, value)

    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense record not found")
    validate_cycle_ownership(db_expense.cycle_id, park_id, db)

    db.delete(db_expense)
    db.commit()
    return {"message": "Expense record deleted successfully"}
