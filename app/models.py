from sqlalchemy import Column, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Gasolinera(Base):
    __tablename__ = "gasolineras"

    IDEESS = Column(String, primary_key=True, index=True)
    rotulo = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    localidad = Column(String, nullable=False)
    provincia = Column(String, nullable=False)
    longitud = Column(Float, nullable=False)
    latitud = Column(Float, nullable=False)

    historico = relationship("Historico", back_populates="gasolinera")

class Historico(Base):
    __tablename__ = "historico"

    id = Column(String, primary_key=True, index=True)
    gasolinera_id = Column(String, ForeignKey("gasolineras.IDEESS"), nullable=False)
    fecha = Column(Date, nullable=False)
    precioGasolina95 = Column(Float)
    precioGasolina98 = Column(Float)
    precioGasoleoA = Column(Float)
    precioGasoleoPremium = Column(Float)
    precioGLP = Column(Float)
    precioGNC = Column(Float)
    precioGNL = Column(Float)
    precioHidrogeno = Column(Float)
    precioBioetanol = Column(Float)
    precioBiodiesel = Column(Float)
    precioEsterMetilico = Column(Float)

    gasolinera = relationship("Gasolinera", back_populates="historico")