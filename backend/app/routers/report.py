from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date

from ..database import get_db
from ..auth import get_current_park_id
from ..deps import validate_cycle_ownership
from .. import models, schemas

router = APIRouter()


@router.get("/report/summary", response_model=schemas.ReportSummary)
def get_report_summary(
    cycle_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(cycle_id, park_id, db)

    wage_total = db.query(func.sum(models.Wage.amount)).filter(
        and_(
            models.Wage.cycle_id == cycle_id,
            models.Wage.expense_date >= start_date,
            models.Wage.expense_date <= end_date,
        )
    ).scalar() or 0

    expense_query = db.query(
        models.Expense.category,
        func.sum(models.Expense.amount).label("total"),
    ).filter(
        and_(
            models.Expense.cycle_id == cycle_id,
            models.Expense.expense_date >= start_date,
            models.Expense.expense_date <= end_date,
        )
    ).group_by(models.Expense.category).all()

    expense_dict = {cat: total for cat, total in expense_query}

    total = wage_total + sum(expense_dict.values())

    categories = []
    if total > 0:
        if wage_total > 0:
            categories.append(schemas.CategorySummary(
                name="工资",
                amount=wage_total,
                ratio=round(wage_total / total, 2),
            ))

        for category, amount in expense_dict.items():
            categories.append(schemas.CategorySummary(
                name=category,
                amount=amount,
                ratio=round(amount / total, 2),
            ))

    return schemas.ReportSummary(
        total=total,
        period={"start": start_date.isoformat(), "end": end_date.isoformat()},
        categories=categories,
    )
