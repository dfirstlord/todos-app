import sys

sys.path.append("..")

from fastapi import Depends, APIRouter
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_current_user, get_user_execption, verify_password, get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "not found"}}
)


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


@router.get("/{id}")
async def get_user_by_id(id: int, db: Session = Depends(get_db)):
    selected = db.query(models.Users).filter(models.Users.id == id).first()
    if selected is not None:
        return selected
    return "Invalid user ID"


@router.put("/password")
async def change_password(user_verification: UserVerification, user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_execption()
    selected = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if selected is not None:
        if user_verification.username == selected.username and verify_password(user_verification.password,
                                                                               selected.hashed_password):
            selected.hashed_password = get_password_hash(user_verification.new_password)
            db.add(selected)
            db.commit()
            return "successful"
        return "invalid user or request"

@router.delete("/")
async def delete_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_execption()
    selected = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if selected is None:
        return "Invalid request or user"
    db.query(models.Users).filter(models.Users.id == user.get("id")).delete()
    db.commit()
    return "Delete successful"
