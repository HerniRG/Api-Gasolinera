# app/main.py

import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
from .scheduler import start_scheduler

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gasolineras API",
    description="API para obtener precios de gasolineras y su histórico.",
    version="1.0.0",
)

# Iniciar el scheduler al arrancar la aplicación
start_scheduler()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    logger.info("Accediendo a la ruta raíz '/'")
    return {"message": "API de Gasolineras funcionando correctamente."}

@app.post("/gasolineras/", response_model=schemas.Gasolinera)
def create_gasolinera_endpoint(gasolinera: schemas.GasolineraCreate, db: Session = Depends(get_db)):
    logger.info(f"Intentando crear gasolinera con IDEESS: {gasolinera.IDEESS}")
    db_gasolinera = crud.get_gasolinera(db, IDEESS=gasolinera.IDEESS)
    if db_gasolinera:
        logger.warning(f"Gasolinera con IDEESS {gasolinera.IDEESS} ya existe.")
        raise HTTPException(status_code=400, detail="Gasolinera ya registrada.")
    creada = crud.create_gasolinera(db=db, gasolinera=gasolinera)
    logger.info(f"Gasolinera creada con éxito: {creada.IDEESS}")
    return creada

@app.get("/gasolineras/", response_model=list[schemas.Gasolinera])
def read_gasolineras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info(f"Obteniendo gasolineras con skip={skip} y limit={limit}")
    gasolineras = crud.get_gasolineras(db, skip=skip, limit=limit)
    logger.info(f"Total de gasolineras obtenidas: {len(gasolineras)}")
    return gasolineras

@app.get("/gasolineras/{ideess}/historico/", response_model=list[schemas.Historico])
def read_historico(ideess: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info(f"Obteniendo histórico para gasolinera con IDEESS: {ideess}, skip={skip}, limit={limit}")
    historico = crud.get_historico(db, gasolinera_id=ideess, skip=skip, limit=limit)
    logger.info(f"Total de históricos obtenidos para {ideess}: {len(historico)}")
    return historico

@app.post("/gasolineras/fetch/")
def fetch_gasolineras(db: Session = Depends(get_db)):
    from .utils import parse_and_store_data
    logger.info("Se ha llamado al endpoint /gasolineras/fetch/")
    try:
        parse_and_store_data(db)
        logger.info("Recolección de gasolineras completada con éxito.")
        return {"message": "Recolección de gasolineras completada con éxito."}
    except Exception as e:
        logger.error(f"Error en /gasolineras/fetch/: {e}")
        raise HTTPException(status_code=500, detail=str(e))