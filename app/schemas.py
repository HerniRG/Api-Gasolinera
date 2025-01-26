from pydantic import BaseModel
from typing import Optional
from datetime import date

class GasolineraBase(BaseModel):
    IDEESS: str
    rotulo: str
    direccion: str
    localidad: str
    provincia: str
    longitud: float
    latitud: float

class GasolineraCreate(GasolineraBase):
    pass

class Gasolinera(GasolineraBase):
    class Config:
        orm_mode = True

class HistoricoBase(BaseModel):
    id: str
    gasolinera_id: str
    fecha: date
    precioGasolina95: Optional[float]
    precioGasolina98: Optional[float]
    precioGasoleoA: Optional[float]
    precioGasoleoPremium: Optional[float]
    precioGLP: Optional[float]
    precioGNC: Optional[float]
    precioGNL: Optional[float]
    precioHidrogeno: Optional[float]
    precioBioetanol: Optional[float]
    precioBiodiesel: Optional[float]
    precioEsterMetilico: Optional[float]

class HistoricoCreate(HistoricoBase):
    pass

class Historico(HistoricoBase):
    class Config:
        orm_mode = True