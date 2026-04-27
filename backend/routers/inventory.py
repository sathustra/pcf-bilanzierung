from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


# ── Materials ─────────────────────────────────────────────────────────────────

@router.get("/materials/{product_id}", response_model=List[schemas.MaterialEntryRead])
def list_materials(product_id: int, db: Session = Depends(get_db)):
    return (db.query(models.MaterialEntry)
            .options(joinedload(models.MaterialEntry.emission_factor))
            .filter(models.MaterialEntry.product_id == product_id)
            .all())


@router.post("/materials/", response_model=schemas.MaterialEntryRead, status_code=201)
def create_material(entry: schemas.MaterialEntryCreate, db: Session = Depends(get_db)):
    db_entry = models.MaterialEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    db.refresh(db_entry, ["emission_factor"])
    return db_entry


@router.put("/materials/{entry_id}", response_model=schemas.MaterialEntryRead)
def update_material(entry_id: int, entry: schemas.MaterialEntryUpdate, db: Session = Depends(get_db)):
    db_entry = db.query(models.MaterialEntry).filter(models.MaterialEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    for key, value in entry.model_dump().items():
        setattr(db_entry, key, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/materials/{entry_id}", status_code=204)
def delete_material(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.MaterialEntry).filter(models.MaterialEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    db.delete(db_entry)
    db.commit()


# ── Energy ────────────────────────────────────────────────────────────────────

@router.get("/energy/{product_id}", response_model=List[schemas.EnergyEntryRead])
def list_energy(product_id: int, db: Session = Depends(get_db)):
    return (db.query(models.EnergyEntry)
            .options(joinedload(models.EnergyEntry.emission_factor))
            .filter(models.EnergyEntry.product_id == product_id)
            .all())


@router.post("/energy/", response_model=schemas.EnergyEntryRead, status_code=201)
def create_energy(entry: schemas.EnergyEntryCreate, db: Session = Depends(get_db)):
    db_entry = models.EnergyEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    db.refresh(db_entry, ["emission_factor"])
    return db_entry


@router.put("/energy/{entry_id}", response_model=schemas.EnergyEntryRead)
def update_energy(entry_id: int, entry: schemas.EnergyEntryUpdate, db: Session = Depends(get_db)):
    db_entry = db.query(models.EnergyEntry).filter(models.EnergyEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    for key, value in entry.model_dump().items():
        setattr(db_entry, key, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/energy/{entry_id}", status_code=204)
def delete_energy(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.EnergyEntry).filter(models.EnergyEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    db.delete(db_entry)
    db.commit()


# ── Transport ─────────────────────────────────────────────────────────────────

@router.get("/transport/{product_id}", response_model=List[schemas.TransportEntryRead])
def list_transport(product_id: int, db: Session = Depends(get_db)):
    entries = (db.query(models.TransportEntry)
               .options(joinedload(models.TransportEntry.emission_factor))
               .filter(models.TransportEntry.product_id == product_id)
               .all())
    result = []
    for e in entries:
        data = schemas.TransportEntryRead.model_validate(e)
        data.transport_performance_tkm = e.transport_performance_tkm
        result.append(data)
    return result


@router.post("/transport/", response_model=schemas.TransportEntryRead, status_code=201)
def create_transport(entry: schemas.TransportEntryCreate, db: Session = Depends(get_db)):
    db_entry = models.TransportEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    db.refresh(db_entry, ["emission_factor"])
    data = schemas.TransportEntryRead.model_validate(db_entry)
    data.transport_performance_tkm = db_entry.transport_performance_tkm
    return data


@router.put("/transport/{entry_id}", response_model=schemas.TransportEntryRead)
def update_transport(entry_id: int, entry: schemas.TransportEntryUpdate, db: Session = Depends(get_db)):
    db_entry = db.query(models.TransportEntry).filter(models.TransportEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    for key, value in entry.model_dump().items():
        setattr(db_entry, key, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/transport/{entry_id}", status_code=204)
def delete_transport(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.TransportEntry).filter(models.TransportEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    db.delete(db_entry)
    db.commit()


# ── Waste ─────────────────────────────────────────────────────────────────────

@router.get("/waste/{product_id}", response_model=List[schemas.WasteEntryRead])
def list_waste(product_id: int, db: Session = Depends(get_db)):
    return (db.query(models.WasteEntry)
            .options(joinedload(models.WasteEntry.emission_factor))
            .filter(models.WasteEntry.product_id == product_id)
            .all())


@router.post("/waste/", response_model=schemas.WasteEntryRead, status_code=201)
def create_waste(entry: schemas.WasteEntryCreate, db: Session = Depends(get_db)):
    db_entry = models.WasteEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    db.refresh(db_entry, ["emission_factor"])
    return db_entry


@router.put("/waste/{entry_id}", response_model=schemas.WasteEntryRead)
def update_waste(entry_id: int, entry: schemas.WasteEntryUpdate, db: Session = Depends(get_db)):
    db_entry = db.query(models.WasteEntry).filter(models.WasteEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    for key, value in entry.model_dump().items():
        setattr(db_entry, key, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/waste/{entry_id}", status_code=204)
def delete_waste(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.WasteEntry).filter(models.WasteEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    db.delete(db_entry)
    db.commit()
