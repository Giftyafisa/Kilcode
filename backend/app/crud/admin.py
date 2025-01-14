from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminUpdate

def get_by_email(db: Session, email: str) -> Optional[Admin]:
    return db.query(Admin).filter(Admin.email == email).first()

def authenticate(db: Session, *, email: str, password: str) -> Optional[Admin]:
    admin = get_by_email(db, email=email)
    if not admin:
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    return admin

def create(db: Session, *, obj_in: AdminCreate) -> Admin:
    db_obj = Admin(
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        country=obj_in.country,
        role=obj_in.role,
        is_active=obj_in.is_active
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, *, db_obj: Admin, obj_in: AdminUpdate) -> Admin:
    if obj_in.password:
        db_obj.hashed_password = get_password_hash(obj_in.password)
    if obj_in.full_name:
        db_obj.full_name = obj_in.full_name
    if obj_in.country:
        db_obj.country = obj_in.country
    if obj_in.is_active is not None:
        db_obj.is_active = obj_in.is_active
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_multi(db: Session, *, skip: int = 0, limit: int = 100):
    return db.query(Admin).offset(skip).limit(limit).all()

def get(db: Session, id: int) -> Optional[Admin]:
    return db.query(Admin).filter(Admin.id == id).first() 