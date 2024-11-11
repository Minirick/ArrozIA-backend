import io
import json
import os
from datetime import date, datetime

import torch
from dotenv import load_dotenv
from fastapi import HTTPException
from PIL import Image
from sqlalchemy.orm import Session, joinedload
from timm import create_model
from torchvision import transforms

from src.database.database import \
    SessionLocal  # Importa la sesión de base de datos
from src.models.phytosanitaryDiagnosisModel import \
    DiagnosticoFitosanitario  # Importa el modelo

# Cargar variables de entorno
#load_dotenv()
model_path = os.path.join("src", "models", "swin_transformer_v2.pth")
# Configuración del dispositivo
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Cargar la ruta del modelo desde el archivo .env
#model_path = os.getenv("SWIN_MODEL_PATH")

# Verificar si la ruta existe
if not model_path or not os.path.exists(model_path):
    raise FileNotFoundError(f"El archivo del modelo no se encontró en la ruta: {model_path}")

# Cargar el modelo en memoria utilizando io.BytesIO
with open(model_path, "rb") as f:
    buffer = io.BytesIO(f.read())

# Crear el modelo y cargar solo los pesos
model = create_model('swin_base_patch4_window7_224', pretrained=False, num_classes=10)
model.load_state_dict(torch.load(buffer, map_location=device, weights_only=True))

model = model.to(device)
model.eval()

# Lista de clases
classes = [
    "bacterial_leaf_blight",
    "brown_spot",
    "healthy",
    "leaf_blast",
    "leaf_scald",
    "narrow_brown_spot",
    "neck_blast",
    "rice_hispa",
    "sheath_blight",
    "tungro"
]

# Transformaciones de imagen
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def predict_image(image_data: bytes, cultivo_id: int):
    # Convertir los bytes de la imagen a formato PIL y transformar
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    # Realizar la predicción
    with torch.no_grad():
        output = model(image)
        _, predicted = torch.max(output, 1)
    predicted_class = classes[predicted.item()]

    # Guardar la imagen en el servidor
    image_filename = f"{os.urandom(16).hex()}.jpg"
    image_path = os.path.join("src", "images", image_filename)
    with open(image_path, "wb") as img_file:
        img_file.write(image_data)

    # Guardar el diagnóstico en la base de datos
    db = SessionLocal()
    try:
        diagnostico = DiagnosticoFitosanitario(
            resultado_ia=json.dumps(predicted_class),
            ruta=image_path,  # Guardar la ruta real de la imagen
            cultivo_id=cultivo_id,
            fecha_diagnostico=date.today(),
            confianza_promedio=output[0, predicted.item()].item(),
            tipo_problema=predicted_class,
            imagenes_analizadas=json.dumps(1),  # JSON válido (cambiar int a JSON)
            exportado=False,
            comparacion_diagnostico=None
        )
        db.add(diagnostico)
        db.commit()
        db.refresh(diagnostico)
    finally:
        db.close()

    return diagnostico



def get_diagnostics_by_cultivo(db: Session, cultivo_id: int, start_date: datetime = None, end_date: datetime = None):
    # Log para depuración
    print(f"cultivo_id: {cultivo_id}, start_date: {start_date}, end_date: {end_date}")

    query = db.query(DiagnosticoFitosanitario).filter(DiagnosticoFitosanitario.cultivo_id == cultivo_id)

    if start_date:
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha no válido para start_date")
        query = query.filter(DiagnosticoFitosanitario.fecha_diagnostico >= start_date)

    if end_date:
        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha no válido para end_date")
        query = query.filter(DiagnosticoFitosanitario.fecha_diagnostico <= end_date)

    diagnostics = query.all()

    # Log para depuración de los resultados
    print(f"diagnostics encontrados: {len(diagnostics)}")

    if not diagnostics:
        raise HTTPException(status_code=404, detail="No se encontraron diagnósticos para este cultivo en el rango de fechas especificado.")

    return diagnostics


def get_diagnostic_detail(db: Session, diagnostic_id: int):
    # Cargar la relación 'cultivo' para el detalle del diagnóstico
    diagnostic = (
        db.query(DiagnosticoFitosanitario)
        .options(joinedload(DiagnosticoFitosanitario.cultivo))  # Carga la relación 'cultivo'
        .filter(DiagnosticoFitosanitario.id == diagnostic_id)
        .first()
    )
    if diagnostic is None:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado.")
    return diagnostic