from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/api/emission-factors", tags=["emission-factors"])


@router.get("/", response_model=List[schemas.EmissionFactorRead])
def list_emission_factors(db: Session = Depends(get_db)):
    return db.query(models.EmissionFactor).all()


@router.post("/", response_model=schemas.EmissionFactorRead, status_code=201)
def create_emission_factor(ef: schemas.EmissionFactorCreate, db: Session = Depends(get_db)):
    db_ef = models.EmissionFactor(**ef.model_dump())
    db.add(db_ef)
    db.commit()
    db.refresh(db_ef)
    return db_ef


@router.get("/{ef_id}", response_model=schemas.EmissionFactorRead)
def get_emission_factor(ef_id: int, db: Session = Depends(get_db)):
    ef = db.query(models.EmissionFactor).filter(models.EmissionFactor.id == ef_id).first()
    if not ef:
        raise HTTPException(status_code=404, detail="Emissionsfaktor nicht gefunden")
    return ef


@router.put("/{ef_id}", response_model=schemas.EmissionFactorRead)
def update_emission_factor(ef_id: int, ef: schemas.EmissionFactorUpdate, db: Session = Depends(get_db)):
    db_ef = db.query(models.EmissionFactor).filter(models.EmissionFactor.id == ef_id).first()
    if not db_ef:
        raise HTTPException(status_code=404, detail="Emissionsfaktor nicht gefunden")
    for key, value in ef.model_dump().items():
        setattr(db_ef, key, value)
    db.commit()
    db.refresh(db_ef)
    return db_ef


@router.delete("/{ef_id}", status_code=204)
def delete_emission_factor(ef_id: int, db: Session = Depends(get_db)):
    db_ef = db.query(models.EmissionFactor).filter(models.EmissionFactor.id == ef_id).first()
    if not db_ef:
        raise HTTPException(status_code=404, detail="Emissionsfaktor nicht gefunden")
    db.delete(db_ef)
    db.commit()
