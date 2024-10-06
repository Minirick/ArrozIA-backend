from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base
from src.models.landModel import Land
from src.models.varietyArrozModel import VariedadArroz
from src.models.weightUnitModel import WeightUnit


class Crop(Base):
    __tablename__ = 'cultivo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cropName = Column('nombre_cultivo', String(100), nullable=False) 
    varietyId = Column('variedad_id', Integer, ForeignKey('variedad_arroz.id'), nullable=False)  
    plotId = Column('lote_id', Integer, ForeignKey('lote.id'), nullable=False) 
    plantingDate = Column('fecha_siembra', Date, nullable=True)  
    estimatedHarvestDate = Column('fecha_estimada_cosecha', Date, nullable=True)  
   
    #weightUnitId = Column('unidad_peso_id', Integer, ForeignKey('unidad_peso.id'), nullable=True)
   

    # Relaciones
    variety = relationship("VariedadArroz", back_populates="crops")
    lotes = relationship("Land", back_populates="crops")
    #weightUnit = relationship("WeightUnit", back_populates="crops")
