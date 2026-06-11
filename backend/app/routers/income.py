from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..auth import get_current_park_id, require_edit_permission
from ..deps import validate_cycle_ownership
from .. import models, schemas

router = APIRouter()


def _compute_investor_ratios(db: Session, cycle_id: int):
    rows = db.query(
        models.Investment.investor_name,
        func.sum(models.Investment.amount).label("total"),
    ).filter(
        models.Investment.cycle_id == cycle_id
    ).group_by(models.Investment.investor_name).all()
    grand_total = sum(r.total for r in rows)
    ratios = []
    for r in rows:
        ratios.append({
            "investor_name": r.investor_name,
            "amount": r.total,
            "ratio": (r.total / grand_total) if grand_total > 0 else 0,
        })
    return ratios, grand_total


def _generate_dividends(db: Session, income_db: models.Income):
    ratios, grand_total = _compute_investor_ratios(db, income_db.cycle_id)
    if grand_total == 0:
        return []
    dividends = []
    for inv in ratios:
        dv = models.Dividend(
            income_id=income_db.id,
            cycle_id=income_db.cycle_id,
            investor_name=inv["investor_name"],
            amount=round(income_db.amount * inv["ratio"], 2),
            ratio=inv["ratio"],
            income_date=income_db.income_date,
        )
        db.add(dv)
        dividends.append(dv)
    return dividends


@router.get("/incomes", response_model=List[schemas.IncomeResponse])
def list_incomes(
    cycle_id: int = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    grade_id: Optional[int] = Query(None),
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(cycle_id, park_id, db)
    query = db.query(models.Income).options(joinedload(models.Income.grade))
    filters = [models.Income.cycle_id == cycle_id]
    if start_date:
        filters.append(models.Income.income_date >= start_date)
    if end_date:
        filters.append(models.Income.income_date <= end_date)
    if grade_id:
        filters.append(models.Income.grade_id == grade_id)
    query = query.filter(and_(*filters))
    return query.order_by(models.Income.income_date.desc()).all()


@router.post("/incomes", response_model=schemas.IncomeResponse)
def create_income(
    item: schemas.IncomeCreate,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(item.cycle_id, park_id, db)
    amount = item.quantity_kg * item.unit_price
    db_income = models.Income(
        cycle_id=item.cycle_id,
        grade_id=item.grade_id,
        quantity_kg=item.quantity_kg,
        unit_price=item.unit_price,
        amount=amount,
        income_date=item.income_date,
        remark=item.remark,
    )
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    _generate_dividends(db, db_income)
    db.commit()
    db.refresh(db_income)
    return db_income


@router.delete("/incomes/{item_id}")
def delete_income(
    item_id: int,
    park_id: int = Depends(get_current_park_id),
    _editor=Depends(require_edit_permission),
    db: Session = Depends(get_db),
):
    db_item = db.query(models.Income).filter(models.Income.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")
    validate_cycle_ownership(db_item.cycle_id, park_id, db)
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted successfully"}


@router.get("/dividends", response_model=List[schemas.DividendResponse])
def list_dividends(
    cycle_id: int = Query(...),
    investor_name: Optional[str] = Query(None),
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(cycle_id, park_id, db)
    query = db.query(models.Dividend).filter(models.Dividend.cycle_id == cycle_id)
    if investor_name:
        query = query.filter(models.Dividend.investor_name == investor_name)
    return query.order_by(models.Dividend.income_date.desc()).all()


@router.get("/dividends/summary", response_model=List[schemas.InvestorDividendSummary])
def dividend_summary(
    cycle_id: int = Query(...),
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(cycle_id, park_id, db)
    ratios, _ = _compute_investor_ratios(db, cycle_id)
    total_income = db.query(func.sum(models.Income.amount)).filter(
        models.Income.cycle_id == cycle_id
    ).scalar() or 0
    dividends = db.query(
        models.Dividend.investor_name,
        func.sum(models.Dividend.amount).label("total"),
    ).filter(
        models.Dividend.cycle_id == cycle_id
    ).group_by(models.Dividend.investor_name).all()
    dividend_map = {d.investor_name: d.total for d in dividends}
    inv_amount_map = {r["investor_name"]: r["amount"] for r in ratios}
    ratio_map = {r["investor_name"]: r["ratio"] for r in ratios}

    investor_names = set(inv_amount_map.keys()) | set(dividend_map.keys())
    result = []
    for name in sorted(investor_names):
        inv_amount = inv_amount_map.get(name, 0)
        div_amount = dividend_map.get(name, 0)
        ratio = ratio_map.get(name, 0)
        result.append(schemas.InvestorDividendSummary(
            investor_name=name,
            total_investment=inv_amount,
            total_dividend=div_amount,
            ratio=ratio,
            pending=round(total_income * ratio - div_amount, 2),
        ))
    return result
