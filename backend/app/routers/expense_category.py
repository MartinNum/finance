from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_park_id, require_edit_permission
from .. import models, schemas

router = APIRouter()


@router.get("/expense-categories", response_model=List[schemas.ExpenseCategoryResponse])
def list_expense_categories(
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    return db.query(models.ExpenseCategory).filter(
        models.ExpenseCategory.is_active == True,
        models.ExpenseCategory.park_id == park_id,
    ).order_by(models.ExpenseCategory.category, models.ExpenseCategory.sub_category).all()


@router.post("/expense-categories", response_model=schemas.ExpenseCategoryResponse)
def create_expense_category(
    item: schemas.ExpenseCategoryCreate,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    existing = db.query(models.ExpenseCategory).filter(
        models.ExpenseCategory.category == item.category,
        models.ExpenseCategory.sub_category == item.sub_category,
        models.ExpenseCategory.park_id == park_id,
    ).first()
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.commit()
            db.refresh(existing)
            return existing
        raise HTTPException(status_code=400, detail="该分类已存在")

    db_item = models.ExpenseCategory(
        category=item.category,
        sub_category=item.sub_category,
        sort_order=item.sort_order,
        park_id=park_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/expense-categories/{item_id}")
def delete_expense_category(
    item_id: int,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    db_item = db.query(models.ExpenseCategory).filter(
        models.ExpenseCategory.id == item_id,
        models.ExpenseCategory.park_id == park_id,
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")

    db_item.is_active = False
    db.commit()
    return {"message": "Deleted successfully"}
