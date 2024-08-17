
import src.schemas.schemas as schemas
import src.models.models as models
import jwt
from datetime import datetime
from src.models.models import User, TokenTable
from src.database.database import Base, engine, SessionLocal
from fastapi import FastAPI, Depends, HTTPException,status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from src.helpers.auth_bearer import JWTBearer
from functools import wraps
from src.helpers.utils import create_access_token, create_refresh_token, verify_password, get_hashed_password,JWT_SECRET_KEY, ALGORITHM
from src.helpers.auth_bearer import JWTBearer



Base.metadata.create_all(engine)    
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
app=FastAPI()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"   # should be kept secret
JWT_REFRESH_SECRET_KEY = "13ugfdfgh@#$%^@&jkl45678902"

@app.post("/users/register")
def register_user(user: schemas.CrearUsuario, session: Session = Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password = get_hashed_password(user.password)

    new_user = models.User(nombre=user.nombre, apellido=user.apellido, email=user.email, password=encrypted_password )
    #new_user = models.User(nombre=user.nombre, apellido=user.apellido, email=user.email, password=user.password )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message":"user created successfully"}

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"   # should be kept secret
JWT_REFRESH_SECRET_KEY = "13ugfdfgh@#$%^@&jkl45678902"

@app.post('/login' ,response_model=schemas.TokenSchema)

def login(request: schemas.requestdetails, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email")
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    access=create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = models.TokenTable(user_id=user.id,  access_toke=access,  refresh_toke=refresh, status=True)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }

@app.get('/users/getusers',)

def getusers( dependencies=Depends(JWTBearer()),session: Session = Depends(get_session)):
    user = session.query(models.User).all()
    return user

@app.get('/users/{user_id}', )

def get_user(user_id: int, dependencies=[Depends(JWTBearer())], db: Session = Depends(get_session)):
    # Buscar el usuario en la base de datos
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@app.put('/users/update/{user_id}')

def update_user(user_id: int, user_update: schemas.UpdateUser, db: Session = Depends(get_session)):
    # Buscar el usuario en la base de datos
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Actualizar la información del usuario solo si se proporciona un nuevo valor
    if user_update.nombre is not None:
        user.nombre = user_update.nombre
    if user_update.apellido is not None:
        user.apellido = user_update.apellido
    if user_update.email is not None:
        # Verificar si el nuevo email ya está registrado
        existing_user = db.query(models.User).filter(models.User.email == user_update.email).first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user.email = user_update.email  
    
    db.commit()
    db.refresh(user)
    
    return {"message": "User updated successfully", "user": user}

@app.delete('/users/delete/{user_id}')

def deleteUser(user_id: int, db: Session = Depends(get_session)):
    # Buscar el usuario en la base de datos
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Eliminar el usuario de la base de datos
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully", "status": status.HTTP_200_OK}

@app.post('/change-password')
def change_password(request: schemas.changepassword, db: Session = Depends(get_session)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")
    
    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()
    
    return {"message": "Password changed successfully"}































































































# @app.post('/logout')
# def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_session)):
#     token=dependencies
#     payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
#     user_id = payload['sub']
#     token_record = db.query(models.TokenTable).all()
#     info=[]
#     for record in token_record :
#         print("record",record)
#         if (datetime.utcnow() - record.created_date).days >1:
#             info.append(record.user_id)
#     if info:
#         existing_token = db.query(models.TokenTable).where(TokenTable.user_id.in_(info)).delete()
#         db.commit()
        
#     existing_token = db.query(models.TokenTable).filter(models.TokenTable.user_id == user_id, models.TokenTable.access_toke==token).first()
#     if existing_token:
#         existing_token.status=False
#         db.add(existing_token)
#         db.commit()
#         db.refresh(existing_token)
#     return {"message":"Logout Successfully"} 