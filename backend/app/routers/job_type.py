from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_park_id
from .. import models, schemas

router = APIRouter()


@router.get("/job-types", response_model=List[schemas.JobTypeResponse])
def list_job_types(
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    return db.query(models.JobType).filter(
        models.JobType.is_active == True,
        models.JobType.park_id == park_id,
    ).all()


@router.post("/job-types", response_model=schemas.JobTypeResponse)
def create_job_type(
    job_type: schemas.JobTypeCreate,
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    existing = db.query(models.JobType).filter(
        models.JobType.name == job_type.name,
        models.JobType.park_id == park_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Job type name already exists")

    db_job_type = models.JobType(
        name=job_type.name,
        billing_type=job_type.billing_type,
        default_price=job_type.default_price,
        is_active=job_type.is_active,
        park_id=park_id,
    )
    db.add(db_job_type)
    db.commit()
    db.refresh(db_job_type)
    return db_job_type


@router.put("/job-types/{job_type_id}", response_model=schemas.JobTypeResponse)
def update_job_type(
    job_type_id: int,
    job_type: schemas.JobTypeUpdate,
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    db_job_type = db.query(models.JobType).filter(
        models.JobType.id == job_type_id,
        models.JobType.park_id == park_id,
    ).first()
    if not db_job_type:
        raise HTTPException(status_code=404, detail="Job type not found")

    for key, value in job_type.model_dump(exclude_unset=True).items():
        setattr(db_job_type, key, value)

    db.commit()
    db.refresh(db_job_type)
    return db_job_type


@router.delete("/job-types/{job_type_id}")
def delete_job_type(
    job_type_id: int,
    park_id: int = Depends(get_current_park_id),
    db: Session = Depends(get_db),
):
    db_job_type = db.query(models.JobType).filter(
        models.JobType.id == job_type_id,
        models.JobType.park_id == park_id,
    ).first()
    if not db_job_type:
        raise HTTPException(status_code=404, detail="Job type not found")

    db_job_type.is_active = False
    db.commit()
    return {"message": "Job type deleted successfully"}
