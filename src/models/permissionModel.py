from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.database.database import Base

class Permission(Base):
    __tablename__ = 'permiso'  # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)  # La columna se llama 'nombre'
    descripcion = Column(String, nullable=True)

    # Relación inversa con Rol (a través de la tabla intermedia rol_permiso)
    roles = relationship("Rol", secondary="rol_permiso", back_populates="permissions")

class RolPermiso(Base):
    __tablename__ = 'rol_permiso'  # Nombre de la tabla en la base de datos
    
    rol_id = Column(Integer, ForeignKey('rol.id'), primary_key=True)
    permiso_id = Column(Integer, ForeignKey('permiso.id'), primary_key=True)