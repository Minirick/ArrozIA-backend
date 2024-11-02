from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.models.weatherRecordModel import WeatherRecord
from src.schemas.weatherRecordSchema import WeatherRecordCreate, WeatherRecordResponse
from src.controller.weatherRecordController import (
    createWeatherRecord,
    fetchWeatherRecord,
    getWeatherRecommendations,
    fetchWeatherHistory,
    createManualWeatherRecord,
    createWeatherRecordFromAPI,
    fetchWeatherRecordDetail   # Nueva función para obtener detalles específicos
)

WEATHER_RECORD_ROUTES = APIRouter()

@WEATHER_RECORD_ROUTES.post("/weather-record/", response_model=WeatherRecordResponse)
def registerWeatherRecord(
    record: WeatherRecordCreate, db: Session = Depends(get_db)):
    return createWeatherRecord(db, record)

@WEATHER_RECORD_ROUTES.post("/meteorology/manual", response_model=WeatherRecordResponse)
def registerManualWeatherRecord(
    record: WeatherRecordCreate, db: Session = Depends(get_db)):
    return createManualWeatherRecord(db, record)

@WEATHER_RECORD_ROUTES.post("/meteorology/api", response_model=WeatherRecordResponse)
def registerWeatherRecordFromAPI(lote_id: int, db: Session = Depends(get_db)):
    return createWeatherRecordFromAPI(db, lote_id)

@WEATHER_RECORD_ROUTES.get("/weather-record/{lote_id}/recommendations")
def getRecommendations(lote_id: int, db: Session = Depends(get_db)):
    return getWeatherRecommendations(db, lote_id)

@WEATHER_RECORD_ROUTES.get("/weather-record/by-date/{fecha}/{lote_id}", response_model=WeatherRecordResponse)
def getWeatherRecord(fecha: str, lote_id: int, db: Session = Depends(get_db)):
    record = fetchWeatherRecord(db, fecha, lote_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return record

# Endpoint para consultar el historial meteorológico de un lote
@WEATHER_RECORD_ROUTES.get("/meteorology/history/{lote_id}", response_model=List[WeatherRecordResponse])
def getWeatherHistory(
    lote_id: int,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    fuente_datos: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return fetchWeatherHistory(db, lote_id, fecha_inicio, fecha_fin, fuente_datos)

# Endpoint para ver el detalle de un registro meteorológico específico
@WEATHER_RECORD_ROUTES.get("/meteorology/history/detail/{id}", response_model=WeatherRecordResponse)
def getWeatherRecordDetail(id: int, db: Session = Depends(get_db)):
    record = fetchWeatherRecordDetail(db, id)
    if record is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return record

@WEATHER_RECORD_ROUTES.put("/meteorology/history/update/{id}", response_model=WeatherRecordResponse)
def updateWeatherRecord(
    id: int,
    record: WeatherRecordCreate,
    db: Session = Depends(get_db)
):
    existing_record = db.query(WeatherRecord).filter(WeatherRecord.id == id).first()
    if existing_record is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # Actualizar los campos del registro existente
    for key, value in record.dict().items():
        setattr(existing_record, key, value)

    # Asignar valor por defecto a 'fuente_datos' si está vacío
    if existing_record.fuente_datos is None:
        existing_record.fuente_datos = "manual"  # Valor por defecto

    db.commit()
    db.refresh(existing_record)
    return existing_record