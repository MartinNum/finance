from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_park_id
from ..deps import validate_cycle_ownership
from ..models import GrapeBunchConfig
from .. import schemas

router = APIRouter()


@router.get("/grape-bunch-config", response_model=schemas.GrapeBunchConfigResponse)
def get_grape_bunch_config(
    cycle_id: int,
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(cycle_id, park_id, db)
    config = db.query(GrapeBunchConfig).filter(GrapeBunchConfig.cycle_id == cycle_id).first()
    if not config:
        config = GrapeBunchConfig(
            cycle_id=cycle_id,
            bunch_count=0,
            bunch_weight=0,
            total_weight=0,
            calc_mode="by_weight",
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.put("/grape-bunch-config", response_model=schemas.GrapeBunchConfigResponse)
def update_grape_bunch_config(
    cycle_id: int,
    data: schemas.GrapeBunchConfigUpdate,
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    validate_cycle_ownership(cycle_id, park_id, db)
    config = db.query(GrapeBunchConfig).filter(GrapeBunchConfig.cycle_id == cycle_id).first()
    if not config:
        config = GrapeBunchConfig(cycle_id=cycle_id)
        db.add(config)

    config.bunch_count = data.bunch_count
    config.bunch_weight = data.bunch_weight
    config.total_weight = data.total_weight
    config.calc_mode = data.calc_mode
    db.commit()
    db.refresh(config)
    return config
