from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models


def validate_cycle_ownership(cycle_id: int, park_id: int, db: Session) -> models.Cycle:
    cycle = db.query(models.Cycle).filter(
        models.Cycle.id == cycle_id,
        models.Cycle.park_id == park_id,
    ).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="周期不存在或无权访问")
    return cycle
