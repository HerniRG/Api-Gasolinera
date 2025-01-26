from sqlalchemy.orm import Session
from . import models, schemas

def get_gasolineras(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Gasolinera).offset(skip).limit(limit).all()

def get_gasolinera(db: Session, IDEESS: str):
    return db.query(models.Gasolinera).filter(models.Gasolinera.IDEESS == IDEESS).first()

def create_gasolinera(db: Session, gasolinera: schemas.GasolineraCreate):
    db_gasolinera = models.Gasolinera(**gasolinera.dict())
    db.add(db_gasolinera)
    db.commit()
    db.refresh(db_gasolinera)
    return db_gasolinera

def get_historico(db: Session, gasolinera_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Historico).filter(models.Historico.gasolinera_id == gasolinera_id).offset(skip).limit(limit).all()

def create_historico(db: Session, historico: schemas.HistoricoCreate):
    db_historico = models.Historico(**historico.dict())
    db.add(db_historico)
    db.commit()
    db.refresh(db_historico)
    return db_historico