import os
from passlib.context import CryptContext
from passlib.context import CryptContext
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Union, Any
from typing import Union, Any
from jose import jwt, JWTError
from jose import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.database import get_session
from src.models.userModel import User
from src.models.rolModel import UsuarioFincaRol, Rol
from src.models.permissionModel import Permission, RolPermiso
from src.helpers.auth_bearer import JWTBearer
from src.helpers.config import JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
# Configuración de hashing de contraseñas

passwordContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return passwordContext.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return passwordContext.verify(password, hashed_pass)

def create_access_token(subject: Union[str, Any], expiresDelta: int = None) -> str:
    if expiresDelta is not None:
        expiresDelta = datetime.utcnow() + expiresDelta
        
    else:
        expiresDelta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
         
    
    to_encode = {"exp": expiresDelta, "sub": str(subject)}
    encodedJwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
     
    return encodedJwt

def create_refresh_token(subject: Union[str, Any], expiresDelta: int = None) -> str:
    if expiresDelta is not None:
        expiresDelta = datetime.utcnow() + expiresDelta
    else:
        expiresDelta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    toEncode = {"exp": expiresDelta, "sub": str(subject)}
    encodedJwt = jwt.encode(toEncode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encodedJwt

import uuid

def generate_password_reset_token():
    return str(uuid.uuid4())

def send_password_reset_email(email: str, token: str):
    # Esto es solo un ejemplo. Deberías integrar un servicio real de envío de correos.
    print(f"Se ha enviado un correo electrónico a {email} con el token de restablecimiento de contraseña: {token}")

def get_current_user(token: str = Depends(JWTBearer()), db: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Asegúrate de que la función esté correctamente indentada
def generate_password_reset_token():
    return str(uuid.uuid4())

def send_password_reset_email(email: str, token: str):
    # Esto es solo un ejemplo. Deberías integrar un servicio real de envío de correos.
    print(f"Se ha enviado un correo electrónico a {email} con el token de restablecimiento de contraseña: {token}")

def verify_permission(permission_name: str):
    def verify(user: User = Depends(get_current_user), db: Session = Depends(get_session)):
        # Obtener todos los roles del usuario
        user_roles = db.query(UsuarioFincaRol).filter(UsuarioFincaRol.usuario_id == user.id).all()
        
        # Verificar si se encontraron roles para el usuario
        if not user_roles:
            print(f"Usuario {user.id} no tiene roles asociados.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have any roles")

        print(f"Roles encontrados para el usuario {user.id}: {user_roles}")

        # Iterar sobre cada rol del usuario
        for user_role in user_roles:
            # Obtener todos los permisos asociados al rol
            role_permissions = db.query(RolPermiso).filter(RolPermiso.rol_id == user_role.rol_id).all()
            print(f"Permisos encontrados para el rol {user_role.rol_id}: {role_permissions}")
            
            # Verificar cada permiso asociado con el rol
            for role_permission in role_permissions:
                permission = db.query(Permission).filter(Permission.id == role_permission.permiso_id).first()
                # Si se encuentra el permiso requerido, permitir el acceso
                if permission and permission.nombre == permission_name:
                    print(f"Permiso '{permission_name}' encontrado para el usuario {user.id}")
                    return
        
        # Si después de iterar no se encontró el permiso, denegar el acceso
        print(f"Permiso '{permission_name}' no encontrado para el usuario {user.id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return verify

